"""
DeepSeek API 客户端
支持流式（SSE）和非流式两种调用模式，内置重试机制和超时处理
"""

import json
import time
from typing import AsyncGenerator, Dict, List, Optional, Union

import httpx

from ..config import settings
from ..utils.logger import logger


class DeepSeekClient:
    """
    DeepSeek 大模型 API 客户端

    功能说明：
    - 支持流式（SSE）和非流式两种调用模式
    - 内置指数退避重试机制
    - 请求超时控制
    - 完整的对话历史上下文携带
    """

    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.api_base = settings.DEEPSEEK_API_BASE.rstrip("/")
        self.model = settings.DEEPSEEK_MODEL
        self.timeout = settings.DEEPSEEK_TIMEOUT
        self.max_retries = settings.DEEPSEEK_MAX_RETRIES
        self.retry_delay = settings.DEEPSEEK_RETRY_DELAY
        self.max_tokens = settings.DEEPSEEK_MAX_TOKENS
        self.temperature = settings.DEEPSEEK_TEMPERATURE

        # 请求头
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # HTTP 客户端（连接池复用）
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            follow_redirects=True,
        )

    async def _request(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
    ) -> Union[Dict, AsyncGenerator[str, None]]:
        """
        发送请求到 DeepSeek API，带重试机制

        Args:
            messages: 对话消息列表 [{"role": "user", "content": "..."}, ...]
            stream: 是否启用流式输出

        Returns:
            stream=False: 返回完整响应字典
            stream=True: 返回异步生成器，逐个产出文本片段

        Raises:
            Exception: 所有重试均失败时抛出
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

        url = f"{self.api_base}/chat/completions"

        # 重试循环
        for attempt in range(1, self.max_retries + 1):
            try:
                if stream:
                    # 流式模式
                    return self._handle_stream(url, payload)
                else:
                    # 非流式模式
                    response = await self._client.post(url, json=payload, headers=self.headers)
                    response.raise_for_status()
                    data = response.json()
                    logger.info(
                        "DeepSeek API 调用成功 (非流式) | "
                        f"input_tokens={data.get('usage', {}).get('prompt_tokens', 'N/A')}, "
                        f"output_tokens={data.get('usage', {}).get('completion_tokens', 'N/A')}"
                    )
                    return data

            except httpx.TimeoutException as e:
                logger.warning(f"DeepSeek API 超时 (attempt {attempt}/{self.max_retries}): {e}")
                if attempt < self.max_retries:
                    await self._wait_retry(attempt)
                else:
                    raise

            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                try:
                    body = e.response.json()
                except Exception:
                    body = {"error": e.response.text}

                error_detail = body.get("error", {}).get("message", "") or body.get("error", "")

                if status == 401:
                    logger.error(
                        f"DeepSeek API Key 验证失败: status={status}, "
                        f"detail={error_detail}"
                    )
                    raise RuntimeError(
                        f"API Key 验证失败: {error_detail}。请检查 DEEPSEEK_API_KEY 配置是否正确。"
                    )
                elif status == 402:
                    logger.error(f"DeepSeek API 余额不足: {error_detail}")
                    raise RuntimeError(
                        f"API 余额不足: {error_detail}。请充值后重试。"
                    )
                elif status == 429:
                    logger.error(f"DeepSeek API 请求频率限制: {error_detail}")
                    raise RuntimeError(
                        f"API 请求频率过高: {error_detail}。请稍后重试。"
                    )
                else:
                    logger.error(
                        f"DeepSeek API HTTP 错误 (attempt {attempt}/{self.max_retries}): "
                        f"status={status}, body={e.response.text}"
                    )

                if attempt < self.max_retries and status >= 500:
                    await self._wait_retry(attempt)
                else:
                    raise

            except Exception as e:
                logger.error(f"DeepSeek API 未知错误 (attempt {attempt}/{self.max_retries}): {e}")
                if attempt < self.max_retries:
                    await self._wait_retry(attempt)
                else:
                    raise

    async def _handle_stream(self, url: str, payload: dict) -> AsyncGenerator[str, None]:
        """
        处理 SSE 流式响应

        Args:
            url: API 地址
            payload: 请求体

        Yields:
            逐个文本片段
        """
        async with self._client.stream("POST", url, json=payload, headers=self.headers) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data_str = line[6:].strip()
                if data_str == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        yield content
                except json.JSONDecodeError:
                    logger.warning(f"SSE 解析失败，跳过: {data_str}")
                    continue

    async def _wait_retry(self, attempt: int):
        """指数退避等待"""
        wait_time = self.retry_delay * (2 ** (attempt - 1))
        logger.info(f"等待 {wait_time:.1f}s 后重试...")
        await self._client.aclose()
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            follow_redirects=True,
        )
        await time.sleep(wait_time)

    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        stream: bool = False,
    ) -> Union[str, AsyncGenerator[str, None]]:
        """
        对话接口（对外暴露的主方法）

        Args:
            messages: 对话历史
            system_prompt: 系统提示词（可选）
            stream: 是否流式输出

        Returns:
            stream=False: 返回完整回复文本
            stream=True: 返回异步生成器
        """
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        logger.debug(f"发送对话请求: messages_count={len(full_messages)}, stream={stream}")

        result = await self._request(full_messages, stream=stream)

        if stream:
            return self._wrap_stream(result)
        else:
            try:
                content = result["choices"][0]["message"]["content"]
                return content
            except (KeyError, IndexError, TypeError) as e:
                logger.error(f"解析响应失败: {e}, response={result}")
                return "抱歉，AI 服务暂时不可用，请稍后再试。"

    async def _wrap_stream(self, gen: AsyncGenerator[str, None]) -> AsyncGenerator[str, None]:
        """包装流式生成器，确保异常处理"""
        try:
            async for chunk in gen:
                yield chunk
        except Exception as e:
            logger.error(f"流式输出异常: {e}")
            yield "抱歉，AI 服务暂时出现异常，请稍后再试。"

    async def close(self):
        """关闭 HTTP 客户端"""
        await self._client.aclose()


# 全局单例
deepseek_client = DeepSeekClient()