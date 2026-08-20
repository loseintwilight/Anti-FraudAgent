import request from '@/utils/request'

/**
 * 获取检测记录列表
 * @param {Object} params 查询参数
 */
export function getDetectionList(params) {
  return request.get('/detection/list', { params })
}

/**
 * 获取检测记录详情
 * @param {number|string} id 记录ID
 */
export function getDetectionDetail(id) {
  return request.get(`/detection/${id}`)
}

/**
 * 删除检测记录
 * @param {number|string} id 记录ID
 */
export function deleteDetection(id) {
  return request.delete(`/detection/${id}`)
}