import request from '@/utils/request.js'

/**
 * 风险检测 - 文本评估
 * @param {string} text - 待检测文本
 * @returns {Promise}
 */
export function assessRisk(text) {
  return request({
    url: '/api/v1/risk/assess',
    method: 'POST',
    data: { text }
  })
}

/**
 * 获取检测报告详情
 * @param {string} reportId - 报告ID
 * @returns {Promise}
 */
export function getReport(reportId) {
  return request({
    url: `/api/v1/report/${reportId}`,
    method: 'GET'
  })
}

/**
 * 获取检测历史记录
 * @param {number} [page=1] - 页码
 * @param {number} [size=10] - 每页条数
 * @returns {Promise}
 */
export function getHistory(page = 1, size = 10) {
  return request({
    url: '/api/v1/history',
    method: 'GET',
    data: { page, size }
  })
}

/**
 * 获取用户信息
 * @returns {Promise}
 */
export function getUserProfile() {
  return request({
    url: '/api/v1/user/profile',
    method: 'GET'
  })
}