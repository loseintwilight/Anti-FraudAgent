"""
图片版风险报告生成器
使用 Pillow 生成包含风险评分、来源项、话术等信息的图片报告
"""

from __future__ import annotations

import base64
import io
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

# 颜色定义
COLORS = {
    "background": (245, 247, 250),
    "card_white": (255, 255, 255),
    "primary": (59, 130, 246),       # 蓝色
    "danger": (239, 68, 68),          # 红色
    "warning": (245, 158, 11),        # 橙色
    "success": (16, 185, 129),        # 绿色
    "text_primary": (30, 41, 59),     # 深色文本
    "text_secondary": (100, 116, 139), # 灰色文本
    "border": (226, 232, 240),        # 边框色
    "star": (250, 204, 21),           # 金色
}

# 风险等级颜色映射
RISK_COLORS = {
    "low": COLORS["success"],
    "mid": COLORS["warning"],
    "high": COLORS["danger"],
    "critical": (139, 0, 0),          # 暗红色
}

# 风险等级中文名
RISK_NAMES = {
    "low": "低风险",
    "mid": "中风险",
    "high": "高风险",
    "critical": "极高风险",
}


class ImageReportGenerator:
    """
    图片风控报告生成器
    使用 Pillow 库绘制包含丰富信息的风险报告图片
    """

    def __init__(self, font_path: Optional[str] = None):
        """
        初始化报告生成器
        :param font_path: 中文字体路径，若为 None 则尝试加载系统默认中文字体
        """
        self.font_path = font_path or self._find_chinese_font()
        self.width = 800
        self.height = 1200

    @staticmethod
    def _find_chinese_font() -> str:
        """
        查找系统中可用的中文字体
        按优先级搜索常见字体路径
        """
        # Windows 常见中文字体路径
        windows_fonts = [
            "C:/Windows/Fonts/msyh.ttc",           # 微软雅黑
            "C:/Windows/Fonts/simhei.ttf",          # 黑体
            "C:/Windows/Fonts/simsun.ttc",          # 宋体
            "C:/Windows/Fonts/yahei.ttf",           # 微软雅黑
        ]
        # Linux/macOS 常见字体路径
        unix_fonts = [
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
        ]

        for font_path in windows_fonts + unix_fonts:
            if os.path.exists(font_path):
                return font_path

        # 如果找不到中文字体，返回 None，后续会使用默认字体
        logger.warning("未找到中文字体，报告中的中文可能无法正常显示")
        return ""

    def _load_font(self, size: int) -> ImageFont.FreeTypeFont:
        """加载指定大小的字体"""
        try:
            if self.font_path and os.path.exists(self.font_path):
                return ImageFont.truetype(self.font_path, size)
        except Exception:
            logger.warning(f"无法加载字体 {self.font_path}，使用默认字体")
        return ImageFont.load_default()

    def generate(
        self,
        user_id: str,
        risk_level: str,
        risk_score: float,
        profile_summary: str = "",
        risk_sources: Optional[List[Dict[str, Any]]] = None,
        fraud_type: Optional[str] = None,
        persuasion_text: Optional[str] = None,
        output_format: str = "png",
    ) -> Dict[str, Any]:
        """
        生成风险报告图片

        参数说明:
            user_id: 用户ID
            risk_level: 风险等级 (low/mid/high/critical)
            risk_score: 风险评分 (0-100)
            profile_summary: 用户画像摘要
            risk_sources: 风险来源列表
            fraud_type: 诈骗类型
            persuasion_text: 劝阻话术
            output_format: 输出格式 (png/jpg)

        返回:
            dict: 包含 base64 编码图片及其格式
        """
        logger.info(f"开始生成风险报告: user_id={user_id}")

        # 创建画布
        img = Image.new("RGB", (self.width, self.height), COLORS["background"])
        draw = ImageDraw.Draw(img)

        # 加载字体
        title_font = self._load_font(36)
        header_font = self._load_font(28)
        body_font = self._load_font(22)
        small_font = self._load_font(18)

        y_offset = 0

        # ======== 顶部标题栏 ========
        draw.rectangle(
            [0, 0, self.width, 100], fill=COLORS["primary"]
        )
        draw.text(
            (self.width // 2, 50),
            "📋 反诈风险评估报告",
            fill=COLORS["card_white"],
            font=title_font,
            anchor="mm",
        )
        y_offset = 120

        # ======== 风险等级 + 评分区域 ========
        risk_color = RISK_COLORS.get(risk_level, COLORS["text_primary"])
        risk_name = RISK_NAMES.get(risk_level, "未知")

        # 卡片背景
        draw.rounded_rectangle(
            [40, y_offset, self.width - 40, y_offset + 180],
            radius=16, fill=COLORS["card_white"], outline=COLORS["border"]
        )

        # 风险等级标签
        draw.rounded_rectangle(
            [60, y_offset + 15, 150, y_offset + 55],
            radius=8, fill=risk_color
        )
        draw.text(
            (105, y_offset + 35), risk_name,
            fill=COLORS["card_white"], font=header_font, anchor="mm"
        )

        # 风险评分
        draw.text(
            (self.width - 60, y_offset + 35),
            f"风险评分: {risk_score:.1f}",
            fill=risk_color, font=header_font, anchor="rm",
        )

        # 用户ID
        draw.text(
            (60, y_offset + 75),
            f"用户: {user_id}",
            fill=COLORS["text_secondary"], font=body_font,
        )

        # 时间戳
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        draw.text(
            (60, y_offset + 110),
            f"评估时间: {timestamp}",
            fill=COLORS["text_secondary"], font=body_font,
        )

        # 画像摘要
        if profile_summary:
            draw.text(
                (60, y_offset + 145),
                f"画像摘要: {profile_summary[:50]}",
                fill=COLORS["text_secondary"], font=small_font,
            )

        y_offset += 210

        # ======== 风险来源明细 ========
        draw.text(
            (40, y_offset), "📊 风险来源明细",
            fill=COLORS["text_primary"], font=header_font,
        )
        y_offset += 45

        risk_sources = risk_sources or []
        if risk_sources:
            # 表头
            header_y = y_offset
            draw.rounded_rectangle(
                [40, header_y, self.width - 40, header_y + 40],
                radius=8, fill=COLORS["primary"]
            )
            draw.text((80, header_y + 20), "风险维度", fill=COLORS["card_white"], font=body_font, anchor="lm")
            draw.text((280, header_y + 20), "得分", fill=COLORS["card_white"], font=body_font, anchor="lm")
            draw.text((380, header_y + 20), "权重", fill=COLORS["card_white"], font=body_font, anchor="lm")
            draw.text((480, header_y + 20), "贡献", fill=COLORS["card_white"], font=body_font, anchor="lm")
            y_offset += 50

            # 数据行
            for i, source in enumerate(risk_sources):
                row_y = y_offset
                # 斑马纹
                bg_color = COLORS["card_white"] if i % 2 == 0 else (249, 250, 251)

                # 获取详情文本，截断过长的
                detail = source.get("detail", "")
                if len(detail) > 25:
                    detail = detail[:22] + "..."

                draw.rectangle([40, row_y, self.width - 40, row_y + 35], fill=bg_color)
                draw.text((80, row_y + 17), source.get("dimension", ""), fill=COLORS["text_primary"], font=body_font, anchor="lm")
                draw.text((280, row_y + 17), f"{source.get('score', 0):.1f}", fill=COLORS["text_primary"], font=body_font, anchor="lm")
                draw.text((380, row_y + 17), f"{source.get('weight', 0):.2f}", fill=COLORS["text_primary"], font=body_font, anchor="lm")
                draw.text((480, row_y + 17), f"{source.get('contribution', 0):.1f}", fill=risk_color, font=body_font, anchor="lm")
                draw.text((580, row_y + 17), detail, fill=COLORS["text_secondary"], font=small_font, anchor="lm")

                y_offset += 38
                if y_offset > self.height - 250:
                    break
        else:
            draw.text(
                (60, y_offset), "暂无风险数据",
                fill=COLORS["text_secondary"], font=body_font,
            )
            y_offset += 40

        y_offset += 15

        # ======== 分隔线 ========
        draw.line(
            [40, y_offset, self.width - 40, y_offset],
            fill=COLORS["border"], width=2
        )
        y_offset += 25

        # ======== 诈骗类型 ========
        if fraud_type:
            draw.text((40, y_offset), "🔍 诈骗类型分析", fill=COLORS["text_primary"], font=header_font)
            y_offset += 40
            draw.rounded_rectangle(
                [60, y_offset, self.width - 60, y_offset + 50],
                radius=10, fill=COLORS["card_white"], outline=COLORS["border"]
            )
            draw.text(
                (self.width // 2, y_offset + 25),
                fraud_type,
                fill=COLORS["danger"], font=header_font, anchor="mm",
            )
            y_offset += 70

        # ======== 劝阻话术 ========
        if persuasion_text:
            draw.text((40, y_offset), "💬 劝阻话术", fill=COLORS["text_primary"], font=header_font)
            y_offset += 40

            # 话术文本框
            text_box = draw.textbbox((60, y_offset), persuasion_text, font=body_font)
            text_height = text_box[3] - text_box[1] + 20
            draw.rounded_rectangle(
                [60, y_offset, self.width - 60, y_offset + text_height + 30],
                radius=10, fill=COLORS["card_white"], outline=COLORS["border"]
            )
            draw.text(
                (80, y_offset + 15), persuasion_text,
                fill=COLORS["text_primary"], font=body_font,
            )
            y_offset += text_height + 50

        # ======== 底部提示 ========
        y_offset = max(y_offset, self.height - 100)
        draw.line(
            [40, y_offset, self.width - 40, y_offset],
            fill=COLORS["border"], width=1
        )
        draw.text(
            (self.width // 2, y_offset + 30),
            "本报告由 AI 辅助反诈系统自动生成，仅供参考",
            fill=COLORS["text_secondary"], font=small_font, anchor="mm",
        )
        draw.text(
            (self.width // 2, y_offset + 55),
            "如有疑问请拨打反诈热线 96110",
            fill=COLORS["text_secondary"], font=small_font, anchor="mm",
        )

        # ======== 编码输出 ========
        output = io.BytesIO()
        img_format = "PNG" if output_format.lower() == "png" else "JPEG"
        img.save(output, format=img_format)
        output.seek(0)

        base64_str = base64.b64encode(output.getvalue()).decode("utf-8")

        logger.info(f"风险报告生成完成: {len(base64_str)} bytes")

        return {
            "image_base64": base64_str,
            "format": output_format,
        }
