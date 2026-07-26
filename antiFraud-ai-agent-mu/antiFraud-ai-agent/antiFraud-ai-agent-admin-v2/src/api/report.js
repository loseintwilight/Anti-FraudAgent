import request from '@/utils/request'

/**
 * 获取报告列表
 * @param {Object} params 查询参数
 */
export function getReportList(params) {
  return request.get('/report/list', { params })
}

/**
 * 获取报告详情
 * @param {number|string} id 报告ID
 */
export function getReportDetail(id) {
  return request.get(`/report/${id}`)
}

/**
 * 导出报告
 * @param {number|string} id 报告ID
 */
export function exportReport(id) {
  return request.get(`/report/export/${id}`, { responseType: 'blob' })
}

/**
 * 删除报告
 * @param {number|string} id 报告ID
 */
export function deleteReport(id) {
  return request.delete(`/report/${id}`)
}