"""
文本向量化模块
使用 sentence-transformers 将文本转为向量
"""

from __future__ import annotations

import logging
from typing import List, Optional, Union

logger = logging.getLogger(__name__)

# 默认使用的模型名称
DEFAULT_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


class TextEmbedder:
    """
    文本向量化器
    使用 sentence-transformers 将文本转为向量表示
    """

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME) -> None:
        """
        初始化嵌入器

        参数:
            model_name: 预训练模型名称，默认使用多语言模型
        """
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        """懒加载模型实例"""
        if self._model is None:
            self._load_model()
        return self._model

    def _load_model(self) -> None:
        """加载 sentence-transformers 模型"""
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"开始加载 embedding 模型: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            logger.info("embedding 模型加载完成")
        except ImportError:
            logger.warning(
                "sentence-transformers 未安装，使用降级方案（基于哈希的简单向量化）"
            )
            self._model = None
        except Exception as e:
            logger.error(f"加载 embedding 模型失败: {e}")
            self._model = None

    def embed(self, text: str) -> List[float]:
        """
        将单条文本转为向量

        参数:
            text: 输入文本

        返回:
            浮点数向量列表
        """
        if not text or not text.strip():
            return [0.0] * self._get_dimension()

        try:
            if self._model is not None:
                embedding = self._model.encode(text, show_progress_bar=False)
                return embedding.tolist()
            else:
                return self._fallback_embed(text)
        except Exception as e:
            logger.error(f"向量化失败: {e}")
            return [0.0] * self._get_dimension()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        批量将文本转为向量

        参数:
            texts: 文本列表

        返回:
            向量列表
        """
        if not texts:
            return []

        try:
            if self._model is not None:
                embeddings = self._model.encode(
                    texts, show_progress_bar=False
                )
                return [emb.tolist() for emb in embeddings]
            else:
                return [self._fallback_embed(t) for t in texts]
        except Exception as e:
            logger.error(f"批量向量化失败: {e}")
            return [[0.0] * self._get_dimension() for _ in texts]

    def _get_dimension(self) -> int:
        """获取向量维度"""
        if self._model is not None:
            try:
                return self._model.get_sentence_embedding_dimension()
            except Exception:
                pass
        return 384  # MiniLM 默认维度

    @staticmethod
    def _fallback_embed(text: str) -> List[float]:
        """
        降级方案：模型不可用时使用简单的基于哈希的向量化
        生成固定 384 维的向量
        """
        import hashlib

        dim = 384
        vector = [0.0] * dim

        # 对每个字符的 Unicode 值做哈希映射
        for i, char in enumerate(text[:500]):  # 限制长度
            hash_val = hashlib.md5(
                f"{char}{i}".encode()
            ).hexdigest()
            # 将哈希值映射到向量的不同维度
            for j in range(8):
                idx = (i * 8 + j) % dim
                val = int(hash_val[j * 4: (j + 1) * 4], 16) / 65535.0
                vector[idx] += val

        # 归一化
        magnitude = sum(v * v for v in vector) ** 0.5
        if magnitude > 0:
            vector = [v / magnitude for v in vector]

        return vector
