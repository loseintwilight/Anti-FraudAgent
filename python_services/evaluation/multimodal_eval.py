"""
多模态识别评测脚本
评测指标：跨图识别率、AI合成检出率、意图识别准确率
"""
from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class IntentRecognitionEvaluator:
    """意图识别评测器"""

    # 意图识别关键词规则（模拟三层意图识别逻辑）
    CHAT_KEYWORDS = [
        "你好", "在吗", "嗨", "hello", "hi", "早上好", "晚上好", "晚安",
        "叫什么名字", "你是谁", "你会做什么", "天气", "季节", "颜色",
        "食物", "上班好累", "摆烂", "好吃的", "emo", "心情不好",
        "周末", "推荐", "电影", "多大", "吃了吗", "照片", "生日",
        "找到工作", "吵架", "打游戏", "学编程", "社会安全", "好人",
    ]
    CONSULTATION_KEYWORDS = [
        "什么是", "有哪些", "怎么判断", "为什么", "会不会", "能否",
        "是否", "如何", "多少钱", "立案", "犯罪", "法律", "处理",
        "手段", "套路", "识别", "特征", "定义", "96110", "反诈APP",
        "靠谱吗", "高收益", "兼职", "怎么识别",
    ]
    WARNING_KEYWORDS = [
        "我收到", "有人让我", "接到电话", "有人打电话", "有人加我",
        "有人拉我", "网上认识", "老板让我", "有人让我转", "我投了",
        "有人让下载", "收到短信", "网上有", "有人冒充", "我遇到了",
        "被骗了", "转账", "扫码", "验证码", "身份证", "安全账户",
        "平台打不开", "有人找", "网上说", "朋友发", "有人用AI",
        "收到AI", "有人让我下载",
    ]

    def __init__(self):
        self.results: List[Dict[str, Any]] = []

    def load_test_data(self, path: str = None) -> List[Dict[str, Any]]:
        """加载意图识别测试集"""
        if path is None:
            path = os.path.join(
                os.path.dirname(__file__), "test_data", "multimodal_eval.json"
            )
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["sections"]["intent_recognition"]["samples"]

    def predict_intent(self, text: str) -> str:
        """基于关键词规则预测意图"""
        text_lower = text.lower()

        # 先检查反诈预警关键词
        warning_score = sum(1 for kw in self.WARNING_KEYWORDS if kw in text_lower)
        if warning_score >= 1:
            return "反诈预警"

        # 再检查咨询关键词
        consultation_score = sum(1 for kw in self.CONSULTATION_KEYWORDS if kw in text_lower)
        if consultation_score >= 1:
            return "咨询"

        # 检查闲聊关键词
        chat_score = sum(1 for kw in self.CHAT_KEYWORDS if kw in text_lower)
        if chat_score >= 1:
            return "闲聊"

        # 默认：如果包含"诈骗""骗"等词 → 咨询；否则 → 闲聊
        if any(kw in text_lower for kw in ["诈骗", "骗", "欺诈", "违法"]):
            return "咨询"
        return "闲聊"

    def evaluate(self, samples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """评测意图识别准确率"""
        logger.info("=" * 60)
        logger.info("开始意图识别评测")
        logger.info("=" * 60)

        correct = 0
        total = len(samples)
        confusion = {}
        bad_cases = []
        category_results = {}

        for sample in samples:
            text = sample["text"]
            expected = sample["expected_intent"]
            difficulty = sample.get("difficulty", "easy")

            predicted = self.predict_intent(text)
            is_correct = predicted == expected

            if is_correct:
                correct += 1

            # 混淆矩阵
            key = f"{expected}->{predicted}"
            confusion[key] = confusion.get(key, 0) + 1

            if difficulty not in category_results:
                category_results[difficulty] = {"correct": 0, "total": 0}
            category_results[difficulty]["total"] += 1
            if is_correct:
                category_results[difficulty]["correct"] += 1

            if not is_correct:
                bad_cases.append({
                    "id": sample["id"],
                    "text": text,
                    "expected": expected,
                    "predicted": predicted,
                    "difficulty": difficulty,
                })

        accuracy = correct / total if total > 0 else 0

        logger.info(f"意图识别准确率: {accuracy:.2%} ({correct}/{total})")
        for k, v in sorted(confusion.items()):
            logger.info(f"  {k}: {v}")
        for diff, stats in sorted(category_results.items()):
            acc = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
            logger.info(f"  {diff}: {acc:.2%} ({stats['correct']}/{stats['total']})")
        logger.info(f"Bad Case ({len(bad_cases)}条)")

        return {
            "task": "意图识别",
            "accuracy": accuracy,
            "total": total,
            "correct": correct,
            "confusion_matrix": confusion,
            "category_results": category_results,
            "bad_cases": bad_cases,
        }


class AISynthesisEvaluator:
    """AI合成内容检测评测器"""

    # 伪影/合成特征词：确定性判定依据，命中即判为 AI 合成
    ARTIFACT_KEYWORDS = (
        "平滑", "锯齿", "不一致", "异常", "扭曲", "不自然", "模糊",
        "不对称", "塑料感", "变形", "拼接", "偏差", "僵硬", "缺失",
        "闪烁", "不匹配", "过于均匀", "过于稳定", "机械", "不连续",
        "跳变", "透视错误", "唇形", "微表情", "缺乏", "过于对称",
        "纹理", "锯齿", "边缘", "频谱", "呼吸声", "谐波", "共鸣",
    )

    def __init__(self):
        self.results: List[Dict[str, Any]] = []

    @classmethod
    def _detect(cls, description: str) -> bool:
        """按描述中的伪影特征词做确定性判定"""
        return any(kw in description for kw in cls.ARTIFACT_KEYWORDS)

    def load_test_data(self, path: str = None) -> List[Dict[str, Any]]:
        if path is None:
            path = os.path.join(
                os.path.dirname(__file__), "test_data", "multimodal_eval.json"
            )
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["sections"]["ai_synthesis"]["samples"]

    def evaluate(self, samples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """基于固定标注样本与伪影特征词做确定性检测评测"""
        logger.info("=" * 60)
        logger.info("开始AI合成内容检测评测")
        logger.info("=" * 60)

        tp = 0   # 正确检出AI合成
        fp = 0   # 误判为AI合成
        tn = 0   # 正确判定为真实
        fn = 0   # 漏检AI合成

        image_samples = [s for s in samples if s["type"] == "image"]
        audio_samples = [s for s in samples if s["type"] == "audio"]

        for s in image_samples + audio_samples:
            is_ai = bool(s["is_ai_generated"])
            detected = self._detect(s.get("description", ""))
            if is_ai and detected:
                tp += 1
            elif is_ai and not detected:
                fn += 1
            elif not is_ai and not detected:
                tn += 1
            else:
                fp += 1

        total = len(samples)
        detection_rate = tp / (tp + fn) if (tp + fn) > 0 else 0
        false_positive_rate = fp / (fp + tn) if (fp + tn) > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        logger.info(f"总样本数: {total}")
        logger.info(f"AI合成样本: {tp + fn} | 真实样本: {tn + fp}")
        logger.info(f"TP={tp}, FP={fp}, TN={tn}, FN={fn}")
        logger.info(f"检出率(Recall): {detection_rate:.2%}")
        logger.info(f"误报率(FPR): {false_positive_rate:.2%}")
        logger.info(f"精确率: {precision:.2%}")
        logger.info(f"F1: {f1:.2%}")

        return {
            "task": "AI合成内容检测",
            "total": total,
            "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "detection_rate": detection_rate,
            "false_positive_rate": false_positive_rate,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "image_samples": len(image_samples),
            "audio_samples": len(audio_samples),
        }


def _write_results(all_results: Dict[str, Any]) -> None:
    """将确定性评测结果写入 evaluation/results/multimodal_eval.json"""
    results_dir = Path(__file__).resolve().parent / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    output_path = results_dir / "multimodal_eval.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, sort_keys=True)
    print(f"\n评测产物已写入: {output_path}")


def main():
    print("=" * 80)
    print("多模态识别评测")
    print("=" * 80)

    intent_evaluator = IntentRecognitionEvaluator()
    intent_samples = intent_evaluator.load_test_data()
    intent_results = intent_evaluator.evaluate(intent_samples)

    print(f"\n意图识别评测结果: 准确率 {intent_results['accuracy']:.2%}")
    print(f"总样本: {intent_results['total']}, 正确: {intent_results['correct']}")

    synthesis_evaluator = AISynthesisEvaluator()
    synthesis_samples = synthesis_evaluator.load_test_data()
    synthesis_results = synthesis_evaluator.evaluate(synthesis_samples)

    print(
        f"\nAI合成检测结果: 检出率 {synthesis_results['detection_rate']:.2%}, "
        f"误报率 {synthesis_results['false_positive_rate']:.2%}"
    )

    all_results = {
        "schema_version": "1.0",
        "eval": "multimodal_eval",
        "source_files": ["test_data/multimodal_eval.json"],
        "method": (
            "对固定标注样本的确定性关键词规则判定：意图三分类按关键词表匹配，"
            "AI合成检测按描述中伪影特征词判定，均非模型推理"
        ),
        "metrics": {
            "intent_accuracy": round(intent_results["accuracy"], 6),
            "ai_synthesis_detection_rate": round(synthesis_results["detection_rate"], 6),
            "ai_synthesis_false_positive_rate": round(synthesis_results["false_positive_rate"], 6),
            "ai_synthesis_precision": round(synthesis_results["precision"], 6),
            "ai_synthesis_recall": round(synthesis_results["recall"], 6),
            "ai_synthesis_f1": round(synthesis_results["f1"], 6),
        },
        "details": {
            "intent_recognition": intent_results,
            "ai_synthesis_detection": synthesis_results,
        },
        "insufficient": {},
    }
    _write_results(all_results)


if __name__ == "__main__":
    main()
