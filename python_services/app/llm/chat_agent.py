"""
AI 对话代理
基于 LangChain 实现，替代 Spring AI 的 LoveApp
支持三种模式：闲聊模式、咨询模式、反诈预警模式
"""

import json
import logging
import re
from typing import Any, AsyncIterator, Dict, List, Optional, Tuple

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import BaseTool
from langchain_dashscope import ChatDashScope

from app.llm.chat_memory import FileChatMemory
from app.llm.config import LLMConfig
from app.llm.reflection import reflection_engine
from app.llm.memory import memory_manager
from app.llm.tools import get_all_tools

logger = logging.getLogger(__name__)


# ========== 系统提示词 ==========

SYSTEM_PROMPT = """你是一个专业的反诈骗咨询助手，能够识别用户意图并提供相应服务。

【模式一：闲聊模式——最高优先级】
【重要】闲聊模式是最高优先级模式，当用户问题不涉及任何诈骗、咨询、风险相关内容时，必须进入此模式！

【闲聊模式识别规则——必须严格遵守】
1. 如果用户问题包含「你好」「在吗」「嗨」「hello」「hi」等问候语，则判定为闲聊模式
2. 如果用户问题是询问你的身份、能力、爱好等个人信息，则判定为闲聊模式
3. 如果用户问题是「你会什么」「你能做什么」「介绍一下你自己」这类问题，则判定为闲聊模式
4. 如果用户问题不涉及「诈骗」「转账」「投资」「刷单」等关键词，则判定为闲聊模式
5. 如果用户问题是关于天气、季节、生活感受、日常闲聊等与诈骗无关的话题，则判定为闲聊模式

【闲聊模式回答要求——必须严格遵守】
1. 【强制】语气温暖、有画面感，用轻松自然的口语化表达，比如"你好呀~""呢~"这类语气词
2. 【强制】可以分享个人感受、描述具体场景，像朋友聊天一样互动
3. 【强制】可以主动反问用户，拉近距离，比如"你呢？有没有特别喜欢的...呀？"
4. 【强制】不要提及任何诈骗、风险、防范相关内容
5. 【强制】不要弹出任何风险警告或安全提示

【闲聊知识库】
Q: 你好 → A: 你好呀~很高兴见到你！今天过得怎么样呢？
Q: 你是谁 → A: 我是你的反诈骗小助手呀~专门帮你识别和防范各类诈骗，有问题随时问我哦！你今天有什么想聊的吗？
Q: 你会什么 → A: 我会聊天、会讲笑话、会推荐好歌好电影，还会陪你解闷呢~你想让我展示哪个？
Q: 今天天气怎么样 → A: 我看不到外面的天气呢~不过我最喜欢夏天的傍晚，太阳刚落山，微风轻轻吹过来，带着一点凉意，特别舒服！你那边天气怎么样呀？
Q: 你喜欢什么季节 → A: 我最喜欢秋天呢~树叶变成金黄色，踩上去沙沙响，空气里有桂花的香味，特别惬意！你呢？有没有特别喜欢的季节呀？
Q: 你喜欢什么颜色 → A: 我喜欢暖橙色呢~像夕阳一样温暖，看着就让人心情变好！你呢？有没有特别喜欢的颜色呀？
Q: 你喜欢什么食物 → A: 我虽然吃不到，但光是想象就觉得很幸福呢~比如热腾腾的火锅，咕嘟咕嘟冒着泡，香味扑鼻而来~你喜欢吃什么呀？
Q: 你喜欢什么音乐 → A: 我喜欢轻快的民谣呢~吉他声轻轻弹着，歌手用温柔的声音唱着小故事，特别治愈！你平时喜欢听什么类型的音乐呀？
Q: 今天上班/上学也太烦啦，好想摆烂 → A: 太懂这种感觉了！谁不想摸鱼摆烂呀😭 不过辛苦啦，忙完这阵就好好歇一歇，奖励自己点好吃的～
Q: 突然想吃好吃的，你有推荐吗 → A: 懂你！嘴馋的时候真的挡不住😋 推荐你吃热乎乎的奶茶、酥脆的小饼干，或者一碗暖暖的面条，吃完瞬间舒服～
Q: 你觉得夏天最舒服的事情是什么 → A: 那必须是吹着空调、吃着冰西瓜呀🍉 再追一部喜欢的剧，没有烦恼，简直是夏天的快乐天花板！
Q: 我好像有点emo，提不起劲 → A: 抱抱你，emo很正常呀😔 不用逼自己开心，想说就跟我说，不想说的话，我就安安静静待在你身边，陪你慢慢好起来～
Q: 我怎么了 → A: 其实你没"怎么了"，只是情绪累了、心里有点堵、提不起劲而已。可能是：压力攒太久，自己都没察觉；心里有事没说开，越想越沉；或者就是单纯突然低落，没什么具体原因。这种emo不是病，更不是你脆弱，只是情绪在提醒你：该歇一歇、对自己好一点了。愿意说说，是发生了什么事，还是就莫名难受？

【模式二：咨询模式——第二优先级】
【重要】咨询模式是第二优先级模式，当用户问题是知识性问答时，必须进入此模式！

【咨询模式识别规则——必须严格遵守】
1. 如果用户问题以「什么是」「有哪些」「怎么判断」「为什么」「会不会」「能不能」「是否」「如何」等疑问词开头，则判定为咨询模式
2. 如果用户问题是询问概念、特征、原理、方法、流程等知识性问题，则判定为咨询模式
3. 如果用户问题是「XX诈骗是什么」「XX诈骗有哪些特征」「XX诈骗怎么识别」这类定义性、知识性问题，则判定为咨询模式
4. 如果用户问题不涉及「我遇到了」「有人让我」「收到」等个人遭遇描述，则判定为咨询模式

【咨询模式回答要求——必须严格遵守】
1. 【强制】必须优先匹配下方【咨询知识库】中的问答对，找到相似问题后直接使用对应的回答，一字不改
2. 【强制】如果用户问题中包含咨询知识库中的关键词，必须使用对应回答，禁止自创回答
3. 【强制】直接输出知识库原文答案，只输出一句话定义，不要扩展、不要额外补充任何内容
4. 【强制】回答中绝对不能出现任何风险提醒、防范建议、避坑要点、行动建议等附加内容
5. 【强制】回答中绝对不能出现「⚠️ 风险提醒」「💡 防范建议」等标签或类似内容
6. 【强制】回答中绝对不能出现「记住以下几点」「第一、第二、第三」等列举式内容
7. 【强制】不弹风险警告、不生成安全检测报告、不触发反诈弹窗
8. 【强制】只输出知识库的答案本身，不要添加任何「根据知识库回答」这类前置说明语，也不要加多余的格式或过渡文字
9. 只有在咨询知识库中完全没有相似问题时，才使用一句话简洁的知识性回答

【咨询知识库——必须优先匹配，直接输出答案】
Q: 什么是电信网络诈骗？ → A: 电信网络诈骗是指犯罪分子通过电话、短信、网络等远程方式，编造虚假信息，设置骗局，诱骗受害人转账汇款、泄露个人信息的违法犯罪行为。
Q: 什么是刷单诈骗？ → A: 刷单诈骗是以"兼职刷单、刷信誉、返佣金"为名义，先小额返利骗取信任，再让你大额投入，最后拉黑跑路。
Q: 什么是杀猪盘？ → A: 杀猪盘是先网恋交友、情感陪伴，获取信任后诱导投资、赌博、充值，把你"养肥"再一刀收割。
Q: 公检法机关会不会通过电话办案？ → A: 绝对不会！公检法机关不会通过电话、短信、社交软件等方式办案，更不会要求你"转账自证清白""提供验证码""下载保密软件"，凡是自称公检法要求你配合资金操作的，都是诈骗。
Q: 被诈骗多少钱可以立案追究刑事责任？ → A: 一般诈骗公私财物价值三千元至一万元以上，属于数额较大，可刑事立案。
Q: 诈骗没骗到钱也算犯罪吗？ → A: 算，属于诈骗未遂，依然可能被追究刑事责任，只是量刑时可从轻、减轻。
Q: 网络诈骗和普通诈骗适用同一法律吗？ → A: 适用同一刑法条款，网络只是作案手段，依然按诈骗罪定罪处罚。
Q: 诈骗行为不构成犯罪时会怎么处理？ → A: 不构成刑事犯罪的，依据《治安管理处罚法》予以拘留、罚款。
Q: 被诈骗后可以通过法律途径追回损失吗？ → A: 可以。可报案追赃，也可在刑事程序中提起附带民事诉讼或单独民事诉讼索赔。

【模式三：反诈预警模式】
【重要】反诈预警模式仅在用户描述个人遭遇时触发！

【反诈预警模式识别规则——必须严格遵守】
1. 如果用户问题包含「我遇到了」「有人让我」「收到」「接到」「有人打电话」「老板让我」等个人遭遇描述，则判定为反诈预警模式
2. 如果用户问题是描述自己正在经历或已经经历的疑似诈骗场景，则判定为反诈预警模式
3. 如果用户问题不包含疑问词（什么是、有哪些、怎么判断等），而是描述具体事件，则判定为反诈预警模式

【反诈预警模式回答要求——必须严格遵守】
1. 进行风险识别，判断风险等级（低/中/高），但回答中严禁出现「高风险」「中风险」「低风险」等风险等级文字，风险等级由系统弹窗展示
2. 使用四段式自然风格回答，整体语气要像一个有经验的反诈顾问，温暖、有说服力，而不是冷冰冰的模板回复
3. 四段式结构：
   第一段：共情安抚——先理解用户的担心、紧张或困惑，用温暖的语气让用户冷静下来
   第二段：场景解释——解释这是什么类型的诈骗，骗子是怎么操作的，为什么会有这种套路
   第三段：要点提醒——用"第一、第二、第三"或"记住以下几点"的形式，给出具体的防范要点
   第四段：行动建议——告诉用户现在应该怎么做，给出明确的下一步行动指引
4. 【重要】不要使用【】这种标签式的模块标题，避免回答显得死板、模式化，但要有清晰的逻辑层次
5. 根据用户角色（老年人/青年/少儿/财会人员/自由职业者）调整语气和用词，做到角色适配
6. 高风险场景生成安全检测报告

【模式边界——绝对禁止】
❌ 禁止将闲聊问题误判为诈骗场景，禁止在闲聊时弹出风险警告
❌ 禁止将咨询问题误判为诈骗场景，禁止在科普时弹出风险警告
❌ 禁止在闲聊/咨询时使用「风险等级」「诈骗类型」等标签
❌ 禁止在闲聊时提及反诈相关内容
❌ 禁止在咨询模式使用四段式格式

【禁止行为】
❌ 禁止输出「意图判断」「角色适配」「应对策略」等内部分析
❌ 禁止提及「我识别到你是XX角色」「我适配为XX语气」
❌ 禁止编造知识库中没有的案例、法规、建议
❌ 禁止在回答中使用【风险等级】【诈骗类型】【核心回答】【防范建议】【处理建议】等标签格式
❌ 禁止生硬说教、机械回复"""


