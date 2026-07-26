"""
LangChain 工具定义
替代 Spring AI 的 ToolCallback 工具注册
"""

import json
import logging
import os
import subprocess
import tempfile
from datetime import datetime
from typing import Any, Dict, List, Optional, Type

from langchain_core.tools import BaseTool, tool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ========== 工具参数 Schema ==========

class FileOperationInput(BaseModel):
    """文件操作工具参数"""
    operation: str = Field(description="操作类型: read/write/delete/list")
    path: str = Field(description="文件路径")
    content: Optional[str] = Field(default=None, description="写入内容（write 操作时必填）")


class PDFGenerationInput(BaseModel):
    """PDF 生成工具参数"""
    title: str = Field(description="PDF 标题")
    content: str = Field(description="PDF 内容（Markdown 格式）")
    output_path: Optional[str] = Field(default=None, description="输出路径（可选）")


class WebSearchInput(BaseModel):
    """网页搜索工具参数"""
    query: str = Field(description="搜索关键词")
    num_results: int = Field(default=5, description="返回结果数量")


class WebScrapingInput(BaseModel):
    """网页抓取工具参数"""
    url: str = Field(description="目标 URL")


class TerminalOperationInput(BaseModel):
    """终端操作工具参数"""
    command: str = Field(description="要执行的命令")
    timeout: int = Field(default=30, description="超时时间（秒）")


# ========== 工具实现 ==========

@tool("file_operation", args_schema=FileOperationInput)
def file_operation(
    operation: str,
    path: str,
    content: Optional[str] = None,
) -> str:
    """文件操作：读取、写入、删除、列出文件"""
    try:
        if operation == "read":
            if not os.path.exists(path):
                return f"文件不存在: {path}"
            with open(path, "r", encoding="utf-8") as f:
                return f.read()

        elif operation == "write":
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content or "")
            return f"文件写入成功: {path}"

        elif operation == "delete":
            if os.path.exists(path):
                os.remove(path)
                return f"文件删除成功: {path}"
            return f"文件不存在: {path}"

        elif operation == "list":
            if not os.path.exists(path):
                return f"目录不存在: {path}"
            files = os.listdir(path)
            return json.dumps(files, ensure_ascii=False, indent=2)

        else:
            return f"不支持的操作: {operation}"

    except Exception as e:
        logger.error(f"文件操作失败: {e}")
        return f"文件操作失败: {str(e)}"


@tool("pdf_generation", args_schema=PDFGenerationInput)
def pdf_generation(
    title: str,
    content: str,
    output_path: Optional[str] = None,
) -> str:
    """生成 PDF 报告"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            Paragraph, SimpleDocTemplate, Spacer, ListFlowable, ListItem,
        )

        if output_path is None:
            output_dir = tempfile.mkdtemp()
            safe_title = title.replace(" ", "_").replace("/", "_")
            output_path = os.path.join(output_dir, f"{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        doc = SimpleDocTemplate(output_path, pagesize=A4)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "CustomTitle", parent=styles["Title"],
            fontSize=18, spaceAfter=20,
        )
        normal_style = ParagraphStyle(
            "CustomNormal", parent=styles["Normal"],
            fontSize=11, leading=16,
        )

        elements = []
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 0.2 * inch))

        # 按行处理内容
        for line in content.split("\n"):
            line = line.strip()
            if not line:
                elements.append(Spacer(1, 0.1 * inch))
            elif line.startswith("- ") or line.startswith("* "):
                elements.append(ListItem(Paragraph(line[2:], normal_style)))
            else:
                elements.append(Paragraph(line, normal_style))

        doc.build(elements)
        return f"PDF 生成成功: {output_path}"

    except ImportError:
        return "reportlab 未安装，请执行: pip install reportlab"
    except Exception as e:
        logger.error(f"PDF 生成失败: {e}")
        return f"PDF 生成失败: {str(e)}"


@tool("web_search", args_schema=WebSearchInput)
def web_search(query: str, num_results: int = 5) -> str:
    """搜索互联网信息"""
    try:
        import requests
        from urllib.parse import quote

        # 使用 DuckDuckGo 搜索结果（无需 API Key）
        encoded_query = quote(query)
        url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1"

        resp = requests.get(url, timeout=10)
        data = resp.json()

        results = []
        abstract = data.get("AbstractText", "")
        if abstract:
            results.append(f"摘要: {abstract}")

        related = data.get("RelatedTopics", [])
        for item in related[:num_results]:
            if isinstance(item, dict):
                text = item.get("Text", "")
                url_val = item.get("FirstURL", "")
                if text:
                    results.append(f"- {text}\n  {url_val}")

        if not results:
            # 备用：使用 DuckDuckGo HTML 搜索
            html_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            resp = requests.get(html_url, timeout=10, headers={
                "User-Agent": "Mozilla/5.0 (compatible; AntiFraudBot/1.0)"
            })
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, "html.parser")
            for result in soup.select(".result__body")[:num_results]:
                title_el = result.select_one(".result__title a")
                snippet_el = result.select_one(".result__snippet")
                if title_el:
                    title_text = title_el.get_text(strip=True)
                    snippet_text = snippet_el.get_text(strip=True) if snippet_el else ""
                    results.append(f"- {title_text}\n  {snippet_text}")

        return "\n\n".join(results) if results else "未找到相关结果"

    except Exception as e:
        logger.error(f"搜索失败: {e}")
        return f"搜索失败: {str(e)}"


@tool("web_scraping", args_schema=WebScrapingInput)
def web_scraping(url: str) -> str:
    """抓取网页内容"""
    try:
        import requests
        from bs4 import BeautifulSoup

        resp = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })
        resp.encoding = resp.apparent_encoding

        soup = BeautifulSoup(resp.text, "html.parser")

        # 移除脚本和样式
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        # 提取文本
        text = soup.get_text(separator="\n", strip=True)
        lines = [line for line in text.split("\n") if line.strip()]
        content = "\n".join(lines[:200])  # 限制 200 行

        return content

    except Exception as e:
        logger.error(f"网页抓取失败: {e}")
        return f"网页抓取失败: {str(e)}"


@tool("terminal_operation", args_schema=TerminalOperationInput)
def terminal_operation(command: str, timeout: int = 30) -> str:
    """执行终端命令"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        output = []
        if result.stdout:
            output.append(f"输出:\n{result.stdout[:2000]}")
        if result.stderr:
            output.append(f"错误:\n{result.stderr[:1000]}")

        return "\n".join(output) if output else "命令执行完成，无输出"

    except subprocess.TimeoutExpired:
        return f"命令执行超时（{timeout}秒）"
    except Exception as e:
        return f"命令执行失败: {str(e)}"


@tool("terminate")
def terminate() -> str:
    """终止当前任务"""
    return "任务已终止"


# 获取所有工具
def get_all_tools() -> List[BaseTool]:
    """获取所有工具列表"""
    return [
        file_operation,
        pdf_generation,
        web_search,
        web_scraping,
        terminal_operation,
        terminate,
    ]