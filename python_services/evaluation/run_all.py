"""
主评测入口脚本
运行所有评测模块，生成综合评测报告
"""
from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from evaluation.rag_eval import RAGEvaluator, main as rag_main
from evaluation.multimodal_eval import IntentRecognitionEvaluator, AISynthesisEvaluator
from evaluation.agent_eval import AgentReflectionEvaluator
from evaluation.risk_engine_eval import FraudClassifierEvaluator, PersuasionEvaluator
from evaluation.crawler_eval import CrawlerEvaluator
from evaluation.guardian_memory_test import GuardianNotificationTester, MemorySystemTester

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def run_all_evaluations():
    """运行全部评测"""
    print("=" * 80)
    print("AI反诈智能体平台 — 综合评测报告")
    print(f"评测时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    all_results = {
        "meta": {
            "timestamp": datetime.now().isoformat(),
            "version": "1.0",
        },
        "results": {},
    }

    # P1: RAG 评测
    print("\n" + "=" * 80)
    print("P1: RAG 检索增强生成评测")
    print("=" * 80)
    try:
        rag_evaluator = RAGEvaluator()
        rag_samples = rag_evaluator.load_test_data()
        rag_results = rag_evaluator.run_ablation(rag_samples)
        all_results["results"]["rag"] = {
            "ablation": rag_results,
            "sample_count": len(rag_samples),
        }
    except Exception as e:
        logger.error(f"RAG评测失败: {e}")
        all_results["results"]["rag"] = {"error": str(e)}

    # P2: 多模态识别评测
    print("\n" + "=" * 80)
    print("P2: 多模态识别评测")
    print("=" * 80)
    try:
        intent_evaluator = IntentRecognitionEvaluator()
        intent_samples = intent_evaluator.load_test_data()
        intent_result = intent_evaluator.evaluate(intent_samples)

        synthesis_evaluator = AISynthesisEvaluator()
        synthesis_samples = synthesis_evaluator.load_test_data()
        synthesis_result = synthesis_evaluator.evaluate(synthesis_samples)

        all_results["results"]["multimodal"] = {
            "intent_recognition": intent_result,
            "ai_synthesis_detection": synthesis_result,
        }
    except Exception as e:
        logger.error(f"多模态评测失败: {e}")
        all_results["results"]["multimodal"] = {"error": str(e)}

    # P3: Agent 评测
    print("\n" + "=" * 80)
    print("P3: Agent 反思机制与幻觉率评测")
    print("=" * 80)
    try:
        agent_evaluator = AgentReflectionEvaluator()
        risk_cases = agent_evaluator.load_risk_cases()
        reflection_result = agent_evaluator.evaluate_reflection(risk_cases)

        hallucination_cases = agent_evaluator.load_hallucination_cases()
        hallucination_result = agent_evaluator.evaluate_hallucination(hallucination_cases)

        all_results["results"]["agent"] = {
            "reflection": reflection_result,
            "hallucination": hallucination_result,
        }
    except Exception as e:
        logger.error(f"Agent评测失败: {e}")
        all_results["results"]["agent"] = {"error": str(e)}

    # P4: 风险引擎评测
    print("\n" + "=" * 80)
    print("P4: 风险引擎分类评测 + 话术接受度评估")
    print("=" * 80)
    try:
        classifier = FraudClassifierEvaluator()
        class_samples = classifier.load_test_data()
        class_result = classifier.evaluate(class_samples)

        persuasion = PersuasionEvaluator()
        persuasion_result = persuasion.evaluate()

        all_results["results"]["risk_engine"] = {
            "classification": class_result,
            "persuasion": persuasion_result,
        }
    except Exception as e:
        logger.error(f"风险引擎评测失败: {e}")
        all_results["results"]["risk_engine"] = {"error": str(e)}

    # P6: AI爬虫评测
    print("\n" + "=" * 80)
    print("P6: AI爬虫噪音过滤评测")
    print("=" * 80)
    try:
        crawler = CrawlerEvaluator()
        noise_samples = crawler.load_noise_test_data()
        noise_result = crawler.evaluate_noise_filter(noise_samples)
        breakpoint_result = crawler.test_breakpoint_resume()

        all_results["results"]["crawler"] = {
            "noise_filter": noise_result,
            "breakpoint_resume": breakpoint_result,
        }
    except Exception as e:
        logger.error(f"爬虫评测失败: {e}")
        all_results["results"]["crawler"] = {"error": str(e)}

    # P9: 监护人通知测试
    print("\n" + "=" * 80)
    print("P9: 监护人通知链路测试")
    print("=" * 80)
    try:
        guardian = GuardianNotificationTester()
        normal_result = guardian.test_normal_notification()
        abnormal_result = guardian.test_abnormal_scenario()

        all_results["results"]["guardian_notification"] = {
            "normal": normal_result,
            "abnormal": abnormal_result,
        }
    except Exception as e:
        logger.error(f"监护人通知测试失败: {e}")
        all_results["results"]["guardian_notification"] = {"error": str(e)}

    # P10: 记忆系统测试
    print("\n" + "=" * 80)
    print("P10: 记忆系统测试")
    print("=" * 80)
    try:
        memory = MemorySystemTester()
        short_term = memory.test_short_term_memory()
        long_term = memory.test_long_term_memory()
        update_test = memory.test_memory_update()

        all_results["results"]["memory_system"] = {
            "short_term": short_term,
            "long_term": long_term,
            "update": update_test,
        }
    except Exception as e:
        logger.error(f"记忆系统测试失败: {e}")
        all_results["results"]["memory_system"] = {"error": str(e)}

    return all_results


def print_summary(results: dict):
    """打印评测摘要"""
    print("\n\n" + "=" * 80)
    print("评测摘要")
    print("=" * 80)

    results_dir = Path(__file__).parent / "results"
    if not results_dir.is_dir():
        print("  - 尚无评测产物，请先运行各评测脚本")
        print("=" * 80)
        return

    for path in sorted(results_dir.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  - {path.name}: 读取失败（{e}）")
            continue

        metrics = payload.get("metrics") or {}
        measured = {k: v for k, v in metrics.items() if isinstance(v, (int, float))}
        missing = sorted(k for k, v in metrics.items() if v is None)
        name = payload.get("eval", path.stem)
        print(f"  - {name}: 已测 {len(measured)} 项 / 数据不足 {len(missing)} 项")
        for key, value in sorted(measured.items()):
            print(f"      {key} = {value}")
        if missing:
            print(f"      数据不足: {', '.join(missing)}")

    print("=" * 80)


def main():
    results = run_all_evaluations()

    # 保存综合报告
    output_path = os.path.join(
        os.path.dirname(__file__), "test_data", "comprehensive_eval_report.json"
    )
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n综合评测报告已保存到: {output_path}")

    # 打印摘要
    print_summary(results)

    print("\n全部评测完成！")


if __name__ == "__main__":
    main()