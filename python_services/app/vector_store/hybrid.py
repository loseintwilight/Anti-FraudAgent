"""
混合检索模块
BM25 关键词路 + Qdrant 向量路 → RRF(k=60) 融合 → 可选 CrossEncoder 精排。

对外契约（contract c2）：
    HybridRetriever.retrieve(query, top_k=5, history=None) -> list[dict]
        每个 dict 含 page_content / metadata / score / source
    retrieve_context(query: str, k: int = 3) -> str
    collection_count() -> int | None

所有第三方依赖（qdrant-client / rank_bm25 / sentence-transformers）均 lazy import，
缺失或加载失败时自动降级并打日志，保证模块 import 不崩。
"""
from __future__ import annotations

import logging
import os
import re
import threading
import uuid
from typing import Any, Dict, List, Optional

from app.llm.config import LLMConfig

logger = logging.getLogger(__name__)

# 集合名与融合/精排参数
COLLECTION_NAME = LLMConfig.QDRANT_COLLECTION
RRF_K = 60
RERANK_MODEL = os.getenv("RERANK_MODEL", "BAAI/bge-reranker-base")
RERANK_ENABLED = os.getenv("RERANK_ENABLED", "true").strip().lower() not in {
    "0", "false", "no", "off"
}

# Qdrant point id 需为合法 UUID，用命名空间把任意字符串 id 映射为稳定 UUID
_ID_NAMESPACE = uuid.UUID("6b8e2f10-9c3a-4d5e-8f71-2a4b6c8d0e12")

# ---- 客户端单例（本地持久化 / 可选远程），整进程复用避免本地存储锁冲突 ----
_client: Any = None
_client_initialized = False
_client_lock = threading.Lock()

# ---- 精排模型单例，加载失败只尝试一次 ----
_reranker: Any = None
_reranker_initialized = False
_reranker_lock = threading.Lock()

_embedder: Any = None
_default_retriever: Any = None


def get_client():
    """懒加载并复用 Qdrant 客户端单例，不可用时返回 None。"""
    global _client, _client_initialized
    if _client_initialized:
        return _client
    with _client_lock:
        if _client_initialized:
            return _client
        _client_initialized = True
        try:
            from qdrant_client import QdrantClient

            if LLMConfig.QDRANT_URL:
                _client = QdrantClient(url=LLMConfig.QDRANT_URL)
                logger.info("Qdrant 远程客户端已连接: %s", LLMConfig.QDRANT_URL)
            else:
                path = LLMConfig.QDRANT_PATH
                os.makedirs(path, exist_ok=True)
                _client = QdrantClient(path=path)
                logger.info("Qdrant 本地持久化客户端已初始化: %s", path)
        except ImportError:
            logger.warning("qdrant-client 未安装，向量层不可用，混合检索降级为空结果")
            _client = None
        except Exception as e:
            logger.error("初始化 Qdrant 客户端失败: %s", e)
            _client = None
        return _client


def collection_exists(client) -> bool:
    """判断集合是否存在，兼容不同 qdrant-client 版本。"""
    try:
        if hasattr(client, "collection_exists"):
            return bool(client.collection_exists(COLLECTION_NAME))
        names = [c.name for c in client.get_collections().collections]
        return COLLECTION_NAME in names
    except Exception as e:
        logger.error("检查 Qdrant 集合失败: %s", e)
        return False


def _ensure_collection(client, vector_size: int) -> bool:
    """集合不存在时按实际向量维度创建，维度由入库向量动态决定，不写死。"""
    if collection_exists(client):
        return True
    try:
        from qdrant_client.models import Distance, VectorParams

        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        logger.info("已创建 Qdrant 集合: %s (dim=%d)", COLLECTION_NAME, vector_size)
        return True
    except Exception as e:
        logger.error("创建 Qdrant 集合失败: %s", e)
        return False


def get_embedder():
    """复用 TextEmbedder 单例（其模型为 lazy import）。"""
    global _embedder
    if _embedder is None:
        from app.vector_store.embedder import TextEmbedder

        _embedder = TextEmbedder()
    return _embedder


def to_point_id(raw: Any) -> str:
    """把任意文档 id 映射为 Qdrant 可接受的稳定 UUID 字符串。"""
    return str(uuid.uuid5(_ID_NAMESPACE, str(raw)))


