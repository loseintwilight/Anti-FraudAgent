"""
RAG 检索增强生成模块
基于 LangChain + ChromaDB 实现，替代 Spring AI 的 RAG 配置
"""

import logging
from typing import Any, Dict, List, Optional

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains import create_history_aware_retriever
from langchain.schema import BaseRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_dashscope import DashScopeEmbeddings, ChatDashScope

from app.llm.config import LLMConfig
from app.llm.chat_memory import FileChatMemory

logger = logging.getLogger(__name__)

# 默认集合名称
DEFAULT_COLLECTION = "anti_fraud_articles"

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
    基于 LangChain + ChromaDB 实现知识检索增强的对话
    """

    def __init__(self):
        self._chat_model: Optional[ChatDashScope] = None
        self._embedding_model: Optional[DashScopeEmbeddings] = None
        self._vector_store: Optional[Chroma] = None
        self._retriever: Optional[BaseRetriever] = None
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
    def embedding_model(self) -> DashScopeEmbeddings:
        if self._embedding_model is None:
            self._embedding_model = DashScopeEmbeddings(
                model=LLMConfig.EMBEDDING_MODEL,
                dashscope_api_key=LLMConfig.DASHSCOPE_API_KEY,
            )
        return self._embedding_model

    @property
    def vector_store(self) -> Optional[Chroma]:
        if self._vector_store is None:
            try:
                self._vector_store = Chroma(
                    collection_name=DEFAULT_COLLECTION,
                    embedding_function=self.embedding_model,
                    persist_directory=LLMConfig.VECTOR_STORE_PATH,
                )
                logger.info(f"ChromaDB 向量存储已加载: {LLMConfig.VECTOR_STORE_PATH}")
            except Exception as e:
                logger.warning(f"加载 ChromaDB 失败: {e}，RAG 功能将不可用")
                self._vector_store = None
        return self._vector_store

    @property
    def retriever(self) -> Optional[BaseRetriever]:
        if self._retriever is None and self.vector_store is not None:
            self._retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5},
            )
        return self._retriever

    @property
    def memory(self) -> FileChatMemory:
        if self._memory is None:
            self._memory = FileChatMemory()
        return self._memory

    def rewrite_query(self, question: str) -> str:
        """重写查询以提高检索效果"""
        if not LLMConfig.validate():
            return question

        try:
            prompt = ChatPromptTemplate.from_messages([
                ("human", QUERY_REWRITE_PROMPT.format(question=question)),
            ])
            chain = prompt | self.chat_model
            response = chain.invoke({})
            rewritten = response.content.strip() if response.content else question
            logger.info(f"查询重写: {question[:30]} -> {rewritten[:30]}")
            return rewritten
        except Exception as e:
            logger.warning(f"查询重写失败: {e}，使用原始查询")
            return question

    def add_documents(self, documents: List[Dict[str, Any]]) -> int:
        """添加文档到向量存储"""
        if self.vector_store is None:
            logger.warning("向量存储不可用，无法添加文档")
            return 0

        try:
            docs = []
            for doc in documents:
                docs.append(Document(
                    page_content=doc.get("text", ""),
                    metadata=doc.get("metadata", {}),
                ))

            # 文本分割
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
            )
            split_docs = text_splitter.split_documents(docs)

            # 添加到向量存储
            self.vector_store.add_documents(split_docs)
            logger.info(f"成功添加 {len(split_docs)} 个文档块到向量存储")
            return len(split_docs)

        except Exception as e:
            logger.error(f"添加文档失败: {e}")
            return 0

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """检索相关文档"""
        if self.retriever is None:
            return []

        try:
            docs = self.retriever.invoke(query, k=k)
            results = []
            for doc in docs:
                results.append({
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "score": doc.metadata.get("score", 0.0),
                })
            return results

        except Exception as e:
            logger.error(f"检索失败: {e}")
            return []

    def chat_with_rag(
        self,
        message: str,
        conversation_id: str = "default",
    ) -> str:
        """基于 RAG 的对话"""
        if not LLMConfig.validate():
            return "AI 服务未配置（DASHSCOPE_API_KEY 缺失），请先配置 API Key"

        if self.retriever is None:
            # 降级为普通对话
            logger.warning("RAG 检索器不可用，降级为普通对话")
            return self._chat_without_rag(message, conversation_id)

        try:
            # 1. 重写查询
            rewritten = self.rewrite_query(message)

            # 2. 构建历史感知检索器
            history_prompt = ChatPromptTemplate.from_messages([
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ])

            # 3. 执行 RAG 对话
            qa_prompt = ChatPromptTemplate.from_messages([
                ("system", "你是一个专业的反诈骗助手。基于以下上下文回答问题：\n\n{context}"),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ])

            # 获取历史消息
            history = self.memory.get_langchain_messages(conversation_id, limit=10)

            # 创建检索链
            combine_docs_chain = create_stuff_documents_chain(
                self.chat_model, qa_prompt,
            )

            retrieval_chain = create_retrieval_chain(
                self.retriever, combine_docs_chain,
            )

            response = retrieval_chain.invoke({
                "input": rewritten,
                "chat_history": history,
            })

            answer = response.get("answer", "")

            # 保存对话历史
            self.memory.add_message(conversation_id, HumanMessage(content=message))
            self.memory.add_message(conversation_id, type(answer))

            return answer

        except Exception as e:
            logger.error(f"RAG 对话失败: {e}", exc_info=True)
            return f"对话处理失败: {str(e)}"

    def _chat_without_rag(self, message: str, conversation_id: str) -> str:
        """无 RAG 的普通对话"""
        try:
            history = self.memory.get_langchain_messages(conversation_id, limit=10)
            messages = [HumanMessage(content=message)]
            response = self.chat_model.invoke(messages)

            result = response.content if response.content else ""

            self.memory.add_message(conversation_id, HumanMessage(content=message))
            self.memory.add_message(conversation_id, type(result))

            return result

        except Exception as e:
            logger.error(f"普通对话失败: {e}")
            return f"对话处理失败: {str(e)}"

    def get_stats(self) -> Dict[str, Any]:
        """获取 RAG 统计信息"""
        try:
            count = 0
            if self.vector_store is not None:
                count = self.vector_store._collection.count()
            return {
                "vector_store_path": LLMConfig.VECTOR_STORE_PATH,
                "document_count": count,
                "collection": DEFAULT_COLLECTION,
                "api_key_configured": bool(LLMConfig.DASHSCOPE_API_KEY),
            }
        except Exception as e:
            return {"error": str(e)}