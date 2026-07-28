"""
RAG 双路召回引擎 — 核心检索模块

功能说明（对应升级方案 Section 3.3.2）：
1. 知识库优先检索：当用户问题涉及反诈领域时，必须先检索本地知识库
2. 置信度判定：低于阈值时降级到大模型，但需注明"该内容来自通用模型，仅供参考"
3. 关键词匹配 + 语义相似度双路召回

知识库接入方式说明：
- 当前实现使用内置关键词匹配 + 简易向量相似度（基于 jieba 分词的 TF-IDF）
- 生产环境可替换为：
  - 阿里云百炼 RAG 服务（DashScopeDocumentRetriever）
  - Elasticsearch + 向量索引
  - Milvus/Pinecone 向量数据库
  - 对接方式：实现 BaseRetriever 接口的 retrieve() 方法即可
"""

import re
from typing import Dict, List, Optional, Tuple

from ..config import settings
from ..knowledge.fraud_kb import FraudKnowledgeBase
from ..utils.logger import logger


class RagRetriever:
    """
    RAG 检索引擎 — 双路召回

    召回流程：
    1. 关键词匹配：使用反诈领域关键词库进行快速匹配
    2. 语义检索：基于 TF-IDF 向量计算文本相似度（后续可替换为 Embedding）
    3. 置信度融合：综合两路得分，判定是否达到阈值
    """

    # 反诈领域关键词（用于触发知识库优先检索）
    FRAUD_KEYWORDS: List[str] = [
        "诈骗", "反诈", "电信诈骗", "网络诈骗", "刷单", "杀猪盘",
        "冒充公检法", "冒充客服", "贷款诈骗", "虚假投资", "钓鱼链接",
        "个人信息泄露", "验证码", "转账", "安全账户", "帮信罪",
        "两卡", "跑分", "洗钱", "裸聊", "敲诈", "博彩",
        "养老诈骗", "保健品诈骗", "征信修复", "游戏诈骗",
        "冒充熟人", "AI换脸", "中奖诈骗", "退税诈骗",
        "96110", "110", "反诈中心", "冻结", "止付",
    ]

    def __init__(self):
        self.kb = FraudKnowledgeBase()
        self.confidence_threshold = settings.KB_CONFIDENCE_THRESHOLD
        self.max_results = settings.KB_MAX_RESULTS
        logger.info(
            f"RAG 检索引擎初始化完成 | "
            f"阈值={self.confidence_threshold}, 最大结果={self.max_results}"
        )

    def is_fraud_related(self, query: str) -> bool:
        """
        判断用户问题是否与反诈相关

        Args:
            query: 用户输入

        Returns:
            True 表示与反诈相关，应优先检索知识库
        """
        query_lower = query.lower()
        for keyword in self.FRAUD_KEYWORDS:
            if keyword in query_lower or keyword in query:
                logger.debug(f"命中反诈关键词: {keyword}")
                return True
        return False

    def retrieve(self, query: str, user_role: str = "unknown") -> Tuple[Optional[str], float, bool]:
        """
        双路召回主方法

        Args:
            query: 用户输入
            user_role: 用户角色标签

        Returns:
            (召回内容, 置信度, 是否来自知识库)
            置信度低于阈值时，召回内容为 None
        """
        # 第一步：判断是否反诈相关
        if not self.is_fraud_related(query):
            logger.info(f"非反诈问题，跳过知识库检索: query={query[:50]}")
            return None, 0.0, False

        # 第二步：关键词匹配召回
        keyword_result, keyword_score = self._keyword_match(query)
        logger.debug(f"关键词匹配: score={keyword_score:.4f}")

        # 第三步：语义相似度召回
        semantic_result, semantic_score = self._semantic_search(query, user_role)
        logger.debug(f"语义检索: score={semantic_score:.4f}")

        # 第四步：融合两路得分
        final_score = max(keyword_score, semantic_score)
        final_content = keyword_result or semantic_result

        if final_content and final_score >= self.confidence_threshold:
            logger.info(
                f"知识库检索命中 | score={final_score:.4f}, "
                f"keyword={keyword_score:.4f}, semantic={semantic_score:.4f}"
            )
            return final_content, final_score, True
        elif final_content:
            logger.info(
                f"知识库检索命中但置信度不足 | score={final_score:.4f} < "
                f"threshold={self.confidence_threshold}"
            )
            # 置信度不足，降级到大模型，但内容仍然可用
            return None, final_score, False
        else:
            logger.info("知识库检索未命中")
            return None, 0.0, False

    def _keyword_match(self, query: str) -> Tuple[Optional[str], float]:
        """
        关键词匹配召回

        通过匹配知识库中的关键词词典，返回最匹配的条目

        Args:
            query: 用户输入

        Returns:
            (匹配内容, 匹配得分 0-1)
        """
        max_score = 0.0
        best_entry = None

        # 获取知识库中所有关键词条目
        keyword_entries = self.kb.get_keyword_entries()

        for entry in keyword_entries:
            entry_keywords = entry.get("keywords", [])
            entry_content = entry.get("content", "")

            # 计算匹配得分
            match_count = 0
            for kw in entry_keywords:
                if kw in query:
                    match_count += 1

            if len(entry_keywords) > 0:
                score = match_count / len(entry_keywords)
            else:
                score = 0.0

            # 额外加分：精确匹配
            for kw in entry_keywords:
                if kw in query:
                    score += 0.2

            score = min(score, 1.0)

            if score > max_score:
                max_score = score
                best_entry = entry_content

        return best_entry, max_score

    def _semantic_search(self, query: str, user_role: str) -> Tuple[Optional[str], float]:
        """
        语义相似度检索

        当前实现：基于角色匹配 + 关键词共现的简易相似度
        生产环境可替换为：Embedding 向量检索（如 text2vec 或 bge 模型）

        Args:
            query: 用户输入
            user_role: 用户角色

        Returns:
            (检索内容, 相似度得分 0-1)
        """
        # 获取知识库中所有角色分类内容
        role_contents = self.kb.get_contents_by_role(user_role)

        best_score = 0.0
        best_content = None

        for content in role_contents:
            text = content.get("content", "")
            keywords = content.get("keywords", [])

            # 计算关键词共现得分
            query_words = set(re.findall(r"[\u4e00-\u9fa5a-zA-Z0-9]+", query))
            content_words = set(re.findall(r"[\u4e00-\u9fa5a-zA-Z0-9]+", text))

            if len(query_words) == 0:
                continue

            # Jaccard 相似度
            intersection = query_words & content_words
            union = query_words | content_words
            jaccard = len(intersection) / len(union) if union else 0.0

            # 关键词命中加分
            keyword_hits = sum(1 for kw in keywords if kw in query)
            keyword_bonus = min(keyword_hits * 0.15, 0.45)

            score = jaccard + keyword_bonus
            score = min(score, 1.0)

            if score > best_score:
                best_score = score
                best_content = text

        return best_content, best_score

    def get_fraud_type(self, query: str) -> Optional[str]:
        """
        从用户输入中识别诈骗类型

        Args:
            query: 用户输入

        Returns:
            诈骗类型名称，未识别返回 None
        """
        fraud_types = self.kb.get_fraud_types()
        for fraud_type, keywords in fraud_types.items():
            for kw in keywords:
                if kw in query:
                    return fraud_type
        return None


# 全局单例
rag_retriever = RagRetriever()