def _scroll_all(client) -> List[Dict[str, Any]]:
    """遍历集合全部条目，供 BM25 语料与候选池使用。"""
    items: List[Dict[str, Any]] = []
    offset = None
    try:
        while True:
            records, offset = client.scroll(
                collection_name=COLLECTION_NAME,
                limit=256,
                with_payload=True,
                with_vectors=False,
                offset=offset,
            )
            for record in records:
                payload = record.payload or {}
                items.append(
                    {
                        "id": str(record.id),
                        "page_content": payload.get("page_content", ""),
                        "metadata": payload.get("metadata") or {},
                    }
                )
            if offset is None:
                break
    except Exception as e:
        logger.error("遍历 Qdrant 集合失败: %s", e)
    return items


def upsert_documents(documents: List[Dict[str, Any]]) -> int:
    """把文档写入 Qdrant。每项含 text / metadata，可带 id / embedding。返回写入条数。"""
    if not documents:
        return 0
    client = get_client()
    if client is None:
        logger.warning("Qdrant 客户端不可用，跳过写入")
        return 0

    embedder = get_embedder()
    prepared = []
    for doc in documents:
        text = doc.get("text", "") or ""
        if not text.strip():
            continue
        vector = doc.get("embedding") or embedder.embed(text)
        if not vector:
            continue
        prepared.append(
            {
                "id": to_point_id(doc.get("id") or text),
                "vector": vector,
                "text": text,
                "metadata": doc.get("metadata") or {},
            }
        )
    if not prepared:
        return 0

    if not _ensure_collection(client, len(prepared[0]["vector"])):
        return 0

    try:
        from qdrant_client.models import PointStruct

        points = [
            PointStruct(
                id=p["id"],
                vector=p["vector"],
                payload={"page_content": p["text"], "metadata": p["metadata"]},
            )
            for p in prepared
        ]
        client.upsert(collection_name=COLLECTION_NAME, points=points)
        return len(points)
    except Exception as e:
        logger.error("写入 Qdrant 失败: %s", e)
        return 0


def collection_count() -> Optional[int]:
    """返回当前知识条目数；客户端不可用 / 空库时返回 None（不写死值）。"""
    client = get_client()
    if client is None:
        return None
    try:
        if not collection_exists(client):
            return None
        count = client.count(collection_name=COLLECTION_NAME, exact=True).count
    except Exception as e:
        logger.error("统计知识条目数失败: %s", e)
        return None
    return count if count and count > 0 else None


# ---- 检索辅助 ----
def _tokenize(text: str) -> List[str]:
    """中文按字、英文数字按词切分，供 BM25 使用。"""
    return re.findall(r"[0-9a-z]+|[\u4e00-\u9fff]", (text or "").lower())


def _rrf(rankings: List[List[str]], rrf_k: int = RRF_K) -> Dict[str, float]:
    """倒数排名融合：多路排名按 1/(k+rank) 累加。"""
    scores: Dict[str, float] = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, 1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (rrf_k + rank)
    return scores


def _combine_history(query: str, history) -> str:
    """把最近对话历史拼进检索串，实现历史感知检索。"""
    if not history:
        return query
    parts: List[str] = []
    for item in history[-4:]:
        if isinstance(item, str):
            parts.append(item)
        else:
            parts.append(str(getattr(item, "content", item)))
    extra = " ".join(p for p in parts if p)
    return (query + " " + extra).strip() if extra else query


def _get_reranker():
    """懒加载 CrossEncoder 精排模型；缺失/加载失败返回 None 并降级。"""
    global _reranker, _reranker_initialized
    if _reranker_initialized:
        return _reranker
    with _reranker_lock:
        if _reranker_initialized:
            return _reranker
        _reranker_initialized = True
        if not RERANK_ENABLED:
            logger.info("精排已按配置关闭，使用 RRF 融合结果")
            _reranker = None
            return _reranker
        try:
            from sentence_transformers import CrossEncoder

            _reranker = CrossEncoder(RERANK_MODEL)
            logger.info("精排模型已加载: %s", RERANK_MODEL)
        except ImportError:
            logger.warning("sentence-transformers 未安装，精排降级为 RRF 结果")
            _reranker = None
        except Exception as e:
            logger.warning(
                "精排模型 %s 加载失败，降级为 RRF 结果: %s", RERANK_MODEL, e
            )
            _reranker = None
        return _reranker