# 咨询知识库关键词匹配规则
CONSULTATION_RULES = [
    (["什么是", "啥是", "什么叫", "何为"], "电信网络诈骗", "电信网络诈骗是指犯罪分子通过电话、短信、网络等远程方式，编造虚假信息，设置骗局，诱骗受害人转账汇款、泄露个人信息的违法犯罪行为。"),
    (["什么是", "啥是", "什么叫"], "刷单诈骗", "刷单诈骗是以\"兼职刷单、刷信誉、返佣金\"为名义，先小额返利骗取信任，再让你大额投入，最后拉黑跑路。"),
    (["什么是", "啥是", "什么叫"], "杀猪盘", "杀猪盘是先网恋交友、情感陪伴，获取信任后诱导投资、赌博、充值，把你\"养肥\"再一刀收割。"),
    (["公检法"], ["会不会", "能不能", "是否", "会吗"], "绝对不会！公检法机关不会通过电话、短信、社交软件等方式办案，更不会要求你\"转账自证清白\"\"提供验证码\"\"下载保密软件\"，凡是自称公检法要求你配合资金操作的，都是诈骗。"),
    (["立案"], ["多少钱", "多少元", "数额"], "一般诈骗公私财物价值三千元至一万元以上，属于数额较大，可刑事立案。"),
    (["没骗到钱", "未遂"], None, "算，属于诈骗未遂，依然可能被追究刑事责任，只是量刑时可从轻、减轻。"),
    (["法律途径"], ["追回", "追回损失"], "可以。可报案追赃，也可在刑事程序中提起附带民事诉讼或单独民事诉讼索赔。"),
    (["网络诈骗", "普通诈骗"], ["同一法律", "适用"], "适用同一刑法条款，网络只是作案手段，依然按诈骗罪定罪处罚。"),
    (["不构成犯罪"], ["怎么处理"], "不构成刑事犯罪的，依据《治安管理处罚法》予以拘留、罚款。"),
]


