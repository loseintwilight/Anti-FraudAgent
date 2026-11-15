"""
综合指标报告
读取 evaluation/results/ 下的评测产物，只呈现其中真实存在的结果，
对产物中标注为数据不足的指标集中说明。
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RESULTS_DIR = Path(__file__).resolve().parent / "results"
_REPORT_FILENAME = "metrics_report.json"
_INSUFFICIENT_LABEL = "数据不足"


def _load_artifacts() -> Dict[str, Dict[str, Any]]:
    """读取所有评测产物（不含报告自身），仅收录含 metrics 字典的文件。"""
    artifacts: Dict[str, Dict[str, Any]] = {}
    if not RESULTS_DIR.is_dir():
        return artifacts
    for path in sorted(RESULTS_DIR.glob("*.json")):
        if path.name == _REPORT_FILENAME:
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError) as e:
            logger.warning("评测产物读取失败: %s (%s)", path.name, e)
            continue
        if isinstance(data, dict) and isinstance(data.get("metrics"), dict):
            artifacts[path.name] = data
    return artifacts


def generate_report() -> Dict[str, Any]:
    """汇总评测产物：呈现真实结果，标注数据不足的指标。"""
    artifacts = _load_artifacts()
    all_metrics: Dict[str, Any] = {}
    sections: Dict[str, Any] = {}
    insufficient: Dict[str, str] = {}

    for name, data in artifacts.items():
        metrics = data["metrics"]
        all_metrics.update(metrics)
        sections[name] = {
            "eval": data.get("eval", name),
            "source_files": data.get("source_files", []),
            "method": data.get("method", ""),
            "metrics": metrics,
        }
        reasons = data.get("insufficient")
        if isinstance(reasons, dict):
            for key, reason in reasons.items():
                if isinstance(reason, str):
                    insufficient[key] = reason

    measured = {k: v for k, v in all_metrics.items() if v is not None}
    for key, value in all_metrics.items():
        if value is None:
            insufficient.setdefault(
                key, "评测产物中该指标为 null，无原始实验日志支撑"
            )

    return {
        "schema_version": "1.0",
        "type": "report",
        "measured": measured,
        "insufficient": insufficient,
        "insufficient_label": _INSUFFICIENT_LABEL,
        "sections": sections,
        "sources": sorted(artifacts.keys()),
    }


def main() -> Dict[str, Any]:
    report = generate_report()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RESULTS_DIR / _REPORT_FILENAME
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, sort_keys=True)

    logger.info("=" * 70)
    logger.info("综合指标报告（仅呈现评测产物中真实存在的结果）")
    logger.info("=" * 70)
    logger.info("数据来源: %s", ", ".join(report["sources"]) or "（无产物）")
    for key, value in sorted(report["measured"].items()):
        logger.info("  %s = %s", key, value)

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
