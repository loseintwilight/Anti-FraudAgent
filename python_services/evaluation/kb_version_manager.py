"""
知识库增量更新回归验证 + 版本回滚
- 每次增量更新前自动备份ChromaDB快照
- 更新后跑回归测试验证知识库质量
- 召回率下降超过阈值时自动回滚
"""
from __future__ import annotations

import json
import logging
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.llm.config import LLMConfig

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class KnowledgeBaseManager:
    """知识库版本管理器"""

    BACKUP_DIR = os.path.join(os.path.dirname(__file__), "..", "kb_backups")
    REGRESSION_QUERIES = [
        {"query": "什么是刷单诈骗", "expected_keywords": ["刷单", "兼职", "返利"]},
        {"query": "杀猪盘怎么骗人", "expected_keywords": ["杀猪盘", "网恋", "投资"]},
        {"query": "公检法会不会电话办案", "expected_keywords": ["公检法", "不会", "电话"]},
        {"query": "被骗了怎么办", "expected_keywords": ["报警", "96110", "冻结"]},
        {"query": "AI换脸诈骗怎么识别", "expected_keywords": ["AI", "换脸", "诈骗"]},
        {"query": "老年人防诈骗", "expected_keywords": ["老年人", "防骗", "提醒"]},
        {"query": "收到中奖短信", "expected_keywords": ["中奖", "短信", "诈骗"]},
        {"query": "虚假投资平台特征", "expected_keywords": ["投资", "虚假", "高收益"]},
        {"query": "接到诈骗电话怎么办", "expected_keywords": ["挂断", "报警", "96110"]},
        {"query": "网络贷款诈骗", "expected_keywords": ["贷款", "手续费", "诈骗"]},
        {"query": "冒充警察诈骗", "expected_keywords": ["冒充", "警察", "公检法"]},
        {"query": "客服退款诈骗", "expected_keywords": ["客服", "退款", "钓鱼"]},
        {"query": "有人让我转账", "expected_keywords": ["转账", "诈骗", "核实"]},
        {"query": "刷单兼职靠谱吗", "expected_keywords": ["刷单", "诈骗", "不靠谱"]},
        {"query": "收到验证码短信", "expected_keywords": ["验证码", "诈骗", "不要透露"]},
        {"query": "网上交友被骗", "expected_keywords": ["网恋", "杀猪盘", "报警"]},
        {"query": "AI合成语音诈骗", "expected_keywords": ["AI", "语音", "诈骗", "合成"]},
        {"query": "孩子玩游戏被骗", "expected_keywords": ["游戏", "充值", "诈骗", "未成年人"]},
        {"query": "医保卡诈骗", "expected_keywords": ["医保", "诈骗", "冒充"]},
        {"query": "96110是什么", "expected_keywords": ["96110", "反诈", "热线"]},
    ]

    def __init__(self):
        os.makedirs(self.BACKUP_DIR, exist_ok=True)

    def backup_vector_store(self, version: str = None) -> str:
        """备份当前向量存储"""
        if version is None:
            version = datetime.now().strftime("%Y%m%d_%H%M%S")

        source = LLMConfig.VECTOR_STORE_PATH
        backup_path = os.path.join(self.BACKUP_DIR, f"chroma_backup_{version}")

        if not os.path.exists(source):
            logger.warning(f"向量存储路径不存在: {source}")
            return ""

        try:
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)

            shutil.copytree(source, backup_path)
            logger.info(f"向量存储已备份: {backup_path}")

            # 记录备份元数据
            metadata = {
                "version": version,
                "timestamp": datetime.now().isoformat(),
                "source_path": source,
                "backup_path": backup_path,
            }
            metadata_path = os.path.join(self.BACKUP_DIR, "backup_history.json")
            history = []
            if os.path.exists(metadata_path):
                with open(metadata_path, "r", encoding="utf-8") as f:
                    history = json.load(f)
            history.append(metadata)
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)

            return backup_path

        except Exception as e:
            logger.error(f"备份失败: {e}")
            return ""

    def restore_vector_store(self, backup_path: str) -> bool:
        """从备份恢复向量存储"""
        source = LLMConfig.VECTOR_STORE_PATH

        if not os.path.exists(backup_path):
            logger.error(f"备份路径不存在: {backup_path}")
            return False

        try:
            if os.path.exists(source):
                shutil.rmtree(source)
            shutil.copytree(backup_path, source)
            logger.info(f"向量存储已从备份恢复: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"恢复失败: {e}")
            return False

    def run_regression_test(self) -> Dict[str, Any]:
        """运行回归测试"""
        logger.info("=" * 60)
        logger.info("开始知识库回归测试")
        logger.info("=" * 60)

        from app.llm.rag_agent import RAGAgent
        rag = RAGAgent()

        results = []
        passed = 0
        failed = 0

        for q in self.REGRESSION_QUERIES:
            try:
                retrieved = rag.search(q["query"], k=5)
                retrieved_text = " ".join([r.get("text", "") for r in retrieved]).lower()
                matched = sum(
                    1 for kw in q["expected_keywords"]
                    if kw.lower() in retrieved_text
                )
                recall = matched / len(q["expected_keywords"]) if q["expected_keywords"] else 0

                is_pass = recall >= 0.5  # 至少匹配50%的关键词
                if is_pass:
                    passed += 1
                else:
                    failed += 1

                results.append({
                    "query": q["query"],
                    "recall": recall,
                    "matched": matched,
                    "total": len(q["expected_keywords"]),
                    "passed": is_pass,
                })

            except Exception as e:
                logger.warning(f"回归测试失败 [{q['query']}]: {e}")
                failed += 1
                results.append({
                    "query": q["query"],
                    "recall": 0,
                    "matched": 0,
                    "total": len(q["expected_keywords"]),
                    "passed": False,
                    "error": str(e),
                })

        total = len(self.REGRESSION_QUERIES)
        pass_rate = passed / total if total > 0 else 0
        avg_recall = sum(r["recall"] for r in results) / len(results) if results else 0

        logger.info(f"回归测试结果: {passed}/{total} 通过 ({pass_rate:.2%})")
        logger.info(f"平均召回率: {avg_recall:.2%}")

        if failed > 0:
            logger.warning(f"失败查询 ({failed}条):")
            for r in results:
                if not r["passed"]:
                    logger.warning(f"  - {r['query']}: 召回率={r['recall']:.2%}")

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": pass_rate,
            "avg_recall": avg_recall,
            "details": results,
        }

    def safe_incremental_update(
        self, documents: List[Dict], recall_threshold: float = 0.70
    ) -> Dict[str, Any]:
        """
        安全的增量更新
        1. 备份当前知识库
        2. 执行增量更新
        3. 跑回归测试
        4. 召回率下降超过阈值则自动回滚
        """
        logger.info("=" * 60)
        logger.info("开始安全增量更新")
        logger.info("=" * 60)

        from app.llm.rag_agent import RAGAgent
        rag = RAGAgent()

        # 1. 更新前回归测试
        logger.info("步骤1: 更新前回归测试...")
        before_result = self.run_regression_test()
        before_recall = before_result["avg_recall"]
        logger.info(f"更新前召回率: {before_recall:.2%}")

        # 2. 备份
        logger.info("步骤2: 备份当前知识库...")
        version = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_vector_store(version)
        if not backup_path:
            logger.error("备份失败，取消更新")
            return {"success": False, "error": "备份失败"}

        # 3. 执行增量更新
        logger.info(f"步骤3: 执行增量更新 ({len(documents)}条文档)...")
        try:
            add_count = rag.add_documents(documents)
            logger.info(f"添加了 {add_count} 个文档块")
        except Exception as e:
            logger.error(f"增量更新失败: {e}")
            self.restore_vector_store(backup_path)
            return {"success": False, "error": str(e)}

        # 4. 更新后回归测试
        logger.info("步骤4: 更新后回归测试...")
        after_result = self.run_regression_test()
        after_recall = after_result["avg_recall"]
        logger.info(f"更新后召回率: {after_recall:.2%}")

        # 5. 判断是否需要回滚
        recall_decline = before_recall - after_recall
        if recall_decline > recall_threshold:
            logger.error(
                f"召回率下降 {recall_decline:.2%} > 阈值 {recall_threshold:.2%}，自动回滚！"
            )
            self.restore_vector_store(backup_path)
            return {
                "success": False,
                "error": f"召回率下降超出阈值 ({recall_decline:.2%})",
                "before_recall": before_recall,
                "after_recall": after_recall,
                "rollback": True,
            }

        logger.info(f"增量更新成功！召回率: {before_recall:.2%} → {after_recall:.2%}")
        return {
            "success": True,
            "before_recall": before_recall,
            "after_recall": after_recall,
            "documents_added": add_count,
            "backup_version": version,
        }

    def list_backups(self) -> List[Dict[str, Any]]:
        """列出所有备份"""
        metadata_path = os.path.join(self.BACKUP_DIR, "backup_history.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def get_stats(self) -> Dict[str, Any]:
        """获取知识库统计"""
        backups = self.list_backups()
        return {
            "backup_count": len(backups),
            "backup_dir": self.BACKUP_DIR,
            "latest_backup": backups[-1] if backups else None,
            "regression_queries": len(self.REGRESSION_QUERIES),
        }


def main():
    print("=" * 60)
    print("知识库增量更新回归验证 + 版本回滚")
    print("=" * 60)

    mgr = KnowledgeBaseManager()

    # 1. 显示当前状态
    stats = mgr.get_stats()
    print(f"\n当前状态:")
    print(f"  备份数量: {stats['backup_count']}")
    print(f"  备份目录: {stats['backup_dir']}")
    print(f"  回归查询: {stats['regression_queries']}条")
    if stats["latest_backup"]:
        print(f"  最新备份: {stats['latest_backup']['version']}")

    # 2. 运行回归测试
    print(f"\n运行回归测试...")
    result = mgr.run_regression_test()
    print(f"  通过率: {result['pass_rate']:.2%}")
    print(f"  平均召回率: {result['avg_recall']:.2%}")

    print(f"\n知识库版本管理模块就绪。")


if __name__ == "__main__":
    main()