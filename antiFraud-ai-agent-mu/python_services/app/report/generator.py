"""
报告生成模块 — 对应升级方案 Section 3.2

功能说明：
- 生成反诈风险诊断报告（JSON 格式）
- 支持导出为 PDF 和图片格式
- 报告包含：风险项明细、诈骗类型定性、防骗建议、报警指引等

注意：
- PDF 生成依赖 reportlab 库
- 图片生成依赖 Pillow 库
- 中文字体需要系统支持（默认使用微软雅黑）
"""

import io
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..config import settings
from ..models.schemas import FraudReport
from ..utils.logger import logger


class ReportGenerator:
    """
    报告生成器

    支持生成 JSON / PDF / 图片三种格式的报告
    """

    def __init__(self):
        self.output_path = Path(settings.REPORT_OUTPUT_PATH)
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.font_path = settings.REPORT_FONT_PATH
        logger.info(f"报告生成器初始化完成，输出路径: {self.output_path}")

    def generate_json(self, report: FraudReport) -> dict:
        """
        生成 JSON 格式的风险报告

        Args:
            report: 风险报告数据

        Returns:
            报告字典
        """
        report_dict = {
            "报告编号": report.report_id,
            "生成时间": report.generated_at,
            "用户信息": report.user_info,
            "风险分析": {
                "诈骗类型定性": report.fraud_type,
                "诈骗置信度": f"{report.fraud_confidence:.1%}",
                "被骗概率评估": report.loss_probability,
                "风险项明细": [
                    {
                        "来源": item.source,
                        "风险类型": item.risk_type,
                        "风险分值": item.risk_score,
                        "说明": item.explanation,
                    }
                    for item in report.risk_items
                ],
                "AI分析过程": report.analysis_steps,
            },
            "建议与指引": {
                "防骗建议": report.prevention_tips,
                "转账拦截提醒": report.transfer_warning,
                "报警维权指引": report.legal_guidance,
                "AI劝导话术": report.persuasion_message,
            },
        }
        return report_dict

    def generate_html(self, report: FraudReport) -> str:
        """
        生成 HTML 格式的报告（可用于网页预览或导出为 PDF）

        Args:
            report: 风险报告数据

        Returns:
            HTML 字符串
        """
        risk_level = "极高" if report.fraud_confidence >= 0.8 else (
            "高" if report.fraud_confidence >= 0.5 else (
                "中" if report.fraud_confidence >= 0.3 else "低"
            )
        )

        risk_items_html = "".join([
            f"""
            <tr>
                <td>{item.risk_type}</td>
                <td>{item.risk_score}</td>
                <td>{item.explanation}</td>
            </tr>
            """
            for item in report.risk_items
        ])

        tips_html = "".join([
            f"<li>{tip}</li>" for tip in report.prevention_tips
        ])

        html = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <title>反诈风险诊断报告 - {report.report_id}</title>
            <style>
                body {{
                    font-family: "Microsoft YaHei", "SimHei", sans-serif;
                    margin: 40px;
                    padding: 0;
                    background: #f5f7fa;
                    color: #333;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background: #fff;
                    padding: 40px;
                    border-radius: 12px;
                    box-shadow: 0 2px 12px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #d32f2f;
                    border-bottom: 3px solid #d32f2f;
                    padding-bottom: 12px;
                    font-size: 24px;
                }}
                h2 {{
                    color: #1976d2;
                    margin-top: 30px;
                    font-size: 18px;
                }}
                .risk-level {{
                    display: inline-block;
                    padding: 6px 16px;
                    border-radius: 20px;
                    color: #fff;
                    font-weight: bold;
                    font-size: 16px;
                    background: {"#d32f2f" if risk_level in ("极高","高") else "#f57c00" if risk_level == "中" else "#388e3c"};
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 16px 0;
                }}
                th, td {{
                    border: 1px solid #e0e0e0;
                    padding: 10px 12px;
                    text-align: left;
                }}
                th {{
                    background: #f5f5f5;
                    font-weight: bold;
                }}
                .warning-box {{
                    background: #fff3e0;
                    border-left: 4px solid #ff6f00;
                    padding: 16px;
                    margin: 16px 0;
                    border-radius: 4px;
                }}
                .persuasion-box {{
                    background: #e3f2fd;
                    border-left: 4px solid #1976d2;
                    padding: 16px;
                    margin: 16px 0;
                    border-radius: 4px;
                }}
                ul {{
                    padding-left: 20px;
                }}
                li {{
                    margin: 8px 0;
                    line-height: 1.6;
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #e0e0e0;
                    color: #999;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🛡️ 反诈风险诊断报告</h1>
                <p>报告编号：{report.report_id}</p>
                <p>生成时间：{report.generated_at}</p>
                <p>用户角色：{report.user_info.get("role", "unknown")}</p>

                <h2>一、风险等级评估</h2>
                <p><span class="risk-level">{risk_level}风险</span></p>
                <p>诈骗类型：<strong>{report.fraud_type}</strong></p>
                <p>诈骗置信度：{report.fraud_confidence:.1%}</p>
                <p>被骗概率评估：<strong>{report.loss_probability}</strong></p>

                <h2>二、风险项明细</h2>
                <table>
                    <tr>
                        <th>风险类型</th>
                        <th>风险分值</th>
                        <th>说明</th>
                    </tr>
                    {risk_items_html}
                </table>

                <h2>三、AI 分析过程</h2>
                <ol>
                    {"".join(f"<li>{step}</li>" for step in report.analysis_steps)}
                </ol>

                <h2>四、防骗建议</h2>
                <ul>{tips_html}</ul>

                <div class="warning-box">
                    <strong>⚠️ 转账拦截提醒</strong>
                    <p>{report.transfer_warning}</p>
                </div>

                <div class="persuasion-box">
                    <strong>💬 AI 劝导话术</strong>
                    <p>{report.persuasion_message}</p>
                </div>

                <h2>五、报警维权指引</h2>
                <pre style="white-space: pre-wrap; background: #f5f5f5; padding: 16px; border-radius: 4px;">{report.legal_guidance}</pre>

                <div class="footer">
                    <p>本报告由 AI 反诈智能体自动生成，仅供参考，不构成法律意见。</p>
                    <p>如有紧急情况，请立即拨打 110 报警。</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html

    def save_json(self, report: FraudReport) -> str:
        """
        保存 JSON 报告到文件

        Args:
            report: 风险报告数据

        Returns:
            文件路径
        """
        import json
        report_dict = self.generate_json(report)
        file_path = self.output_path / f"{report.report_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(report_dict, f, ensure_ascii=False, indent=2)
        logger.info(f"JSON 报告已保存: {file_path}")
        return str(file_path)

    def save_html(self, report: FraudReport) -> str:
        """
        保存 HTML 报告到文件

        Args:
            report: 风险报告数据

        Returns:
            文件路径
        """
        html = self.generate_html(report)
        file_path = self.output_path / f"{report.report_id}.html"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html)
        logger.info(f"HTML 报告已保存: {file_path}")
        return str(file_path)

    def export_pdf(self, report: FraudReport) -> Optional[str]:
        """
        导出 PDF 格式的报告

        依赖 reportlab 库，如果未安装则返回 None
        安装方式：pip install reportlab

        Args:
            report: 风险报告数据

        Returns:
            PDF 文件路径，失败返回 None
        """
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import mm
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                PageBreak, HRFlowable,
            )
            from reportlab.lib import colors

            file_path = self.output_path / f"{report.report_id}.pdf"
            doc = SimpleDocTemplate(
                str(file_path),
                pagesize=A4,
                topMargin=20 * mm,
                bottomMargin=20 * mm,
                leftMargin=20 * mm,
                rightMargin=20 * mm,
            )

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                "ReportTitle",
                parent=styles["Title"],
                fontName="STSong-Light" if os.name != "nt" else "Helvetica",
                fontSize=22,
                textColor=colors.HexColor("#d32f2f"),
                spaceAfter=20,
            )
            normal_style = ParagraphStyle(
                "ReportNormal",
                parent=styles["Normal"],
                fontName="STSong-Light" if os.name != "nt" else "Helvetica",
                fontSize=11,
                leading=18,
                spaceAfter=8,
            )
            heading_style = ParagraphStyle(
                "ReportHeading",
                parent=styles["Heading2"],
                fontName="STSong-Light" if os.name != "nt" else "Helvetica",
                fontSize=14,
                textColor=colors.HexColor("#1976d2"),
                spaceBefore=16,
                spaceAfter=8,
            )

            elements = []
            elements.append(Paragraph("反诈风险诊断报告", title_style))
            elements.append(Paragraph(f"报告编号: {report.report_id}", normal_style))
            elements.append(Paragraph(f"生成时间: {report.generated_at}", normal_style))
            elements.append(Spacer(1, 12))

            # 风险等级
            elements.append(Paragraph("一、风险等级评估", heading_style))
            risk_level = "极高" if report.fraud_confidence >= 0.8 else (
                "高" if report.fraud_confidence >= 0.5 else (
                    "中" if report.fraud_confidence >= 0.3 else "低"
                )
            )
            elements.append(Paragraph(f"风险等级: {risk_level}", normal_style))
            elements.append(Paragraph(f"诈骗类型: {report.fraud_type}", normal_style))
            elements.append(Paragraph(f"诈骗置信度: {report.fraud_confidence:.1%}", normal_style))
            elements.append(Spacer(1, 12))

            # 风险项明细
            elements.append(Paragraph("二、风险项明细", heading_style))
            table_data = [["风险类型", "风险分值", "说明"]]
            for item in report.risk_items:
                table_data.append([item.risk_type, str(item.risk_score), item.explanation])

            table = Table(table_data, colWidths=[120, 70, 280])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f5f5f5")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#333")),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 12))

            # 防骗建议
            elements.append(Paragraph("三、防骗建议", heading_style))
            for tip in report.prevention_tips:
                elements.append(Paragraph(f"• {tip}", normal_style))
            elements.append(Spacer(1, 12))

            # 转账拦截提醒
            elements.append(Paragraph("四、转账拦截提醒", heading_style))
            elements.append(Paragraph(
                f'<font color="#ff6f00">⚠️ {report.transfer_warning}</font>',
                normal_style,
            ))
            elements.append(Spacer(1, 12))

            # AI 劝导话术
            if report.persuasion_message:
                elements.append(Paragraph("五、AI 劝导话术", heading_style))
                elements.append(Paragraph(
                    f'<font color="#1976d2">{report.persuasion_message}</font>',
                    normal_style,
                ))
                elements.append(Spacer(1, 12))

            # 报警维权指引
            elements.append(Paragraph("六、报警维权指引", heading_style))
            for line in report.legal_guidance.split("\n"):
                if line.strip():
                    elements.append(Paragraph(line, normal_style))

            doc.build(elements)
            logger.info(f"PDF 报告已生成: {file_path}")
            return str(file_path)

        except ImportError:
            logger.warning("reportlab 未安装，无法生成 PDF。请执行: pip install reportlab")
            return None
        except Exception as e:
            logger.error(f"PDF 报告生成失败: {e}")
            return None

    def export_image(self, report: FraudReport) -> Optional[bytes]:
        """
        导出图片格式的报告

        依赖 Pillow 库，如果未安装则返回 None
        安装方式：pip install Pillow

        Args:
            report: 风险报告数据

        Returns:
            PNG 图片字节数据，失败返回 None
        """
        from PIL import Image, ImageDraw, ImageFont

        risk_level = "极高" if report.fraud_confidence >= 0.8 else (
            "高" if report.fraud_confidence >= 0.5 else (
                "中" if report.fraud_confidence >= 0.3 else "低"
            )
        )

        # 构建报告文本
        lines = [
            "🛡️ 反诈风险诊断报告",
            f"报告编号: {report.report_id}",
            f"生成时间: {report.generated_at}",
            "",
            f"风险等级: {risk_level}",
            f"诈骗类型: {report.fraud_type}",
            "",
            "防骗建议:",
        ]
        for tip in report.prevention_tips:
            lines.append(f"  • {tip}")

        lines.extend([
            "",
            f"转账拦截提醒: {report.transfer_warning}",
        ])

        if report.persuasion_message:
            lines.extend(["", "AI劝导话术:", f"  {report.persuasion_message}"])

        try:
            # 尝试加载中文字体
            font_size = 16
            if os.path.exists(self.font_path):
                font = ImageFont.truetype(self.font_path, font_size)
                title_font = ImageFont.truetype(self.font_path, font_size + 8)
            else:
                font = ImageFont.load_default()
                title_font = ImageFont.load_default()

            # 计算图片尺寸
            char_width = font_size * 0.6
            max_width = 600
            line_height = font_size + 8
            img_height = len(lines) * line_height + 80

            img = Image.new("RGB", (max_width, int(img_height)), "white")
            draw = ImageDraw.Draw(img)

            y = 20
            for i, line in enumerate(lines):
                if line.startswith("🛡️"):
                    draw.text((20, y), line, fill="#d32f2f", font=title_font)
                    y += line_height + 4
                elif line.startswith("风险等级"):
                    draw.text((20, y), line, fill="#d32f2f", font=font)
                    y += line_height
                elif line.startswith("转账拦截"):
                    draw.text((20, y), line, fill="#ff6f00", font=font)
                    y += line_height
                elif line == "":
                    y += 8
                else:
                    draw.text((20, y), line, fill="#333333", font=font)
                    y += line_height

            buf = io.BytesIO()
            img.save(buf, format="PNG")
            logger.info("图片报告已生成")
            return buf.getvalue()

        except ImportError:
            logger.warning("Pillow 未安装，无法生成图片。请执行: pip install Pillow")
            return None
        except Exception as e:
            logger.error(f"图片报告生成失败: {e}")
            return None


# 全局单例
report_generator = ReportGenerator()