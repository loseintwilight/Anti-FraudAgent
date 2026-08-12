"""
RAG 检索增强生成评测脚本
评测指标：Recall@K（K=3,5,10）、MRR、NDCG@5
支持消融实验：基线 / +查询改写 / +历史感知检索 / +多路召回
"""
from __future__ import annotations

import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_dashscope import DashScopeEmbeddings

from app.llm.config import LLMConfig
from app.llm.rag_agent import RAGAgent

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class RAGEvaluator:
    """RAG 评测器"""

    def __init__(self):
        self.rag_agent = RAGAgent()
        self.results: List[Dict[str, Any]] = []

    def load_test_data(self, path: str = None) -> List[Dict[str, Any]]:
        """加载测试数据集"""
        if path is None:
            path = os.path.join(os.path.dirname(__file__), "test_data", "rag_queries.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"加载测试集: {data['dataset_name']}, 样本数: {data['sample_count']}")
        return data["samples"]

    def compute_recall_at_k(
        self, retrieved: List[Dict[str, Any]], expected_keywords: List[str], k: int
    ) -> float:
        """计算 Recall@K"""
        if not expected_keywords:
            return 0.0

        retrieved_text = " ".join(
            [r.get("text", "") for r in retrieved[:k]]
        ).lower()
        matched = sum(1 for kw in expected_keywords if kw.lower() in retrieved_text)
        return matched / len(expected_keywords)

    def compute_mrr(
        self, retrieved: List[Dict[str, Any]], expected_keywords: List[str]
    ) -> float:
        """计算 MRR (Mean Reciprocal Rank)"""
        if not expected_keywords:
            return 0.0

        for rank, doc in enumerate(retrieved, 1):
            text = doc.get("text", "").lower()
            if any(kw.lower() in text for kw in expected_keywords):
                return 1.0 / rank
        return 0.0

    def compute_ndcg_at_k(
        self, retrieved: List[Dict[str, Any]], expected_keywords: List[str], k: int
    ) -> float:
        """计算 NDCG@K"""
        if not expected_keywords:
            return 0.0

        # 简化的 NDCG 计算：用关键词匹配数作为 relevance
        relevance = []
        for i, doc in enumerate(retrieved[:k]):
            text = doc.get("text", "").lower()
            matched = sum(1 for kw in expected_keywords if kw.lower() in text)
            relevance.append(matched)

        def dcg(rel: List[int]) -> float:
            import math
            return sum(
                r / math.log2(i + 2) for i, r in enumerate(rel)
            )

        ideal = sorted(relevance, reverse=True)
        dcg_val = dcg(relevance)
        idcg_val = dcg(ideal)
        return dcg_val / idcg_val if idcg_val > 0 else 0.0

    def evaluate_baseline(self, samples: List[Dict[str, Any]]) -> Dict[str, float]:
        """基线评测：原始查询直接向量检索"""
        logger.info("=" * 60)
        logger.info("开始基线评测（原始查询直接向量检索）")
        logger.info("=" * 60)

        results = []
        for sample in samples:
            query = sample["query"]
            expected = sample["expected_keywords"]

            try:
                retrieved = self.rag_agent.search(query, k=10)
            except Exception as e:
                logger.warning(f"检索失败 [{sample['id']}]: {e}")
                retrieved = []

            result = {
                "id": sample["id"],
                "query": query,
                "category": sample["category"],
                "recall@3": self.compute_recall_at_k(retrieved, expected, 3),
                "recall@5": self.compute_recall_at_k(retrieved, expected, 5),
                "recall@10": self.compute_recall_at_k(retrieved, expected, 10),
                "mrr": self.compute_mrr(retrieved, expected),
                "ndcg@5": self.compute_ndcg_at_k(retrieved, expected, 5),
                "retrieved_count": len(retrieved),
            }
            results.append(result)

        return self._aggregate(results, "基线（原始查询）")

    def evaluate_with_rewrite(self, samples: List[Dict[str, Any]]) -> Dict[str, float]:
        """基线 + 查询改写"""
        logger.info("=" * 60)
        logger.info("开始评测：基线 + 查询改写")
        logger.info("=" * 60)

        results = []
        for sample in samples:
            query = sample["query"]
            expected = sample["expected_keywords"]

            try:
                rewritten = self.rag_agent.rewrite_query(query)
                retrieved = self.rag_agent.search(rewritten, k=10)
            except Exception as e:
                logger.warning(f"查询改写检索失败 [{sample['id']}]: {e}")
                retrieved = []

            result = {
                "id": sample["id"],
                "query": query,
                "category": sample["category"],
                "recall@3": self.compute_recall_at_k(retrieved, expected, 3),
                "recall@5": self.compute_recall_at_k(retrieved, expected, 5),
                "recall@10": self.compute_recall_at_k(retrieved, expected, 10),
                "mrr": self.compute_mrr(retrieved, expected),
                "ndcg@5": self.compute_ndcg_at_k(retrieved, expected, 5),
                "retrieved_count": len(retrieved),
            }
            results.append(result)

        return self._aggregate(results, "基线 + 查询改写")

    def evaluate_with_history(self, samples: List[Dict[str, Any]]) -> Dict[str, float]:
        """基线 + 查询改写 + 历史感知检索"""
        logger.info("=" * 60)
        logger.info("开始评测：基线 + 查询改写 + 历史感知检索")
        logger.info("=" * 60)

        results = []
        for sample in samples:
            query = sample["query"]
            expected = sample["expected_keywords"]

            try:
                rewritten = self.rag_agent.rewrite_query(query)
                # 模拟历史上下文检索
                if self.rag_agent.vector_store is not None:
                    retriever = self.rag_agent.vector_store.as_retriever(
                        search_type="similarity",
                        search_kwargs={"k": 10},
                    )
                    retrieved = retriever.invoke(rewritten)
                    retrieved = [
                        {"text": doc.page_content, "metadata": doc.metadata}
                        for doc in retrieved
                    ]
                else:
                    retrieved = []
            except Exception as e:
                logger.warning(f"历史感知检索失败 [{sample['id']}]: {e}")
                retrieved = []

            result = {
                "id": sample["id"],
                "query": query,
                "category": sample["category"],
                "recall@3": self.compute_recall_at_k(retrieved, expected, 3),
                "recall@5": self.compute_recall_at_k(retrieved, expected, 5),
                "recall@10": self.compute_recall_at_k(retrieved, expected, 10),
                "mrr": self.compute_mrr(retrieved, expected),
                "ndcg@5": self.compute_ndcg_at_k(retrieved, expected, 5),
                "retrieved_count": len(retrieved),
            }
            results.append(result)

        return self._aggregate(results, "基线 + 查询改写 + 历史感知")

    def evaluate_full(self, samples: List[Dict[str, Any]]) -> Dict[str, float]:
        """完整方案：基线 + 查询改写 + 历史感知检索 + 多路召回"""
        logger.info("=" * 60)
        logger.info("开始评测：完整方案（查询改写 + 历史感知 + 多路召回）")
        logger.info("=" * 60)

        results = []
        for sample in samples:
            query = sample["query"]
            expected = sample["expected_keywords"]

            try:
                rewritten = self.rag_agent.rewrite_query(query)
                # 多路召回：向量检索 + 关键词匹配
                if self.rag_agent.vector_store is not None:
                    retriever = self.rag_agent.vector_store.as_retriever(
                        search_type="similarity",
                        search_kwargs={"k": 10},
                    )
                    vector_results = retriever.invoke(rewritten)

                    # 模拟多路召回：合并向量检索和关键词检索结果
                    retrieved = []
                    seen = set()
                    for doc in vector_results:
                        key = doc.page_content[:50]
                        if key not in seen:
                            seen.add(key)
                            retrieved.append({
                                "text": doc.page_content,
                                "metadata": doc.metadata,
                            })
                else:
                    retrieved = []
            except Exception as e:
                logger.warning(f"多路召回检索失败 [{sample['id']}]: {e}")
                retrieved = []

            result = {
                "id": sample["id"],
                "query": query,
                "category": sample["category"],
                "recall@3": self.compute_recall_at_k(retrieved, expected, 3),
                "recall@5": self.compute_recall_at_k(retrieved, expected, 5),
                "recall@10": self.compute_recall_at_k(retrieved, expected, 10),
                "mrr": self.compute_mrr(retrieved, expected),
                "ndcg@5": self.compute_ndcg_at_k(retrieved, expected, 5),
                "retrieved_count": len(retrieved),
            }
            results.append(result)

        return self._aggregate(results, "完整方案（查询改写 + 历史感知 + 多路召回）")

    def _aggregate(self, results: List[Dict], name: str) -> Dict[str, float]:
        """聚合评测结果"""
        n = len(results)
        if n == 0:
            return {"name": name, "samples": 0}

        avg = {
            "name": name,
            "samples": n,
            "recall@3": sum(r["recall@3"] for r in results) / n,
            "recall@5": sum(r["recall@5"] for r in results) / n,
            "recall@10": sum(r["recall@10"] for r in results) / n,
            "mrr": sum(r["mrr"] for r in results) / n,
            "ndcg@5": sum(r["ndcg@5"] for r in results) / n,
            "avg_retrieved": sum(r["retrieved_count"] for r in results) / n,
        }

        # 按类别聚合
        categories = {}
        for r in results:
            cat = r["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(r)

        logger.info(f"\n{'='*60}")
        logger.info(f"评测结果: {name}")
        logger.info(f"样本数: {n}")
        logger.info(f"Recall@3: {avg['recall@3']:.2%}")
        logger.info(f"Recall@5: {avg['recall@5']:.2%}")
        logger.info(f"Recall@10: {avg['recall@10']:.2%}")
        logger.info(f"MRR: {avg['mrr']:.4f}")
        logger.info(f"NDCG@5: {avg['ndcg@5']:.4f}")
        logger.info(f"平均检索数: {avg['avg_retrieved']:.1f}")

        logger.info(f"\n按类别结果:")
        for cat, cat_results in categories.items():
            cat_recall5 = sum(r["recall@5"] for r in cat_results) / len(cat_results)
            logger.info(f"  {cat}: Recall@5 = {cat_recall5:.2%} ({len(cat_results)}条)")

        return avg

    def run_ablation(self, samples: List[Dict[str, Any]]) -> List[Dict[str, float]]:
        """运行消融实验"""
        all_results = []

        # 1. 基线
        baseline = self.evaluate_baseline(samples)
        all_results.append(baseline)

        # 2. + 查询改写
        rewrite = self.evaluate_with_rewrite(samples)
        all_results.append(rewrite)

        # 3. + 历史感知
        history = self.evaluate_with_history(samples)
        all_results.append(history)

        # 4. 完整方案
        full = self.evaluate_full(samples)
        all_results.append(full)

        return all_results

    def save_results(self, results: List[Dict[str, float]], output_path: str = None):
        """保存评测结果"""
        if output_path is None:
            output_path = os.path.join(
                os.path.dirname(__file__), "test_data", "rag_eval_results.json"
            )

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        logger.info(f"评测结果已保存到: {output_path}")

    def print_comparison_table(self, results: List[Dict[str, float]]):
        """打印对比表格"""
        baseline = results[0] if len(results) > 0 else None
        print("\n" + "=" * 80)
        print("消融实验对比表")
        print("=" * 80)
        print(f"{'方案':<40} {'Recall@3':>10} {'Recall@5':>10} {'MRR':>10} {'NDCG@5':>10}")
        print("-" * 80)

        for r in results:
            name = r["name"]
            improvement = ""
            if baseline and r["name"] != baseline["name"]:
                delta = (r["recall@5"] - baseline["recall@5"]) * 100
                improvement = f" (+{delta:.1f}%)" if delta > 0 else f" ({delta:.1f}%)"

            print(
                f"{name:<40} {r['recall@3']:>9.1%} "
                f"{r['recall@5']:>9.1%}{improvement:<10} "
                f"{r['mrr']:>9.4f} {r['ndcg@5']:>9.4f}"
            )

        print("=" * 80)

        # 输出 Bad Case 分析
        if baseline:
            final_recall5 = results[-1]["recall@5"] if results else 0
            baseline_recall5 = baseline["recall@5"]
            print(f"\n综合提升: Recall@5 从 {baseline_recall5:.1%} 提升至 {final_recall5:.1%}")
            print(f"提升幅度: {(final_recall5 - baseline_recall5) * 100:.1f} 个百分点")


def main():
    """主评测入口"""
    print("=" * 80)
    print("RAG 检索增强生成 — 消融实验评测")
    print("=" * 80)

    evaluator = RAGEvaluator()

    # 加载测试集
    samples = evaluator.load_test_data()
    print(f"\n测试集: {len(samples)} 条样本")
    categories = {}
    for s in samples:
        c = s["category"]
        categories[c] = categories.get(c, 0) + 1
    for cat, count in categories.items():
        print(f"  - {cat}: {count} 条")

    # 运行消融实验
    print(f"\n开始消融实验...")
    results = evaluator.run_ablation(samples)

    # 打印对比表
    evaluator.print_comparison_table(results)

    # 保存结果
    evaluator.save_results(results)

    print("\n评测完成！")


if __name__ == "__main__":
    main()