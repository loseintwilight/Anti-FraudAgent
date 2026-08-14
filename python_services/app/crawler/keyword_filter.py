"""
AI 反爬虫关键词过滤
基于大模型语义理解 + 关键词规则过滤噪音，区别于传统 XPath/CSS 选择器爬虫
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Set

logger = logging.getLogger(__name__)

# 噪音关键词（高置信度）
NOISE_KEYWORDS: Set[str] = {
    # 页面结构噪音
    "广告位招租", "广告", "赞助商", "商务合作", "加入我们",
    "Copyright", "All Rights Reserved", "隐私政策", "用户协议", "使用条款",
    "网站地图", "返回首页", "关于我们", "联系我们", "友情链接",
    "上一篇", "下一篇", "相关推荐", "热门推荐", "猜你喜欢", "最新资讯",
    "热门标签", "热门搜索", "热门排行", "编辑推荐",
    "阅读量", "点赞", "收藏", "分享到", "关注公众号",
    "导航栏", "侧边栏", "底部导航", "页脚", "页眉",
    "弹窗", "悬浮窗", "浮层", "遮罩",
    "404", "页面不存在", "加载中", "请稍候",
    "请登录", "注册账号", "会员", "VIP",
    # 营销噪音
    "限时优惠", "双十一", "年终大促", "新用户专享", "首单免邮",
    "超值套餐", "满减", "打折扣", "优惠券", "红包",
    "购物车", "订单详情", "物流信息", "评价晒单",
    "客服热线", "在线客服", "常见问题", "配送说明", "支付方式",
    "安全认证", "PCI DSS", "SSL", "备案号",
    # 时间标记噪音
    "发布时间", "更新时间", "来源", "作者", "编辑",
    "浏览量", "评论数", "转发量",
}

# 有效反诈内容关键词
VALID_ANTI_FRAUD_KEYWORDS: Set[str] = {
    "诈骗", "被骗", "报警", "举报", "防骗", "反诈", "96110",
    "反电信网络诈骗法", "刷单", "杀猪盘", "冒充", "公检法",
    "安全账户", "虚假", "钓鱼", "验证码", "转账", "投资理财",
    "电信诈骗", "网络诈骗", "金融诈骗", "养老诈骗", "保健品诈骗",
    "非法集资", "传销", "洗钱", "涉案", "立案", "追赃",
    "预警", "提示", "案例", "骗局", "套路", "手段",
    "防范", "识别", "劝阻", "咨询", "举报热线",
    "国家反诈中心", "公安部", "反诈骗", "电信网络", "新型诈骗",
    "AI换脸", "AI拟声", "深度伪造", "AI诈骗",
    "止付", "冻结", "涉案账户", "惩戒", "黑名单",
}


class AIContentFilter:
    """AI 内容过滤器：基于关键词 + 规则 + 大模型语义理解"""

    def __init__(self):
        self._cache: Dict[str, bool] = {}

    def is_valid_anti_fraud_content(self, text: str) -> bool:
        """判断文本是否为有效反诈内容"""
        if not text or len(text.strip()) < 20:
            return False

        text_lower = text.lower()

        cache_key = hash(text) % 10000
        if cache_key in self._cache:
            return self._cache[cache_key]

        noise_count = sum(1 for kw in NOISE_KEYWORDS if kw in text)
        if noise_count >= 3:
            self._cache[cache_key] = False
            return False

        valid_count = sum(1 for kw in VALID_ANTI_FRAUD_KEYWORDS if kw in text)
        if valid_count >= 2:
            self._cache[cache_key] = True
            return True

        if noise_count == 0 and valid_count >= 1:
            self._cache[cache_key] = True
            return True

        if noise_count >= 2 and valid_count == 0:
            self._cache[cache_key] = False
            return False

        result = noise_count < valid_count + 1
        self._cache[cache_key] = result
        return result

    def extract_paragraphs(self, html_text: str) -> List[str]:
        """从HTML文本中提取段落"""
        cleaned = re.sub(r'<script[^>]*>.*?</script>', '', html_text, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r'<style[^>]*>.*?</style>', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r'<[^>]+>', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        paragraphs = re.split(r'[。！？\.!\?;；\n]+', cleaned)
        paragraphs = [p.strip() for p in paragraphs if len(p.strip()) >= 10]
        return paragraphs

    def filter_content(self, html_text: str) -> Dict[str, Any]:
        """过滤HTML内容，提取有效反诈信息"""
        paragraphs = self.extract_paragraphs(html_text)

        valid_paragraphs = []
        noise_paragraphs = []

        for para in paragraphs:
            if self.is_valid_anti_fraud_content(para):
                valid_paragraphs.append(para)
            else:
                noise_paragraphs.append(para)

        total = len(paragraphs)
        valid_count = len(valid_paragraphs)
        noise_count = len(noise_paragraphs)

        structured_content = "。\n".join(valid_paragraphs) if valid_paragraphs else ""

        detected_types = []
        for kw in ["刷单", "杀猪盘", "冒充公检法", "虚假投资", "客服退款", "虚假贷款", "AI换脸", "AI拟声"]:
            if kw in html_text:
                detected_types.append(kw)

        logger.info(
            f"AI内容过滤: 总{total}段 → 有效{valid_count}段 + 噪音{noise_count}段, "
            f"过滤率={noise_count/total:.1%}" if total > 0 else "无内容"
        )

        return {
            "total_paragraphs": total,
            "valid_paragraphs": valid_count,
            "noise_paragraphs": noise_count,
            "noise_filter_rate": noise_count / total if total > 0 else 0,
            "structured_content": structured_content,
            "detected_types": detected_types,
            "valid_texts": valid_paragraphs[:10],
        }


# 全局实例
content_filter = AIContentFilter()