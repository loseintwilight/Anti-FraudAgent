"""
RAG 检索增强生成模块
基于 Qdrant + 混合检索（BM25 + 向量 → RRF → 可选精排）实现知识检索增强的对话。
"""
import logging
from typing import Any, Dict, List, Optional

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_dashscope import ChatDashScope

from app.llm.config import LLMConfig
from app.llm.chat_memory import FileChatMemory
from app.vector_store.embedder import TextEmbedder
from app.vector_store.hybrid import (
    HybridRetriever,
    collection_count,
    upsert_documents,
)

logger = logging.getLogger(__name__)

# 默认集合名称
DEFAULT_COLLECTION = LLMConfig.QDRANT_COLLECTION

# 查询重写提示词
QUERY_REWRITE_PROMPT = """你是一个专业的反诈查询重写助手。请根据用户的问题和对话历史，重写查询以使其更适合检索。

原始问题：{question}

要求：
1. 提取核心关键词
2. 补充相关的反诈术语
3. 保持简洁，不超过50字
4. 如果问题本身已经很清晰，直接返回原问题

重写后的查询："""


class RAGAgent:
    """
    RAG 检索增强生成代理
    基于 Qdrant + 混合检索实现知识检索增强的对话
    """

    def __init__(self):
        self._chat_model: Optional[ChatDashScope] = None
        self._embedding_model: Optional[TextEmbedder] = None
        self._retriever: Optional[HybridRetriever] = None
        self._memory: Optional[FileChatMemory] = None

    @property
    def chat_model(self) -> ChatDashScope:
        if self._chat_model is None:
            self._chat_model = ChatDashScope(
                model=LLMConfig.CHAT_MODEL,
                dashscope_api_key=LLMConfig.DASHSCOPE_API_KEY,
                temperature=LLMConfig.TEMPERATURE,
                max_tokens=LLMConfig.MAX_TOKENS,
            )
        return self._chat_model

    @property
    def embedding_model(self) -> TextEmbedder:
        """本地嵌入器（入库与查询共用，保证向量维度一致）"""
        if self._embedding_model is None:
            self._embedding_model = TextEmbedder()
        return self._embedding_model

    @property
    def retriever(self) -> HybridRetriever:
        if self._retriever is None:
            self._retriever = HybridRetriever()
        return self._retriever

    @property
    def vector_store(self):
        """兼容旧接口：返回混合检索器（Qdrant 客户端由 hybrid 单例持有）"""
        return self.retriever

    @property
    def memory(self) -> FileChatMemory:
        if self._memory is None:
            self._memory = FileChatMemory()
        return self._memory

    def rewrite_query(self, question: str, history=None) -> str:
        """结合对话历史重写查询以提高检索效果"""
        if not LLMConfig.validate():
            return question

        try:
            history_text = ""
            if history:
                history_text = "\n".join(
                    str(getattr(m, "content", m)) for m in history[-4:]
                )
            prompt_text = QUERY_REWRITE_PROMPT.replace("{question}", question)
            if history_text:
                prompt_text = f"对话历史：\n{history_text}\n\n{prompt_text}"

            # 直接发消息，避免把用户问题里的花括号当成模板变量解析
            response = self.chat_model.invoke(
                [HumanMessage(content=prompt_text)]
            )
            rewritten = response.content.strip() if response.content else question
            logger.info("查询重写: %s -> %s", question[:30], rewritten[:30])
            return rewritten
        except Exception as e:
            logger.warning("查询重写失败: %s，使用原始查询", e)
            return question

    def add_documents(self, documents: List[Dict[str, Any]], safe_mode: bool = True) -> int:
        """添加文档到向量存储（支持安全模式：备份+回归测试+自动回滚）"""
        if not documents:
            return 0

        try:
            # 安全模式：更新前备份
            backup_path = ""
            before_recall = 0.0
            if safe_mode:
                try:
                    from evaluation.kb_version_manager import KnowledgeBaseManager

                    kb_mgr = KnowledgeBaseManager()
                    before_recall = kb_mgr.run_regression_test()["avg_recall"]
                    backup_path = kb_mgr.backup_vector_store()
                    logger.info(
                        "安全模式: 更新前召回率=%.2f%%, 备份=%s",
                        before_recall * 100,
                        backup_path,
                    )
                except Exception as e:
                    logger.warning("备份失败，跳过安全模式: %s", e)

            # 文本分割 + 编码 + 写入 Qdrant
            from langchain.text_splitter import RecursiveCharacterTextSplitter

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
            )
            embedder = self.embedding_model
            payloads = []
            for doc in documents:
                text = doc.get("text", "") or ""
                metadata = doc.get("metadata", {}) or {}
                for chunk in splitter.split_text(text):
                    payloads.append(
                        {
                            "text": chunk,
                            "metadata": metadata,
                            "embedding": embedder.embed(chunk),
                        }
                    )

            count = upsert_documents(payloads)
            logger.info("成功写入 %d 个文档块到向量存储", count)

            # 安全模式：更新后回归测试
            if safe_mode and backup_path:
                try:
                    from evaluation.kb_version_manager import KnowledgeBaseManager

                    kb_mgr = KnowledgeBaseManager()
                    after_recall = kb_mgr.run_regression_test()["avg_recall"]

                    recall_decline = before_recall - after_recall
                    threshold = 0.15  # 召回率下降超过15%时回滚

                    if recall_decline > threshold:
                        logger.error(
                            "召回率下降 %.2f%% > 阈值 %.2f%%，自动回滚！",
                            recall_decline * 100,
                            threshold * 100,
                        )
                        kb_mgr.restore_vector_store(backup_path)
                        self._retriever = None
                        logger.warning("已回滚到更新前版本")
                        return 0
                    else:
                        logger.info(
                            "回归测试通过: 召回率 %.2f%% → %.2f%%",
                            before_recall * 100,
                            after_recall * 100,
                        )
                except Exception as e:
                    logger.warning("回归测试失败: %s", e)

            return count

        except Exception as e:
            logger.error("添加文档失败: %s", e)
            return 0

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """检索相关文档"""
        try:
            docs = self.retriever.retrieve(query, top_k=k)
            return [
                {
                    "text": d["page_content"],
                    "metadata": d["metadata"],
                    "score": d["score"],
                }
                for d in docs
            ]
        except Exception as e:
            logger.error("检索失败: %s", e)
            return []

    def chat_with_rag(
        self,
        message: str,
        conversation_id: str = "default",
    ) -> str:
        """基于 RAG 的对话"""
        if not LLMConfig.validate():
            return "AI 服务未配置（DASHSCOPE_API_KEY 缺失），请先配置 API Key"

        try:
            # 1. 获取历史并做历史感知的查询改写
            history = self.memory.get_langchain_messages(
                conversation_id, limit=10
            )
            rewritten = self.rewrite_query(message, history=history)

            # 2. 历史感知的混合检索（BM25 + 向量 → RRF → 精排）
            docs = self.retriever.retrieve(
                rewritten, top_k=5, history=history
            )
            context = "\n\n".join(
                d["page_content"].strip()
                for d in docs
                if d.get("page_content") and d["page_content"].strip()
            )

            if not context:
                # 降级为普通对话
                logger.warning("知识库无可用上下文，降级为普通对话")
                return self._chat_without_rag(message, conversation_id)

            # 3. 结合上下文与历史生成回答
            qa_prompt = ChatPromptTemplate.from_messages([
                ("system", "你是一个专业的反诈骗助手。基于以下上下文回答问题：\n\n{context}"),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ])
            chain = qa_prompt | self.chat_model
            response = chain.invoke({
                "context": context,
                "input": message,
                "chat_history": history,
            })
            answer = response.content if response.content else ""

            # 4. 保存对话历史（写入真实 AI 消息）
            self.memory.add_message(conversation_id, HumanMessage(content=message))
            self.memory.add_message(conversation_id, AIMessage(content=answer))

            return answer

        except Exception as e:
            logger.error("RAG 对话失败: %s", e, exc_info=True)
            return f"对话处理失败: {str(e)}"

    def _chat_without_rag(self, message: str, conversation_id: str) -> str:
        """无 RAG 的普通对话"""
        try:
            history = self.memory.get_langchain_messages(
                conversation_id, limit=10
            )
            messages = history + [HumanMessage(content=message)]
            response = self.chat_model.invoke(messages)

            result = response.content if response.content else ""

            self.memory.add_message(conversation_id, HumanMessage(content=message))
            self.memory.add_message(conversation_id, AIMessage(content=result))

            return result

        except Exception as e:
            logger.error("普通对话失败: %s", e)
            return f"对话处理失败: {str(e)}"

    def get_stats(self) -> Dict[str, Any]:
        """获取 RAG 统计信息"""
        try:
            count = collection_count()
            return {
                "vector_store_path": LLMConfig.QDRANT_PATH,
                "document_count": count if count is not None else 0,
                "collection": DEFAULT_COLLECTION,
                "api_key_configured": bool(LLMConfig.DASHSCOPE_API_KEY),
            }
        except Exception as e:
            return {"error": str(e)}
