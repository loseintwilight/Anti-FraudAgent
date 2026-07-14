import axios from 'axios'
import { API_BASE } from '../config'

/**
 * 通用 HTTP 客户端（非流式接口可统一走此实例）。
 * SSE 流式请求使用浏览器 fetch，见 ./sse.js。
 */
export const http = axios.create({
  baseURL: API_BASE,
  timeout: 120_000,
})
