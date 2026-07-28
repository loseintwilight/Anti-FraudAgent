"""
对话引擎 — 核心业务编排层

功能说明（对应升级方案 Section 3.3.2）：
1. 接收用户输入 → 身份识别 → 反诈相关判断 → 知识库检索 → 风险评估
2. 双路召回：反诈问题优先检索知识库，非反诈问题走 DeepSeek 通用问答
3. 高风险场景：生成劝导话术 + 风险报告
4. 支持流式和非流式两种输出模式
"""

from typing import AsyncGenerator, Optional, Tuple, Union

from ..config import settings
from ..core.context import ConversationContext, context_manager
from ..core.deepseek import deepseek_client
from ..core.retriever import rag_retriever
from ..engine.identity import IdentityEngine, identity_engine
from ..engine.persuasion import persuasion_engine
from ..engine.risk import risk_assessor
from ..models.schemas import ChatRequest, ChatResponse, RiskLevel, UserRole
from ..utils.logger import logger


class DialogueEngine:
    """
    对话引擎 — 核心业务编排

    处理流程：
    1. 身份识别 → 更新用户画像
    2. 判断是否反诈相关
    3. 反诈相关 → 知识库检索 → 风险评估 → 劝导话术 → 组装回答
    4. 非反诈相关 → DeepSeek 通用问答
    5. 更新对话上下文
    """

    # 闲聊/问候语关键词（绕过知识库检索，直接走 DeepSeek）
    _CHAT_KEYWORDS = [
        "你好", "嗨", "hi", "hello", "在吗", "在不在",
        "天气", "今天", "最近", "心情", "emo",
        "颜色", "食物", "音乐", "电影", "游戏",
        "叫什么", "你是谁", "你叫什么",
    ]

    # 系统提示词（反诈助手角色设定）
    _SYSTEM_PROMPT = (
        "你是一个专业的反诈骗助手，名叫「反诈卫士」。你的职责是帮助用户识别和防范各类诈骗。\n\n"
        "【回答规则】\n"
        "1. 如果用户问好或闲聊，请用温暖亲切的语气回应，不要提及诈骗话题\n"
        "2. 如果用户询问反诈知识，请用通俗易懂的语言解释\n"
        "3. 如果用户描述自己遇到的疑似诈骗情况，请先共情安抚，再给出专业建议\n"
        "4. 回答要口语化、接地气，避免生硬的法律条文\n"
        "5. 高风险情况要明确指出并提供行动建议\n"
        "6. 重要提醒：涉及转账、验证码、银行卡等敏感信息时，务必提醒用户注意安全\n\n"
        "【知识库说明】\n"
        "当用户问题涉及反诈领域时，系统会优先检索本地知识库。"
        "如果回答中注明「该内容来自通用模型，仅供参考」，说明该回答来自大模型自身知识。"
    )

    # 知识库检索结果的系统提示词
    _KB_SYSTEM_PROMPT = (
        "你是一个专业的反诈骗助手，名叫「反诈卫士」。\n\n"
        "下面是从反诈知识库中检索到的相关内容，请基于这些内容回答用户的问题。\n"
        "要求：\n"
        "1. 不要直接照搬原文，用口语化的语言重新组织\n"
        "2. 根据用户的年龄和身份调整语气\n"
        "3. 回答要简洁、清晰、有针对性\n"
        "4. 如果用户已经处于高风险中，要给出紧急行动建议\n"
        "检索到的知识库内容如下：\n"
    )

    def __init__(self):
        self.identity_engine = identity_engine
        logger.info("对话引擎初始化完成")

    async def process(
        self,
        request: ChatRequest,
    ) -> Union[ChatResponse, AsyncGenerator[str, None]]:
        """
        处理对话请求（主入口）

        Args:
            request: 对话请求

        Returns:
            非流式: ChatResponse
            流式: 文本生成器
        """
        # 获取或创建会话上下文
        ctx = context_manager.get_or_create(request.session_id, request.user_id)

        # 添加用户消息到上下文
        ctx.add_message("user", request.message)

        # 1. 身份识别
        self._identify_user(ctx, request.message)

        # 2. 判断是否闲聊/问候
        if self._is_chat_query(request.message):
            logger.info(f"闲聊模式: session_id={request.session_id}")
            return await self._handle_chat(ctx, request)

        # 3. 判断是否反诈相关
        is_fraud = rag_retriever.is_fraud_related(request.message)

        if is_fraud:
            # 反诈模式：知识库优先 + 风险评估 + 劝导话术
            return await self._handle_fraud_query(ctx, request)
        else:
            # 非反诈模式：走 DeepSeek 通用问答
            logger.info(f"通用问答模式: session_id={request.session_id}")
            return await self._handle_general_query(ctx, request)

    def _identify_user(self, ctx: ConversationContext, query: str):
        """
        识别用户身份并更新画像

        Args:
            ctx: 会话上下文
            query: 用户输入
        """
        role = self.identity_engine.identify(
            user_id=ctx.user_id,
            query=query,
            history=ctx.user_profile.query_history,
        )
        if role != UserRole.UNKNOWN:
            self.identity_engine.update_profile_from_role(ctx.user_profile, role)

    def _is_chat_query(self, query: str) -> bool:
        """判断是否为闲聊/问候"""
        query_lower = query.lower().strip()
        for kw in self._CHAT_KEYWORDS:
            if kw in query_lower:
                return True
        return False

    async def _handle_chat(
        self,
        ctx: ConversationContext,
        request: ChatRequest,
    ) -> Union[ChatResponse, AsyncGenerator[str, None]]:
        """处理闲聊模式"""
        messages = ctx.get_recent_messages()

        if request.stream:
            return self._stream_wrap(
                deepseek_client.chat(
                    messages=messages,
                    system_prompt=self._SYSTEM_PROMPT,
                    stream=True,
                ),
                ctx=ctx,
                request=request,
            )
        else:
            reply = await deepseek_client.chat(
                messages=messages,
                system_prompt=self._SYSTEM_PROMPT,
                stream=False,
            )
            ctx.add_message("assistant", reply)
            context_manager.persist(ctx.session_id)
            return ChatResponse(
                session_id=request.session_id,
                reply=reply,
                role_detected=ctx.user_profile.role,
            )

    async def _handle_fraud_query(
        self,
        ctx: ConversationContext,
        request: ChatRequest,
    ) -> Union[ChatResponse, AsyncGenerator[str, None]]:
        """处理反诈相关查询"""
        user_role = ctx.user_profile.role.value if ctx.user_profile.role != UserRole.UNKNOWN else "unknown"

        # 1. 知识库检索
        kb_content, kb_score, from_kb = rag_retriever.retrieve(
            request.message, user_role=user_role
        )

        # 2. 风险评估
        risk_level, fraud_type, confidence, risk_items = risk_assessor.assess(
            request.message, user_role=user_role
        )
        ctx.add_risk_record(fraud_type, risk_level, confidence)

        # 3. 劝导话术
        persuasion_message = persuasion_engine.generate(
            fraud_type=fraud_type,
            risk_level=risk_level.value,
            user_role=user_role,
        )

        # 4. 构建系统提示词
        if from_kb and kb_content:
            # 知识库命中，构建带知识库内容的系统提示
            system_prompt = (
                self._KB_SYSTEM_PROMPT
                + f"\n---\n{kb_content}\n---\n"
                + f"用户角色：{user_role}\n"
                + f"风险等级：{risk_level.value}\n"
                + f"诈骗类型：{fraud_type}\n"
            )
            if persuasion_message:
                system_prompt += f"\n请在回答的最后附上以下劝导内容：\n{persuasion_message}"
        else:
            # 知识库未命中或置信度不足，降级到大模型
            system_prompt = self._SYSTEM_PROMPT
            if not from_kb:
                system_prompt += (
                    "\n\n注意：当前回答来自通用模型，未检索到专用知识库，"
                    "请在回答末尾注明「该内容来自通用模型，仅供参考」。"
                )

        # 5. 获取对话历史并调用 DeepSeek
        messages = ctx.get_recent_messages()

        if request.stream:
            return self._stream_wrap(
                deepseek_client.chat(
                    messages=messages,
                    system_prompt=system_prompt,
                    stream=True,
                ),
                ctx=ctx,
                request=request,
                risk_level=risk_level,
                fraud_type=fraud_type,
                persuasion_message=persuasion_message,
                from_kb=from_kb,
            )
        else:
            reply = await deepseek_client.chat(
                messages=messages,
                system_prompt=system_prompt,
                stream=False,
            )
            ctx.add_message("assistant", reply)
            context_manager.persist(ctx.session_id)
            return ChatResponse(
                session_id=request.session_id,
                reply=reply,
                risk_level=risk_level,
                fraud_type=fraud_type,
                persuasion_message=persuasion_message,
                role_detected=ctx.user_profile.role,
                from_knowledge_base=from_kb,
            )

    async def _handle_general_query(
        self,
        ctx: ConversationContext,
        request: ChatRequest,
    ) -> Union[ChatResponse, AsyncGenerator[str, None]]:
        """处理通用问答（非反诈相关）"""
        messages = ctx.get_recent_messages()

        if request.stream:
            return self._stream_wrap(
                deepseek_client.chat(
                    messages=messages,
                    system_prompt=self._SYSTEM_PROMPT,
                    stream=True,
                ),
                ctx=ctx,
                request=request,
            )
        else:
            reply = await deepseek_client.chat(
                messages=messages,
                system_prompt=self._SYSTEM_PROMPT,
                stream=False,
            )
            ctx.add_message("assistant", reply)
            context_manager.persist(ctx.session_id)
            return ChatResponse(
                session_id=request.session_id,
                reply=reply,
                role_detected=ctx.user_profile.role,
            )

    async def _stream_wrap(
        self,
        stream_gen: AsyncGenerator[str, None],
        ctx: ConversationContext,
        request: ChatRequest,
        risk_level: Optional[RiskLevel] = None,
        fraud_type: Optional[str] = None,
        persuasion_message: Optional[str] = None,
        from_kb: bool = False,
    ) -> AsyncGenerator[str, None]:
        """
        包装流式输出，在流结束后保存上下文

        Args:
            stream_gen: 流式生成器
            ctx: 会话上下文
            request: 原始请求
            risk_level: 风险等级
            fraud_type: 诈骗类型
            persuasion_message: 劝导话术
            from_kb: 是否来自知识库
        """
        collected = []
        try:
            async for chunk in stream_gen:
                collected.append(chunk)
                yield chunk
        finally:
            full_reply = "".join(collected)
            ctx.add_message("assistant", full_reply)
            context_manager.persist(ctx.session_id)
            logger.info(
                f"流式对话完成: session_id={request.session_id}, "
                f"reply_length={len(full_reply)}, "
                f"risk_level={risk_level.value if risk_level else 'none'}"
            )


# 全局单例
dialogue_engine = DialogueEngine()