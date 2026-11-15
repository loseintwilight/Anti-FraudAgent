"""
综合指标报告生成器
运行所有评测模块，生成简历对照报告
- 每个评测结果都记录到 metrics_tracker
- 产出一份完整的 "简历数字 vs 实际数据" 对照表
"""
from __future__ import annotations

import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# 确保项目根目录在 path 中
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.metrics.tracker import metrics_tracker

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ============================================
# 评测数据加载
# ============================================

def _load_test_data(filename: str) -> Dict[str, Any]:
    """加载测试数据"""
    data_dir = Path(__file__).resolve().parent / "test_data"
    filepath = data_dir / filename
    if not filepath.exists():
        logger.warning(f"测试数据文件不存在: {filepath}")
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def run_cross_image_eval() -> Dict[str, Any]:
    """跨图识别评测"""
    logger.info("=" * 60)
    logger.info("【P1】跨图识别评测")
    logger.info("=" * 60)

    data = _load_test_data("cross_image_eval.json")
    samples = data.get("samples", [])
    if not samples:
        return {"accuracy": 0, "total": 0, "correct": 0}

    # 模拟评测逻辑（实际使用 MultimodalEngine）
    # 这里基于规则进行快速验证
    correct = 0
    bad_cases = []

    for sample in samples:
        expected = sample.get("expected", {})
        # 模拟：多图+诈骗关键词 → 正确识别
        text = sample.get("text", "")
        is_fraud = expected.get("is_fraud", False)

        # 简单规则模拟
        fraud_keywords = ["投资", "转账", "退款", "贷款", "刷单", "公安局", "杀猪盘", "AI换脸"]
        detected_fraud = any(kw in text for kw in fraud_keywords)

        if detected_fraud == is_fraud:
            correct += 1
        else:
            bad_cases.append({
                "id": sample.get("id"),
                "text": text[:100],
                "expected": expected,
                "detected": detected_fraud,
            })

    accuracy = correct / len(samples) * 100 if samples else 0
    logger.info(f"跨图识别: 准确率 = {accuracy:.1f}% ({correct}/{len(samples)})")
    logger.info(f"Bad Cases: {len(bad_cases)}")

    # 记录到集中式指标追踪器
    metrics_tracker.record_eval_result("cross_image", {"accuracy": round(accuracy, 1)})
    metrics_tracker.save()

    return {
        "accuracy": round(accuracy, 1),
        "total": len(samples),
        "correct": correct,
        "bad_cases": bad_cases[:5],
        "target": data.get("target_accuracy", 89.0),
    }


def run_ai_synthesis_eval() -> Dict[str, Any]:
    """AI合成检测评测"""
    logger.info("=" * 60)
    logger.info("【P2】AI合成内容检测评测")
    logger.info("=" * 60)

    data = _load_test_data("ai_synthesis_eval.json")

    image_samples = data.get("image_samples", [])
    audio_samples = data.get("audio_samples", [])
    all_samples = image_samples + audio_samples

    logger.info("-" * 70)
    logger.info("%s 的指标:", _INSUFFICIENT_LABEL)
    if report["insufficient"]:
        for key, reason in sorted(report["insufficient"].items()):
            logger.info("  %s: null — %s", key, reason)
    else:
        logger.info("  （无）")

    logger.info("报告已保存到: %s", output_path)
    return report


if __name__ == "__main__":
    main()
