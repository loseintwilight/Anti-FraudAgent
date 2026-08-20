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

/**
 * API 连接错误提示回调
 * 前端组件可以注册此回调来显示错误提示
 */
export let onApiError = null

/**
 * 注册 API 错误处理回调
 * @param {Function} callback - (errorMessage: string) => void
 */
export function setOnApiError(callback) {
  onApiError = callback
}

/**
 * 显示 API 错误提示
 * @param {string} message
 */
function notifyApiError(message) {
  if (onApiError) {
    onApiError(message)
  }
  console.error('[API Error]', message)
}

// 响应拦截器：统一处理 API 错误
http.interceptors.response.use(
  response => response,
  error => {
    let errorMessage = ''

    if (error.code === 'ERR_NETWORK') {
      errorMessage = '网络连接失败，请检查后端服务是否已启动（http://localhost:8123）'
    } else if (error.code === 'ECONNABORTED') {
      errorMessage = '请求超时，请稍后重试'
    } else if (error.response) {
      const status = error.response.status
      const data = error.response.data || {}

      if (status === 401) {
        errorMessage = data.error || 'API Key 验证失败，请检查后端配置文件中的 DEEPSEEK_API_KEY 是否有效'
      } else if (status === 403) {
        errorMessage = data.error || 'API 访问被拒绝，请检查 API Key 权限'
      } else if (status === 429) {
        errorMessage = 'API 请求频率过高，请稍后重试'
      } else if (status >= 500) {
        errorMessage = data.error || `服务器内部错误 (${status})，请联系管理员`
      } else {
        errorMessage = data.error || `请求失败 (${status})`
      }
    } else {
      errorMessage = error.message || '未知网络错误，请检查连接'
    }

    notifyApiError(errorMessage)
    return Promise.reject(error)
  }
)