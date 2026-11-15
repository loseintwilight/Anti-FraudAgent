"""
风险引擎分类评测 + 话术接受度评估
分类准确率对固定标注样本做确定性计算；话术接受度对照结论无原始日志时记为数据不足。
"""
from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class FraudClassifierEvaluator:
    """诈骗分类评测器"""

    # 6大类诈骗关键词规则
    TYPE_KEYWORDS = {
        "刷单返利": ["刷单", "刷信誉", "返佣金", "做任务", "点赞", "兼职群", "会员费", "VIP", "日结", "垫资", "交保证金", "佣金", "抖音点赞"],
        "虚假投资": ["投资", "日收益", "年化", "保本", "稳赚", "炒", "理财", "数字货币", "外汇", "回本", "返利", "养老", "投资项目", "内部消息", "老师", "股票"],
        "冒充公检法": ["公安局", "检察院", "法院", "涉嫌", "洗钱", "通缉令", "传票", "安全账户", "冻结", "配合调查", "警官证", "医保卡", "社保", "反诈中心"],
        "杀猪盘": ["网恋", "交往", "一见钟情", "婚恋", "聊天后", "网恋对象", "网恋男友", "网恋女友", "网上认识", "条件很好", "美女", "异性", "恋爱", "确定关系", "国外"],
        "客服退款": ["快递", "退款", "客服", "订单", "淘宝", "会员", "验证码", "退款申请", "退货", "运费", "包裹", "赔偿", "商家", "商品", "退款操作"],
        "虚假贷款": ["贷款", "无抵押", "利息低", "手续费", "解冻", "银行卡号", "还款能力", "放款", "额度", "申请", "网贷", "保险金", "征信", "验资", "贷款APP"],
    }

    def __init__(self):
        self.results: List[Dict[str, Any]] = []

    def load_test_data(self, path: str = None) -> List[Dict[str, Any]]:
        if path is None:
            path = os.path.join(
                os.path.dirname(__file__), "test_data", "fraud_classification.json"
            )
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["samples"]

    def predict_type(self, scenario: str) -> str:
        """基于关键词规则预测诈骗类型"""
        scores = {}
        for fraud_type, keywords in self.TYPE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in scenario)
            if score > 0:
                scores[fraud_type] = score

        if not scores:
            return "非诈骗"

        return max(scores, key=scores.get)

    def evaluate(self, samples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """评测分类准确率"""
        logger.info("=" * 60)
        logger.info("开始诈骗分类评测")
        logger.info("=" * 60)

        class_stats = {}
        confusion = {}
        correct = 0
        total = 0
        bad_cases = []

        for sample in samples:
            scenario = sample["scenario"]
            true_type = sample["true_type"]

            predicted = self.predict_type(scenario)
            is_correct = predicted == true_type
            total += 1
            if is_correct:
                correct += 1

            if true_type not in class_stats:
                class_stats[true_type] = {"tp": 0, "fp": 0, "fn": 0, "total": 0}
            class_stats[true_type]["total"] += 1
            if is_correct:
                class_stats[true_type]["tp"] += 1
            else:
                class_stats[true_type]["fn"] += 1
                if predicted not in class_stats:
                    class_stats[predicted] = {"tp": 0, "fp": 0, "fn": 0, "total": 0}
                class_stats[predicted]["fp"] += 1

            key = f"{true_type}->{predicted}"
            confusion[key] = confusion.get(key, 0) + 1

            if not is_correct:
                bad_cases.append({
                    "id": sample["id"],
                    "scenario": scenario,
                    "true_type": true_type,
                    "predicted": predicted,
                    "difficulty": sample.get("difficulty", "easy"),
                })

        accuracy = correct / total if total > 0 else 0

        logger.info(f"总样本: {total}, 正确: {correct}, 准确率: {accuracy:.2%}")

        class_report = {}
        for cls, stats in sorted(class_stats.items()):
            tp = stats["tp"]
            fp = stats["fp"]
            fn = stats["fn"]
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            class_report[cls] = {"precision": precision, "recall": recall, "f1": f1, "total": stats["total"]}
            logger.info(f"  {cls}: P={precision:.2%} R={recall:.2%} F1={f1:.2%} ({stats['total']}条)")

        logger.info(f"Bad Case ({len(bad_cases)}条)")

        return {
            "task": "诈骗分类评测",
            "accuracy": accuracy,
            "total": total,
            "correct": correct,
            "class_report": class_report,
            "confusion_matrix": confusion,
            "bad_cases": bad_cases,
        }


class PersuasionEvaluator:
    """话术接受度评估器"""

    def __init__(self):
        self.scenarios = [
            {"id": "ps_001", "type": "刷单返利", "age_group": "青年", "scenario": "做了几天任务赚了几百块，现在让升级VIP"},
            {"id": "ps_002", "type": "冒充公检法", "age_group": "老年", "scenario": "有人打电话说是公安局的，说我涉嫌洗钱"},
            {"id": "ps_003", "type": "杀猪盘", "age_group": "中年", "scenario": "网恋男友说在国外的投资平台有漏洞能赚钱"},
            {"id": "ps_004", "type": "虚假投资", "age_group": "老年", "scenario": "有人推荐了一个投资平台，日收益10%"},
            {"id": "ps_005", "type": "虚假贷款", "age_group": "青年", "scenario": "急需用钱，在网上下载了一个贷款APP"},
            {"id": "ps_006", "type": "客服退款", "age_group": "中年", "scenario": "客服说退款需要验证我的银行卡信息"},
            {"id": "ps_007", "type": "冒充公检法", "age_group": "老年", "scenario": "检察院说我的银行卡涉嫌犯罪需要冻结"},
            {"id": "ps_008", "type": "刷单返利", "age_group": "青年", "scenario": "兼职群说帮商家刷信誉，一单20元"},
            {"id": "ps_009", "type": "杀猪盘", "age_group": "中年", "scenario": "认识了一个条件很好的异性，很快确定关系，然后提到投资"},
            {"id": "ps_010", "type": "虚假投资", "age_group": "老年", "scenario": "养老投资，每个月返利，三年回本"},
            {"id": "ps_011", "type": "虚假贷款", "age_group": "青年", "scenario": "贷款APP审批通过了，但要先交手续费"},
            {"id": "ps_012", "type": "客服退款", "age_group": "中年", "scenario": "淘宝客服说我的会员需要续费，否则会扣款"},
        ]

    def evaluate(self) -> Dict[str, Any]:
        """话术接受度评估：无 A/B 对照实验原始日志，结论指标记为数据不足。"""
        logger.info("=" * 60)
        logger.info("话术接受度评估（固定场景概况统计）")
        logger.info("=" * 60)

        age_distribution: Dict[str, int] = {}
        type_distribution: Dict[str, int] = {}
        for s in self.scenarios:
            age = s.get("age_group", "unknown")
            typ = s.get("type", "unknown")
            age_distribution[age] = age_distribution.get(age, 0) + 1
            type_distribution[typ] = type_distribution.get(typ, 0) + 1

        logger.info(f"固定场景: {len(self.scenarios)} 条")
        logger.info("接受度评分与提升等对照结论: 数据不足（无原始实验日志）")

        return {
            "task": "话术接受度评估",
            "standard_avg": None,
            "personalized_avg": None,
            "improvement": None,
            "scenarios_count": len(self.scenarios),
            "status": "数据不足",
            "reason": "无标准模板与人群差异化话术的 A/B 对照实验原始评分日志，不填充任何评分或提升值",
            "sample_profile": {
                "age_group_distribution": age_distribution,
                "fraud_type_distribution": type_distribution,
            },
        }


def _write_results(all_results: Dict[str, Any]) -> None:
    results_dir = Path(__file__).resolve().parent / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    output_path = results_dir / "risk_engine_eval.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, sort_keys=True)
    print(f"\n评测产物已写入: {output_path}")


def main():
    print("=" * 80)
    print("风险引擎分类评测 + 话术接受度评估")
    print("=" * 80)

    classifier = FraudClassifierEvaluator()
    samples = classifier.load_test_data()
    classification_results = classifier.evaluate(samples)

    print(f"\n分类评测结果: 准确率 {classification_results['accuracy']:.2%}")

    persuasion = PersuasionEvaluator()
    persuasion_results = persuasion.evaluate()

    print(f"\n话术接受度评估: 提升 数据不足（{persuasion_results['reason']}）")

    insufficient = {
        "persuasion_standard_avg": persuasion_results["reason"],
        "persuasion_personalized_avg": persuasion_results["reason"],
        "persuasion_improvement": persuasion_results["reason"],
    }

    all_results = {
        "schema_version": "1.0",
        "eval": "risk_engine_eval",
        "source_files": ["test_data/fraud_classification.json"],
        "method": (
            "诈骗分类按关键词规则对固定标注样本做确定性计算；"
            "话术接受度 A/B 对照结论无原始实验日志支撑，指标记为 null 并标注数据不足"
        ),
        "metrics": {
            "fraud_classification_accuracy": round(classification_results["accuracy"], 6),
            "persuasion_standard_avg": None,
            "persuasion_personalized_avg": None,
            "persuasion_improvement": None,
        },
        "details": {
            "classification": classification_results,
            "persuasion": persuasion_results,
        },
        "insufficient": insufficient,
    }
    _write_results(all_results)


if __name__ == "__main__":
    main()
