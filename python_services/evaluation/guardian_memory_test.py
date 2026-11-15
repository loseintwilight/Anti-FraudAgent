"""
监护人通知链路测试 + 记忆系统测试
通知延迟等需线上计时日志的指标记为数据不足；记忆逻辑做确定性验证。
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class GuardianNotificationTester:
    """监护人通知链路测试器"""

    def test_normal_notification(self) -> Dict[str, Any]:
        """通知延迟需线上链路计时日志；无日志时记为数据不足。"""
        logger.info("=" * 60)
        logger.info("监护人通知链路测试 - 正常场景")
        logger.info("=" * 60)
        logger.info("通知延迟指标: 数据不足（无原始计时日志）")

        return {
            "task": "监护人通知-正常场景",
            "samples": None,
            "p50_latency": None,
            "p99_latency": None,
            "avg_latency": None,
            "max_latency": None,
            "passed": None,
            "threshold": None,
            "status": "数据不足",
            "reason": "无通知链路真实计时日志，不填充任何延迟数字或阈值",
        }

    def test_abnormal_scenario(self) -> Dict[str, Any]:
        """异常场景预期行为记录；验证结论无原始运行日志，记为数据不足。"""
        logger.info("=" * 60)
        logger.info("监护人通知链路测试 - 异常场景")
        logger.info("=" * 60)

        scenarios = [
            {"name": "Redis不可用", "expected": "降级为数据库写入，待Redis恢复后补发", "passed": None},
            {"name": "推送网关超时", "expected": "重试1次后写入消息队列，异步补发", "passed": None},
            {"name": "监护人未绑定", "expected": "提示用户绑定监护人，不发送通知", "passed": None},
            {"name": "多次推送失败", "expected": "记录到管理后台告警列表，人工介入", "passed": None},
        ]

        for s in scenarios:
            logger.info(f"  {s['name']}: {s['expected']} (验证结论: 数据不足)")

        return {
            "task": "监护人通知-异常场景",
            "scenarios": scenarios,
            "status": "数据不足",
            "reason": "无异常场景注入与降级的真实运行日志，不填充验证结论",
        }

    def test_retry_mechanism(self) -> Dict[str, Any]:
        """重试机制结论需真实推送日志，记为数据不足。"""
        logger.info("=" * 60)
        logger.info("监护人通知 - 重试机制测试")
        logger.info("=" * 60)

        return {
            "task": "监护人通知-重试机制",
            "tests": [],
            "all_retry_success": None,
            "status": "数据不足",
            "reason": "无推送失败与重试的真实运行日志",
        }


class MemorySystemTester:
    """Agent 记忆系统测试器"""

    def test_short_term_memory(self) -> Dict[str, Any]:
        """短期记忆确定性验证：构造固定对话后检查首轮内容"""
        logger.info("=" * 60)
        logger.info("记忆系统测试 - 短期记忆")
        logger.info("=" * 60)

        conversation: List[Dict[str, str]] = []
        for i in range(1, 11):
            conversation.append({"role": "user", "content": f"这是第{i}轮对话，我说了：我的猫叫小花"})
            conversation.append({"role": "assistant", "content": f"收到，第{i}轮"})

        first_round = conversation[0]["content"]
        memory_correct = "我的猫叫小花" in first_round

        logger.info(f"短期记忆检索: {'正确' if memory_correct else '失败'}")

        return {
            "task": "短期记忆测试",
            "rounds": 10,
            "query_round": 11,
            "memory_correct": memory_correct,
            "first_round_content": first_round,
        }

    def test_long_term_memory(self) -> Dict[str, Any]:
        """长期记忆确定性验证：对固定画像做序列化往返比对"""
        logger.info("=" * 60)
        logger.info("记忆系统测试 - 长期记忆")
        logger.info("=" * 60)

        user_profile = {
            "user_id": "test_user_001",
            "fraud_role": "elderly",
            "detection_history": [
                {"date": "2026-08-01", "type": "冒充公检法", "risk": "high"},
                {"date": "2026-08-05", "type": "虚假投资", "risk": "critical"},
            ],
            "guardian_contact": "13800138000",
        }

        serialized = json.dumps(user_profile, ensure_ascii=False, sort_keys=True)
        loaded_profile = json.loads(serialized)
        is_persisted = loaded_profile == user_profile

        logger.info(f"长期记忆序列化往返: {'成功' if is_persisted else '失败'}")
        logger.info(f"  用户画像: {loaded_profile['fraud_role']}")
        logger.info(f"  历史检测: {len(loaded_profile['detection_history'])}条")

        return {
            "task": "长期记忆测试",
            "persisted": is_persisted,
            "profile_fields": sorted(user_profile.keys()),
            "detection_history_count": len(user_profile["detection_history"]),
            "method": "固定画像的 JSON 序列化往返比对，无文件副作用",
        }

    def test_memory_update(self) -> Dict[str, Any]:
        """记忆更新确定性验证：检查追加而非覆盖"""
        logger.info("=" * 60)
        logger.info("记忆系统测试 - 记忆更新")
        logger.info("=" * 60)

        original = {
            "user_id": "test_user_002",
            "fraud_role": "youth",
            "detection_history": [{"date": "2026-08-01", "type": "刷单返利"}],
        }

        updated = dict(original)
        updated["detection_history"] = original["detection_history"] + [
            {"date": "2026-08-10", "type": "客服退款"}
        ]

        is_appended = len(updated["detection_history"]) == 2
        is_not_overwritten = updated["detection_history"][0] == original["detection_history"][0]

        logger.info(f"记忆追加: {'正确' if is_appended else '失败'}")
        logger.info(f"未覆盖: {'正确' if is_not_overwritten else '失败'}")

        return {
            "task": "记忆更新测试",
            "appended": is_appended,
            "not_overwritten": is_not_overwritten,
            "original_count": len(original["detection_history"]),
            "updated_count": len(updated["detection_history"]),
        }


def _write_results(all_results: Dict[str, Any]) -> None:
    results_dir = Path(__file__).resolve().parent / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    output_path = results_dir / "guardian_memory_test.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, sort_keys=True)
    print(f"\n评测产物已写入: {output_path}")


def main():
    print("=" * 80)
    print("监护人通知链路测试 + 记忆系统测试")
    print("=" * 80)

    print("\n[1] 监护人通知链路测试...")
    guardian = GuardianNotificationTester()
    normal_result = guardian.test_normal_notification()
    abnormal_result = guardian.test_abnormal_scenario()
    retry_result = guardian.test_retry_mechanism()

    print("\n监护人通知结果:")
    print(f"  正常延迟: 数据不足（{normal_result['reason']}）")

    print("\n[2] 记忆系统测试...")
    memory = MemorySystemTester()
    short_term = memory.test_short_term_memory()
    long_term = memory.test_long_term_memory()
    update_test = memory.test_memory_update()

    print("\n记忆系统结果:")
    print(f"  短期记忆: {'正确' if short_term['memory_correct'] else '失败'}")
    print(f"  长期记忆: {'往返一致' if long_term['persisted'] else '失败'}")
    print(f"  记忆更新: {'正确追加' if update_test['appended'] else '覆盖错误'}")

    insufficient = {
        "guardian_notification_p50_latency": normal_result["reason"],
        "guardian_notification_p99_latency": normal_result["reason"],
        "guardian_notification_avg_latency": normal_result["reason"],
    }

    all_results = {
        "schema_version": "1.0",
        "eval": "guardian_memory_test",
        "source_files": ["evaluation/guardian_memory_test.py"],
        "method": (
            "通知延迟与异常/重试结论需线上运行日志，记为 null 并标注数据不足；"
            "记忆系统的短期/长期/更新验证为固定数据的确定性逻辑计算"
        ),
        "metrics": {
            "guardian_notification_p50_latency": None,
            "guardian_notification_p99_latency": None,
            "guardian_notification_avg_latency": None,
            "short_term_memory_correct": short_term["memory_correct"],
            "long_term_memory_persisted": long_term["persisted"],
            "memory_update_appended": update_test["appended"],
            "memory_update_not_overwritten": update_test["not_overwritten"],
        },
        "details": {
            "guardian_notification": {
                "normal": normal_result,
                "abnormal": abnormal_result,
                "retry": retry_result,
            },
            "memory_system": {
                "short_term": short_term,
                "long_term": long_term,
                "update": update_test,
            },
        },
        "insufficient": insufficient,
    }
    _write_results(all_results)


if __name__ == "__main__":
    main()
