import request from '@/utils/request'

/**
 * 获取黑名单列表
 * @param {Object} params 查询参数
 */
export function getBlacklist(params) {
  return request.get('/blacklist/list', { params })
}

/**
 * 新增黑名单
 * @param {Object} data 黑名单数据
 */
export function addBlacklist(data) {
  return request.post('/blacklist', data)
}

/**
 * 更新黑名单
 * @param {Object} data 黑名单数据
 */
export function updateBlacklist(data) {
  return request.put('/blacklist', data)
}

/**
 * 删除黑名单
 * @param {number|string} id 黑名单ID
 */
export function deleteBlacklist(id) {
  return request.delete(`/blacklist/${id}`)
}

/**
 * 启用/禁用黑名单
 * @param {number|string} id 黑名单ID
 * @param {number} status 状态 0-禁用 1-启用
 */
export function toggleBlacklistStatus(id, status) {
  return request.put(`/blacklist/${id}/status`, { status })
}