class HybridRetriever:
    """BM25 + 向量双路召回 → RRF 融合 → 可选精排。"""

    def __init__(self, enable_rerank: bool = True) -> None:
        self.enable_rerank = enable_rerank

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        history: list | None = None,
    ) -> List[Dict[str, Any]]:
        client = get_client()
        if client is None:
            logger.warning("Qdrant 客户端不可用，混合检索降级为空结果")
            return []
        if not collection_exists(client):
            return []

        corpus = _scroll_all(client)
        if not corpus:
            return []

        effective_query = _combine_history(query, history)
        bm25_ids = self._bm25_rank(corpus, effective_query, top_k)
        vector_ids = self._vector_rank(client, effective_query, top_k)
        if not bm25_ids and not vector_ids:
            return []

        fused = _rrf([bm25_ids, vector_ids])
        ordered_ids = sorted(fused, key=fused.get, reverse=True)
        by_id = {item["id"]: item for item in corpus}
        candidates = [(fused[i], by_id[i]) for i in ordered_ids if i in by_id]

        ranked = (
            self._apply_rerank(query, candidates, top_k)
            if self.enable_rerank
            else candidates
        )

        bm25_set = set(bm25_ids)
        vector_set = set(vector_ids)
        results: List[Dict[str, Any]] = []
        for score, item in ranked[:top_k]:
            paths = []
            if item["id"] in bm25_set:
                paths.append("bm25")
            if item["id"] in vector_set:
                paths.append("vector")
            results.append(
                {
                    "page_content": item["page_content"],
                    "metadata": item["metadata"],
                    "score": float(score),
                    "source": item["metadata"].get("source") or "qdrant",
                    "recall_paths": paths,
                    "fusion": "rrf_k60",
                }
            )
        return results

    @staticmethod
    def _bm25_rank(corpus: List[Dict[str, Any]], query: str, top_k: int) -> List[str]:
        try:
            from rank_bm25 import BM25Okapi
        except ImportError:
            logger.warning("rank_bm25 未安装，跳过 BM25 关键词路")
            return []
        try:
            tokenized = [_tokenize(item["page_content"]) for item in corpus]
            bm25 = BM25Okapi(tokenized)
            scores = bm25.get_scores(_tokenize(query))
            limit = max(top_k * 2, 10)
            order = sorted(range(len(corpus)), key=lambda i: scores[i], reverse=True)
            return [corpus[i]["id"] for i in order[:limit] if scores[i] > 0]
        except Exception as e:
            logger.warning("BM25 检索失败，跳过关键词路: %s", e)
            return []

    @staticmethod
    def _vector_rank(client, query: str, top_k: int) -> List[str]:
        try:
            vector = get_embedder().embed(query)
            limit = max(top_k * 2, 10)
            try:
                hits = client.query_points(
                    collection_name=COLLECTION_NAME,
                    query=vector,
                    limit=limit,
                ).points
            except AttributeError:
                hits = client.search(
                    collection_name=COLLECTION_NAME,
                    query_vector=vector,
                    limit=limit,
                )
            return [str(hit.id) for hit in hits]
        except Exception as e:
            logger.warning("向量检索失败，跳过向量路: %s", e)
            return []

    @staticmethod
    def _apply_rerank(query: str, candidates, top_k: int):
        reranker = _get_reranker()
        if reranker is None:
            logger.info("精排模型不可用，降级为 RRF 融合结果")
            return candidates
        pool = candidates[: max(top_k * 3, 10)]
        try:
            pairs = [[query, item["page_content"]] for _, item in pool]
            scores = reranker.predict(pairs)
            reranked = [(float(s), item) for (_, item), s in zip(pool, scores)]
            reranked.sort(key=lambda x: x[0], reverse=True)
            # pool 之外的候选保留 RRF 顺序
            return reranked + candidates[len(pool) :]
        except Exception as e:
            logger.warning("精排执行失败，降级为 RRF 融合结果: %s", e)
            return candidates


def retrieve_context(query: str, k: int = 3) -> str:
    """返回拼接后的纯文本上下文；检索失败 / 空库返回空字符串。"""
    global _default_retriever
    try:
        if _default_retriever is None:
            _default_retriever = HybridRetriever()
        docs = _default_retriever.retrieve(query, top_k=k)
        parts = [
            d["page_content"].strip()
            for d in docs
            if d.get("page_content") and d["page_content"].strip()
        ]
        return "\n\n".join(parts)
    except Exception as e:
        logger.error("检索上下文失败，返回空字符串: %s", e)
        return ""
