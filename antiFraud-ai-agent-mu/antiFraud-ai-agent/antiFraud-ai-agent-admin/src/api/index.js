import axios from 'axios'

const http = axios.create({
  baseURL: '/api',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器：添加 Authorization token
http.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('admin_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器：统一错误处理
http.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res.code !== undefined && res.code !== 200) {
      console.error('API 错误:', res.message || '未知错误')
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    return res
  },
  (error) => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          localStorage.removeItem('admin_token')
          window.location.reload()
          break
        case 403:
          console.error('没有权限访问该资源')
          break
        case 404:
          console.error('请求的资源不存在')
          break
        case 500:
          console.error('服务器内部错误')
          break
        default:
          console.error(`请求失败: ${error.response.status}`)
      }
    } else if (error.request) {
      console.error('网络错误，请检查网络连接')
    }
    return Promise.reject(error)
  }
)

// ===== API 方法 =====

/**
 * 获取看板统计数据
 */
export function getDashboardStats() {
  return http.get('/dashboard/stats')
}

/**
 * 获取预警列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.pageSize - 每页条数
 * @param {string} params.riskLevel - 风险等级
 * @param {string} params.status - 处理状态
 * @param {string} params.startTime - 开始时间
 * @param {string} params.endTime - 结束时间
 */
export function getAlertList(params) {
  return http.get('/alerts', { params })
}

/**
 * 更新预警状态
 * @param {number|string} id - 预警 ID
 * @param {string} status - 新状态
 */
export function updateAlertStatus(id, status) {
  return http.put(`/alerts/${id}/status`, { status })
}

/**
 * 获取网格案件
 * @param {Object} params - 查询参数
 */
export function getGridCases(params) {
  return http.get('/grid/cases', { params })
}

/**
 * 获取案件详情
 * @param {number|string} id - 案件 ID
 */
export function getCaseDetail(id) {
  return http.get(`/cases/${id}`)
}

/**
 * 获取统计报表数据
 * @param {Object} params - 查询参数
 */
export function getReportStats(params) {
  return http.get('/stats/report', { params })
}

export default http