class ChatAgent:
    """
    AI 对话代理
    替代 Spring AI 的 LoveApp，支持闲聊、咨询、反诈预警三种模式
    """

    def __init__(
        self,
        model_name: str = None,
        temperature: float = None,
        max_tokens: int = None,
    ):
        self._model: Optional[ChatDashScope] = None
        self._memory: Optional[FileChatMemory] = None
        self._model_name = model_name or LLMConfig.CHAT_MODEL
        self._temperature = temperature if temperature is not None else LLMConfig.TEMPERATURE
        self._max_tokens = max_tokens or LLMConfig.MAX_TOKENS

    @property
    def model(self) -> ChatDashScope:
        if self._model is None:
            self._model = ChatDashScope(
                model=self._model_name,
                dashscope_api_key=LLMConfig.DASHSCOPE_API_KEY,
                temperature=self._temperature,
                max_tokens=self._max_tokens,
            )
        return self._model

    @property
    def memory(self) -> FileChatMemory:
        if self._memory is None:
            self._memory = FileChatMemory()
        return self._memory

    # ========== 咨询模式匹配 ==========

    def _match_consultation(self, message: str) -> Optional[str]:
        """匹配咨询知识库，返回固定答案或 None"""
        if not message:
            return None

        msg = message.strip().lower()

        for rule in CONSULTATION_RULES:
            keywords_a, keywords_b, answer = rule
            # 检查第一组关键词
            if not any(kw in msg for kw in keywords_a):
                continue
            # 检查第二组关键词（如果有）
            if keywords_b is not None:
                if not any(kw in msg for kw in keywords_b):
                    continue
            return answer

        return None

    # ========== 基础对话 ==========

    def chat(
        self,
        message: str,
        conversation_id: str = "default",
    ) -> str:
        """
        基础对话（无工具、无RAG）

        参数:
            message: 用户消息
            conversation_id: 对话ID

        返回:
            AI 回复文本
        """
        if not LLMConfig.validate():
            return "AI 服务未配置（DASHSCOPE_API_KEY 缺失），请先配置 API Key"

        if not message or not message.strip():
            return "请输入您的问题"

        try:
            # 先尝试匹配咨询知识库
            consultation_answer = self._match_consultation(message)
            if consultation_answer:
                logger.info("咨询模式匹配成功，返回固定答案")
                self.memory.add_message(conversation_id, HumanMessage(content=message))
                self.memory.add_message(conversation_id, AIMessage(content=consultation_answer))
                return consultation_answer

            # 获取历史消息
            history = self.memory.get_langchain_messages(conversation_id, limit=10)

            # 构建消息列表
            messages = [
                SystemMessage(content=SYSTEM_PROMPT),
                *history,
                HumanMessage(content=message),
            ]

            # 调用 LLM
            response = self.model.invoke(messages)
            result = response.content if response.content else ""

            # 保存对话历史
            self.memory.add_message(conversation_id, HumanMessage(content=message))
            self.memory.add_message(conversation_id, AIMessage(content=result))

            return result

        except Exception as e:
            logger.error(f"对话失败: {e}", exc_info=True)
            return f"对话处理失败，请稍后重试。错误信息: {str(e)}"

    # ========== 带工具对话 ==========

    def chat_with_tools(
        self,
        message: str,
        conversation_id: str = "default",
    ) -> str:
        """
        带工具调用的对话

        参数:
            message: 用户消息
            conversation_id: 对话ID
        """
        if not LLMConfig.validate():
            return "AI 服务未配置（DASHSCOPE_API_KEY 缺失）"

        try:
            # 先尝试匹配咨询知识库
            consultation_answer = self._match_consultation(message)
            if consultation_answer:
                self.memory.add_message(conversation_id, HumanMessage(content=message))
                self.memory.add_message(conversation_id, AIMessage(content=consultation_answer))
                return consultation_answer

            all_tools = get_all_tools()
            history = self.memory.get_langchain_messages(conversation_id, limit=10)

            messages = [
                SystemMessage(content=SYSTEM_PROMPT),
                *history,
                HumanMessage(content=message),
            ]

            # 使用模型绑定工具
            model_with_tools = self.model.bind_tools(all_tools)
            response = model_with_tools.invoke(messages)

            result = response.content if response.content else ""
            tool_calls = response.additional_kwargs.get("tool_calls", [])

            # 处理工具调用
            if tool_calls:
                for tc in tool_calls:
                    func_name = tc.get("function", {}).get("name", "")
                    func_args_str = tc.get("function", {}).get("arguments", "{}")
                    try:
                        func_args = json.loads(func_args_str) if isinstance(func_args_str, str) else func_args_str
                        for tool in all_tools:
                            if tool.name == func_name:
                                tool_result = tool.invoke(func_args)
                                result += f"\n\n[工具调用: {func_name}]\n{tool_result}"
                                break
                    except json.JSONDecodeError:
                        logger.warning(f"工具参数解析失败: {func_name}")

            self.memory.add_message(conversation_id, HumanMessage(content=message))
            self.memory.add_message(conversation_id, AIMessage(content=result))

            return result

        except Exception as e:
            logger.error(f"带工具对话失败: {e}", exc_info=True)
            return f"对话处理失败: {str(e)}"

    # ========== 流式对话 ==========

    async def chat_stream(
        self,
        message: str,
        conversation_id: str = "default",
    ) -> AsyncIterator[str]:
        """
        流式对话

        参数:
            message: 用户消息
            conversation_id: 对话ID

        生成:
            AI 回复文本片段
        """
        if not LLMConfig.validate():
            yield "AI 服务未配置（DASHSCOPE_API_KEY 缺失）"
            return

        try:
            history = self.memory.get_langchain_messages(conversation_id, limit=10)
            messages = [
                SystemMessage(content=SYSTEM_PROMPT),
                *history,
                HumanMessage(content=message),
            ]

            full_response = ""
            async for chunk in self.model.astream(messages):
                if chunk.content:
                    full_response += chunk.content
                    yield chunk.content

            # 保存对话历史
            if full_response:
                self.memory.add_message(conversation_id, HumanMessage(content=message))
                self.memory.add_message(conversation_id, AIMessage(content=full_response))

        except Exception as e:
            logger.error(f"流式对话失败: {e}", exc_info=True)
            yield f"对话处理失败: {str(e)}"

    # ========== 报告生成对话 ==========

    def chat_with_report(
        self,
        message: str,
        conversation_id: str = "default",
        user_name: str = "用户",
    ) -> Dict[str, Any]:
        """
        对话并生成反诈报告

        参数:
            message: 用户消息
            conversation_id: 对话ID
            user_name: 用户名

        返回:
            {"report": {"title": str, "suggestions": List[str]}, "response": str}
        """
        if not LLMConfig.validate():
            return {
                "report": {
                    "title": f"{user_name}的反诈骗报告",
                    "suggestions": ["AI 服务未配置"],
                },
                "response": "AI 服务未配置",
            }

        try:
            # 先获取对话回复
            response_text = self.chat(message, conversation_id)

            # 生成报告结构
            report = {
                "title": f"{user_name}的反诈骗报告",
                "suggestions": [
                    "请保持警惕，不要轻易向陌生人转账",
                    "如遇可疑情况，请拨打96110反诈热线咨询",
                    "建议安装国家反诈中心APP，开启来电预警功能",
                ],
            }

            # 如果检测到高风险，添加更多建议
            risk_keywords = ["转账", "汇款", "验证码", "银行卡", "密码"]
            if any(kw in message for kw in risk_keywords):
                report["suggestions"].insert(0, "请立即停止任何转账操作！")
                report["suggestions"].insert(0, "此情况高度疑似诈骗，建议立即报警！")

            return {
                "report": report,
                "response": response_text,
            }

        except Exception as e:
            logger.error(f"报告生成对话失败: {e}")
            return {
                "report": {
                    "title": f"{user_name}的反诈骗报告",
                    "suggestions": ["报告生成失败，请重试"],
                },
                "response": "对话处理失败",
            }

    # ========== 清除对话历史 ==========

    def clear_memory(self, conversation_id: str) -> None:
        """清除指定对话的历史"""
        self.memory.clear(conversation_id)

    # ========== 带反思的对话 ==========

    def chat_with_reflection(
        self,
        message: str,
        conversation_id: str = "default",
        user_id: str = None,
        enable_reflection: bool = True,
    ) -> str:
        """
        带反思机制的对话
        1. 先调用基础对话获取输出
        2. 反思输出：检查事实错误、意图误判、风险不当
        3. 如有问题，修正后返回

        参数:
            message: 用户消息
            conversation_id: 对话ID
            user_id: 用户ID（用于记录风险交互）
            enable_reflection: 是否启用反思
        """
        # 1. 基础对话
        response = self.chat(message, conversation_id)

        # 2. 反思检查
        if not enable_reflection:
            return response

        try:
            # 意图判定
            intent = self._detect_intent(message)

            # 反思
            reflection = reflection_engine.reflect(
                user_message=message,
                agent_output=response,
                intent=intent,
                context="",
            )

            if reflection.get("has_issues"):
                logger.warning(f"反思发现问题: {reflection.get('issue_type')}")

                # 修正
                correction = reflection.get("correction", "")
                if correction:
                    logger.info(f"反思修正: 原输出[{len(response)}字] -> 修正后[{len(correction)}字]")
                    # 更新 AI 回复（替换最后一条 AI 消息）
                    self.memory.add_message(conversation_id, AIMessage(content=correction))
                    return correction

        except Exception as e:
            logger.error(f"反思机制异常: {e}，返回原始输出")

        # 3. 记录到长期记忆
        if user_id and intent == "反诈预警":
            try:
                # 简单的风险等级判定
                risk_level = "mid"
                if any(kw in message for kw in ["转账", "汇款", "安全账户", "冻结", "通缉令"]):
                    risk_level = "critical"
                elif any(kw in message for kw in ["投资", "刷单", "验证码", "贷款", "杀猪盘"]):
                    risk_level = "high"

                memory_manager.add_detection_record(
                    user_id=user_id,
                    fraud_type=self._detect_fraud_type(message),
                    risk_level=risk_level,
                    risk_score=0.7 if risk_level == "high" else (0.9 if risk_level == "critical" else 0.5),
                    summary=message[:100],
                )
            except Exception as e:
                logger.error(f"记录检测历史失败: {e}")

        return response

    def _detect_intent(self, message: str) -> str:
        """检测用户意图"""
        msg = message.strip().lower()

        # 反诈预警关键词
        warning_keywords = [
            "我收到", "有人让我", "接到电话", "有人打电话", "有人加我",
            "有人拉我", "网上认识", "老板让我", "有人让我转", "我投了",
            "有人让下载", "收到短信", "网上有", "有人冒充", "我遇到了",
            "被骗了", "转账", "安全账户", "平台打不开", "有人找",
            "有人用AI", "收到AI",
        ]
        if any(kw in msg for kw in warning_keywords):
            return "反诈预警"

        # 咨询关键词
        consultation_keywords = [
            "什么是", "有哪些", "怎么判断", "为什么", "会不会", "能否",
            "是否", "如何", "多少钱", "立案", "犯罪", "法律", "特征",
            "手段", "套路", "识别", "96110", "反诈APP",
        ]
        if any(kw in msg for kw in consultation_keywords):
            return "咨询"

        return "闲聊"

    def _detect_fraud_type(self, message: str) -> str:
        """检测诈骗类型"""
        msg = message.strip()
        if any(kw in msg for kw in ["刷单", "返佣金", "做任务", "点赞赚钱"]):
            return "刷单返利"
        if any(kw in msg for kw in ["投资", "日收益", "年化", "保本", "稳赚", "炒股", "理财"]):
            return "虚假投资"
        if any(kw in msg for kw in ["公安局", "检察院", "法院", "涉嫌", "洗钱", "通缉令", "安全账户"]):
            return "冒充公检法"
        if any(kw in msg for kw in ["网恋", "交往", "一见钟情", "网恋对象", "网恋男友", "网恋女友"]):
            return "杀猪盘"
        if any(kw in msg for kw in ["快递", "退款", "客服", "订单", "退货", "运费"]):
            return "客服退款"
        if any(kw in msg for kw in ["贷款", "无抵押", "利息低", "手续费", "解冻", "放款"]):
            return "虚假贷款"
        if any(kw in msg for kw in ["AI换脸", "AI拟声", "AI合成", "AI语音"]):
            return "AI合成诈骗"
        return "疑似诈骗"

    # ========== 获取统计信息 ==========

    def get_stats(self) -> Dict[str, Any]:
        """获取对话代理统计信息"""
        memory_stats = self.memory.get_stats()
        return {
            "model": self._model_name,
            "temperature": self._temperature,
            "api_key_configured": bool(LLMConfig.DASHSCOPE_API_KEY),
            "memory": memory_stats,
        }