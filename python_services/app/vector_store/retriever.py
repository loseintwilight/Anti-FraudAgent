"""
向量存储与检索模块
使用 ChromaDB 实现向量存储和相似度检索
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)

# 默认集合名称
DEFAULT_COLLECTION_NAME = "anti_fraud_articles"

# 默认 ChromaDB 持久化路径
DEFAULT_PERSIST_DIR = "./chroma_db"


class VectorRetriever:
    """
    向量检索器
    使用 ChromaDB 存储和检索向量化文档
    """

    def __init__(
        self,
        collection_name: str = DEFAULT_COLLECTION_NAME,
        persist_directory: str = DEFAULT_PERSIST_DIR,
    ) -> None:
        """
        初始化检索器

        参数:
            collection_name: ChromaDB 集合名称
            persist_directory: 持久化存储目录
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self._client = None
        self._collection = None

    @property
    def client(self):
        """懒加载 ChromaDB 客户端"""
        if self._client is None:
            self._init_client()
        return self._client

    @property
    def collection(self):
        """懒加载集合"""
        if self._collection is None:
            self._init_collection()
        return self._collection

    def _init_client(self) -> None:
        """初始化 ChromaDB 客户端"""
        try:
            import chromadb
            self._client = chromadb.PersistentClient(
                path=self.persist_directory
            )
            logger.info(
                f"ChromaDB 客户端已初始化: {self.persist_directory}"
            )
        except ImportError:
            logger.warning("chromadb 未安装，使用内存模式")
            self._client = None
        except Exception as e:
            logger.error(f"初始化 ChromaDB 失败: {e}")
            self._client = None

    def _init_collection(self) -> None:
        """获取或创建集合"""
        if self._client is None:
            logger.warning("ChromaDB 客户端不可用，跳过集合初始化")
            return

        try:
            # 尝试获取已有集合
            self._collection = self._client.get_collection(self.collection_name)
            logger.info(f"获取已有集合: {self.collection_name}")
        except Exception:
            # 不存在则创建
            try:
                self._collection = self._client.create_collection(
                    self.collection_name
                )
                logger.info(f"创建新集合: {self.collection_name}")
            except Exception as e:
                logger.error(f"创建集合失败: {e}")
                self._collection = None

    def add_document(
        self,
        document_id: Optional[str] = None,
        text: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        embedding: Optional[List[float]] = None,
    ) -> bool:
        """
        添加单个文档到向量存储

        参数:
            document_id: 文档 ID，若不提供则自动生成
            text: 文档文本内容
            metadata: 文档元数据
            embedding: 文档向量，若不提供则需先实例化 embedder

        返回:
            是否添加成功
        """
        if self.collection is None:
            logger.warning("集合不可用，无法添加文档")
            return False

        doc_id = document_id or str(uuid.uuid4())
        metadata = metadata or {}

        try:
            if embedding:
                # 直接使用提供的向量
                self.collection.add(
                    ids=[doc_id],
                    documents=[text],
                    metadatas=[metadata],
                    embeddings=[embedding],
                )
            else:
                # 不传向量，让 ChromaDB 使用其内置的 all-MiniLM-L6-v2
                self.collection.add(
                    ids=[doc_id],
                    documents=[text],
                    metadatas=[metadata],
                )

            logger.debug(f"文档添加成功: id={doc_id}")
            return True
        except Exception as e:
            logger.error(f"添加文档失败: {e}")
            return False

    def add_documents(
        self,
        documents: List[Dict[str, Any]],
        embeddings: Optional[List[List[float]]] = None,
    ) -> int:
        """
        批量添加文档

        参数:
            documents: 文档列表，每项包含 id, text, metadata
            embeddings: 对应的向量列表（可选）

        返回:
            成功添加的文档数量
        """
        if not documents:
            return 0

        if self.collection is None:
            logger.warning("集合不可用，无法批量添加文档")
            return 0

        success_count = 0
        for i, doc in enumerate(documents):
            embedding = embeddings[i] if embeddings and i < len(embeddings) else None
            ok = self.add_document(
                document_id=doc.get("id"),
                text=doc.get("text", ""),
                metadata=doc.get("metadata"),
                embedding=embedding,
            )
            if ok:
                success_count += 1

        logger.info(f"批量添加文档: {success_count}/{len(documents)} 成功")
        return success_count

    def search(
        self,
        query: Union[str, List[float]],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        向量相似度检索

        参数:
            query: 查询文本（字符串）或查询向量（浮点数列表）
            n_results: 返回结果数量
            where: 过滤条件（可选），如 {"source": "mps_gov"}

        返回:
            {
                "ids": List[List[str]],
                "distances": List[List[float]],
                "documents": List[List[str]],
                "metadatas": List[List[Dict]],
            }
        """
        if self.collection is None:
            logger.warning("集合不可用，无法检索")
            return {"ids": [], "distances": [], "documents": [], "metadatas": []}

        try:
            kwargs: Dict[str, Any] = {
                "n_results": n_results,
            }

            # 判断查询类型
            if isinstance(query, str):
                kwargs["query_texts"] = [query]
            else:
                kwargs["query_embeddings"] = [query]

            if where:
                kwargs["where"] = where

            results = self.collection.query(**kwargs)
            return results
        except Exception as e:
            logger.error(f"检索失败: {e}")
            return {"ids": [], "distances": [], "documents": [], "metadatas": []}

    def delete_document(self, document_id: str) -> bool:
        """
        从向量存储中删除文档

        参数:
            document_id: 文档 ID

        返回:
            是否删除成功
        """
        if self.collection is None:
            return False

        try:
            self.collection.delete(ids=[document_id])
            logger.debug(f"文档删除成功: id={document_id}")
            return True
        except Exception as e:
            logger.error(f"删除文档失败: {e}")
            return False

    def get_collection_stats(self) -> Dict[str, Any]:
        """获取集合统计信息"""
        if self.collection is None:
            return {"status": "unavailable", "count": 0}

        try:
            count = self.collection.count()
            return {
                "status": "available",
                "count": count,
                "collection_name": self.collection_name,
                "persist_directory": self.persist_directory,
            }
        except Exception as e:
            logger.error(f"获取集合统计失败: {e}")
            return {"status": "error", "count": 0, "error": str(e)}
