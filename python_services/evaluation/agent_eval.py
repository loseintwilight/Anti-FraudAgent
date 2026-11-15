"""
Agent 反思机制评测 + 幻觉率评测
固定样本概况做确定性统计；对照实验类结论无原始日志支撑时记为数据不足。
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


class AgentReflectionEvaluator:
    """Agent 反思机制评测器"""

    def load_risk_cases(self) -> List[Dict[str, Any]]:
        """加载风险判定固定样本"""
        return [
            {"id": "rc_001", "scenario": "有人让我下载APP投资，承诺日收益20%", "true_risk": "high", "true_type": "虚假投资", "correct_judgment": True},
            {"id": "rc_002", "scenario": "收到短信称ETC过期需重新认证", "true_risk": "high", "true_type": "钓鱼链接", "correct_judgment": True},
            {"id": "rc_003", "scenario": "网上认识的人说带我赚钱，先让我转1000元", "true_risk": "high", "true_type": "杀猪盘", "correct_judgment": True},
            {"id": "rc_004", "scenario": "自称警察的人打电话说涉嫌洗钱要转账自证清白", "true_risk": "critical", "true_type": "冒充公检法", "correct_judgment": True},
            {"id": "rc_005", "scenario": "孩子班级群里有老师让交资料费", "true_risk": "mid", "true_type": "冒充老师", "correct_judgment": True},
            {"id": "rc_006", "scenario": "二手平台买家说付款失败让扫码", "true_risk": "high", "true_type": "交易诈骗", "correct_judgment": True},
            {"id": "rc_007", "scenario": "有人打电话说航班取消需改签退费", "true_risk": "mid", "true_type": "航班诈骗", "correct_judgment": True},
            {"id": "rc_008", "scenario": "收到贷款APP要交手续费才能放款", "true_risk": "high", "true_type": "虚假贷款", "correct_judgment": True},
            {"id": "rc_009", "scenario": "健康讲座推销保健品称能治百病", "true_risk": "mid", "true_type": "保健品诈骗", "correct_judgment": True},
            {"id": "rc_010", "scenario": "有人用AI换脸视频通话要借钱", "true_risk": "critical", "true_type": "AI换脸诈骗", "correct_judgment": True},
            {"id": "rc_011", "scenario": "收到AI合成语音说家人出事需汇款", "true_risk": "critical", "true_type": "AI拟声诈骗", "correct_judgment": True},
            {"id": "rc_012", "scenario": "微信群有人发红包链接让点击领取", "true_risk": "high", "true_type": "钓鱼链接", "correct_judgment": True},
            {"id": "rc_013", "scenario": "有陌生人加微信推荐股票内部消息", "true_risk": "high", "true_type": "虚假投资", "correct_judgment": True},
            {"id": "rc_014", "scenario": "收到短信称银行卡境外消费需确认", "true_risk": "high", "true_type": "冒充银行", "correct_judgment": True},
            {"id": "rc_015", "scenario": "有人打电话说社保卡异常需处理", "true_risk": "high", "true_type": "冒充社保", "correct_judgment": True},
            {"id": "rc_016", "scenario": "收到一个正经的银行活动通知短信", "true_risk": "low", "true_type": "正常", "correct_judgment": False, "expected_misjudge": "high"},
            {"id": "rc_017", "scenario": "朋友推荐了一个正规的理财平台", "true_risk": "low", "true_type": "正常", "correct_judgment": False, "expected_misjudge": "mid"},
            {"id": "rc_018", "scenario": "公司HR让下载企业办公软件", "true_risk": "low", "true_type": "正常", "correct_judgment": False, "expected_misjudge": "high"},
            {"id": "rc_019", "scenario": "居委会通知缴纳物业费", "true_risk": "low", "true_type": "正常", "correct_judgment": False, "expected_misjudge": "mid"},
            {"id": "rc_020", "scenario": "网购平台的正规退款流程通知", "true_risk": "low", "true_type": "正常", "correct_judgment": False, "expected_misjudge": "mid"},
            {"id": "rc_021", "scenario": "网上兼职写文案，正规平台发布", "true_risk": "low", "true_type": "正常", "correct_judgment": False, "expected_misjudge": "high"},
            {"id": "rc_022", "scenario": "朋友在群里发了一个正规新闻链接", "true_risk": "low", "true_type": "正常", "correct_judgment": False, "expected_misjudge": "mid"},
            {"id": "rc_023", "scenario": "银行客服打电话推荐理财产品", "true_risk": "low", "true_type": "正常", "correct_judgment": False, "expected_misjudge": "mid"},
            {"id": "rc_024", "scenario": "收到快递公司的取件通知短信", "true_risk": "low", "true_type": "正常", "correct_judgment": False, "expected_misjudge": "high"},
            {"id": "rc_025", "scenario": "APP提示需要更新版本", "true_risk": "low", "true_type": "正常", "correct_judgment": False, "expected_misjudge": "mid"},
            {"id": "rc_026", "scenario": "孩子学校通知交课外活动费", "true_risk": "low", "true_type": "正常", "correct_judgment": False, "expected_misjudge": "high"},
            {"id": "rc_027", "scenario": "亲戚发来借款请求说急用", "true_risk": "low", "true_type": "正常", "correct_judgment": False, "expected_misjudge": "high"},
            {"id": "rc_028", "scenario": "收到中奖通知但需要先交税", "true_risk": "high", "true_type": "中奖诈骗", "correct_judgment": False, "expected_misjudge": "low"},
            {"id": "rc_029", "scenario": "有人称可以帮忙消除征信不良记录", "true_risk": "high", "true_type": "征信诈骗", "correct_judgment": False, "expected_misjudge": "low"},
            {"id": "rc_030", "scenario": "视频里有人自称是亲戚换了新号", "true_risk": "high", "true_type": "冒充熟人", "correct_judgment": False, "expected_misjudge": "low"},
            {"id": "rc_031", "scenario": "收到一个投资平台的短信，但之前确实注册过", "true_risk": "mid", "true_type": "边界", "correct_judgment": True},
            {"id": "rc_032", "scenario": "群里有人发红包，但群主说是广告", "true_risk": "mid", "true_type": "边界", "correct_judgment": True},
            {"id": "rc_033", "scenario": "有人打电话说快递丢了，但确实有快递在路上", "true_risk": "mid", "true_type": "边界", "correct_judgment": True},
            {"id": "rc_034", "scenario": "网上认识的人说要见面，但一直没见", "true_risk": "mid", "true_type": "边界", "correct_judgment": True},
            {"id": "rc_035", "scenario": "老板让转账但语气和平时一样", "true_risk": "mid", "true_type": "边界", "correct_judgment": True},
        ]

    def load_hallucination_cases(self) -> List[Dict[str, Any]]:
        """加载幻觉评测固定样本"""
        return [
            {"id": "hl_001", "query": "最近有哪些新型诈骗手段？", "expected_facts": ["AI换脸", "AI拟声", "屏幕共享"], "forbidden_fabrication": True},
            {"id": "hl_002", "query": "2024年反诈法律有什么新规定？", "expected_facts": ["反电信网络诈骗法"], "forbidden_fabrication": True},
            {"id": "hl_003", "query": "刷单诈骗最常见的套路是什么？", "expected_facts": ["小额返利", "大额投入", "拉黑"], "forbidden_fabrication": True},
            {"id": "hl_004", "query": "被诈骗后报警需要什么材料？", "expected_facts": ["转账记录", "聊天记录", "身份信息"], "forbidden_fabrication": True},
            {"id": "hl_005", "query": "国家反诈中心APP有什么功能？", "expected_facts": ["来电预警", "风险查询", "举报"], "forbidden_fabrication": True},
            {"id": "hl_006", "query": "电信诈骗的立案标准是多少钱？", "expected_facts": ["三千元", "刑事责任"], "forbidden_fabrication": True},
            {"id": "hl_007", "query": "杀猪盘诈骗一般持续多长时间？", "expected_facts": ["几周", "几个月", "感情培养"], "forbidden_fabrication": True},
            {"id": "hl_008", "query": "公检法机关办案的正规流程是什么？", "expected_facts": ["书面通知", "当面", "不转账"], "forbidden_fabrication": True},
            {"id": "hl_009", "query": "虚假投资平台有哪些特征？", "expected_facts": ["高收益", "无资质", "无法提现"], "forbidden_fabrication": True},
            {"id": "hl_010", "query": "老年人防诈骗有哪些注意事项？", "expected_facts": ["不轻信", "不转账", "多核实"], "forbidden_fabrication": True},
            {"id": "hl_011", "query": "最近发生了哪些重大诈骗案件？", "expected_facts": [], "forbidden_fabrication": True},
            {"id": "hl_012", "query": "反诈中心最近发布了什么预警？", "expected_facts": [], "forbidden_fabrication": True},
            {"id": "hl_013", "query": "哪种诈骗类型受害者最多？", "expected_facts": ["刷单", "杀猪盘", "冒充公检法"], "forbidden_fabrication": True},
            {"id": "hl_014", "query": "被骗后资金追回的概率有多大？", "expected_facts": ["及时报警", "冻结"], "forbidden_fabrication": True},
            {"id": "hl_015", "query": "微信转账被骗了怎么追回？", "expected_facts": ["投诉", "报警", "冻结"], "forbidden_fabrication": True},
            {"id": "hl_016", "query": "现在最流行的诈骗方式是什么？", "expected_facts": [], "forbidden_fabrication": True},
            {"id": "hl_017", "query": "上个月全国诈骗案件有多少起？", "expected_facts": [], "forbidden_fabrication": True},
            {"id": "hl_018", "query": "反诈骗警察一个月能破多少案？", "expected_facts": [], "forbidden_fabrication": True},
            {"id": "hl_019", "query": "有哪些专门针对大学生的诈骗手段？", "expected_facts": ["刷单", "校园贷", "兼职"], "forbidden_fabrication": True},
            {"id": "hl_020", "query": "被骗后心理创伤怎么恢复？", "expected_facts": ["心理咨询", "家人支持"], "forbidden_fabrication": True},
        ]

    def evaluate_reflection(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """反思机制评测：无对照实验原始日志，结论指标记为数据不足。"""
        logger.info("=" * 60)
        logger.info("反思机制评测（固定样本概况统计）")
        logger.info("=" * 60)

        total = len(cases)
        risk_distribution: Dict[str, int] = {}
        labeled_correct = 0
        for case in cases:
            risk = case.get("true_risk", "unknown")
            risk_distribution[risk] = risk_distribution.get(risk, 0) + 1
            if case.get("correct_judgment"):
                labeled_correct += 1

        logger.info(f"固定样本: {total} 条, 标注正确判定 {labeled_correct} 条")
        logger.info("误判率降低等对照结论: 数据不足（无原始实验日志）")

        return {
            "task": "反思机制评测",
            "total": total,
            "no_reflection_accuracy": None,
            "with_reflection_accuracy": None,
            "misjudge_reduction": None,
            "corrected_count": None,
            "new_errors_count": None,
            "status": "数据不足",
            "reason": "无反思链路开启/关闭的 A/B 对照实验原始日志，不填充任何对照结论",
            "sample_profile": {
                "true_risk_distribution": risk_distribution,
                "labeled_correct_judgment": labeled_correct,
                "labeled_incorrect_judgment": total - labeled_correct,
            },
        }

    def evaluate_hallucination(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """幻觉率评测：无约束前后对照实验原始日志，结论指标记为数据不足。"""
        logger.info("=" * 60)
        logger.info("幻觉率评测（固定样本概况统计）")
        logger.info("=" * 60)

        total = len(cases)
        with_facts = sum(1 for c in cases if c.get("expected_facts"))
        fact_count = sum(len(c.get("expected_facts") or []) for c in cases)

        logger.info(f"固定样本: {total} 条, 含期望事实 {with_facts} 条, 事实项合计 {fact_count}")
        logger.info("幻觉率降低等对照结论: 数据不足（无原始实验日志）")

        return {
            "task": "幻觉率评测",
            "total": total,
            "no_rag_hallucination_rate": None,
            "with_rag_hallucination_rate": None,
            "hallucination_reduction": None,
            "status": "数据不足",
            "reason": "无 RAG 约束前后对照实验原始日志，不填充任何对照结论",
            "sample_profile": {
                "cases_with_expected_facts": with_facts,
                "cases_without_expected_facts": total - with_facts,
                "expected_fact_items": fact_count,
            },
        }


def _write_results(all_results: Dict[str, Any]) -> None:
    results_dir = Path(__file__).resolve().parent / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    output_path = results_dir / "agent_eval.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, sort_keys=True)
    print(f"\n评测产物已写入: {output_path}")


def main():
    print("=" * 80)
    print("Agent 反思机制与幻觉率评测")
    print("=" * 80)

    evaluator = AgentReflectionEvaluator()

    risk_cases = evaluator.load_risk_cases()
    reflection_results = evaluator.evaluate_reflection(risk_cases)

    print("\n反思机制评测结果:")
    print(f"  固定样本: {reflection_results['total']} 条")
    print(f"  误判率降低: 数据不足（{reflection_results['reason']}）")

    hallucination_cases = evaluator.load_hallucination_cases()
    hallucination_results = evaluator.evaluate_hallucination(hallucination_cases)

    print("\n幻觉率评测结果:")
    print(f"  固定样本: {hallucination_results['total']} 条")
    print(f"  幻觉率降低: 数据不足（{hallucination_results['reason']}）")

    insufficient = {
        "misjudge_reduction": reflection_results["reason"],
        "no_reflection_accuracy": reflection_results["reason"],
        "with_reflection_accuracy": reflection_results["reason"],
        "corrected_count": reflection_results["reason"],
        "new_errors_count": reflection_results["reason"],
        "hallucination_reduction": hallucination_results["reason"],
        "no_rag_hallucination_rate": hallucination_results["reason"],
        "with_rag_hallucination_rate": hallucination_results["reason"],
    }

    all_results = {
        "schema_version": "1.0",
        "eval": "agent_eval",
        "source_files": [
            "evaluation/agent_eval.py::load_risk_cases",
            "evaluation/agent_eval.py::load_hallucination_cases",
        ],
        "method": (
            "固定样本概况为确定性统计；反思与幻觉的对照实验类结论无原始实验日志支撑，"
            "指标记为 null 并标注数据不足"
        ),
        "metrics": {
            "no_reflection_accuracy": None,
            "with_reflection_accuracy": None,
            "misjudge_reduction": None,
            "corrected_count": None,
            "new_errors_count": None,
            "no_rag_hallucination_rate": None,
            "with_rag_hallucination_rate": None,
            "hallucination_reduction": None,
        },
        "details": {
            "reflection": reflection_results,
            "hallucination": hallucination_results,
        },
        "insufficient": insufficient,
    }
    _write_results(all_results)


if __name__ == "__main__":
    main()
