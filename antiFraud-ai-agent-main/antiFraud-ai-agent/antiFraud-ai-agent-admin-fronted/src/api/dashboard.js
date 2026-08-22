import request from '@/utils/request'

/**
 * 获取仪表盘统计数据
 */
export function getDashboardStats() {
  return request.get('/dashboard/stats')
}

/**
 * 获取风险等级分布
 */
export function getRiskDistribution() {
  return request.get('/dashboard/risk-distribution')
}

/**
 * 获取检测趋势
 */
export function getDetectionTrend() {
  return request.get('/dashboard/detection-trend')
}

/**
 * 获取最新检测记录
 */
export function getLatestRecords() {
  return request.get('/dashboard/latest-records')
}