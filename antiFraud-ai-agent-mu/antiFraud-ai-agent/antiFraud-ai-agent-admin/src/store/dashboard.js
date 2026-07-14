import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getDashboardStats, getAlertList } from '../api/index.js'

export const useDashboardStore = defineStore('dashboard', () => {
  const stats = ref({
    todayDetections: 0,
    pendingAlerts: 0,
    highRiskUsers: 0,
    monthlyInterceptions: 0,
    todayDetectionChange: 0,
    pendingAlertChange: 0,
    highRiskChange: 0,
    interceptionChange: 0,
  })

  const alertList = ref([])
  const trendData = ref([])
  const fraudTypeDistribution = ref([])
  const loading = ref(false)

  async function fetchDashboardStats() {
    loading.value = true
    try {
      const res = await getDashboardStats()
      if (res.data) {
        stats.value = {
          todayDetections: res.data.todayDetections ?? 0,
          pendingAlerts: res.data.pendingAlerts ?? 0,
          highRiskUsers: res.data.highRiskUsers ?? 0,
          monthlyInterceptions: res.data.monthlyInterceptions ?? 0,
          todayDetectionChange: res.data.todayDetectionChange ?? 0,
          pendingAlertChange: res.data.pendingAlertChange ?? 0,
          highRiskChange: res.data.highRiskChange ?? 0,
          interceptionChange: res.data.interceptionChange ?? 0,
        }
        trendData.value = res.data.trendData ?? []
        fraudTypeDistribution.value = res.data.fraudTypeDistribution ?? []
      }
    } catch (error) {
      console.error('获取看板数据失败:', error)
      // 使用模拟数据
      stats.value = {
        todayDetections: 1286,
        pendingAlerts: 47,
        highRiskUsers: 23,
        monthlyInterceptions: 8562,
        todayDetectionChange: 12.5,
        pendingAlertChange: -8.3,
        highRiskChange: 5.2,
        interceptionChange: 18.7,
      }
      trendData.value = [
        { date: '2026-01', value: 820 },
        { date: '2026-02', value: 932 },
        { date: '2026-03', value: 901 },
        { date: '2026-04', value: 1234 },
        { date: '2026-05', value: 1150 },
        { date: '2026-06', value: 1286 },
      ]
      fraudTypeDistribution.value = [
        { name: '刷单诈骗', value: 35 },
        { name: '冒充客服', value: 25 },
        { name: '投资理财', value: 20 },
        { name: '网络贷款', value: 12 },
        { name: '其他', value: 8 },
      ]
    } finally {
      loading.value = false
    }
  }

  async function fetchAlertList(params) {
    loading.value = true
    try {
      const res = await getAlertList(params)
      alertList.value = res.data?.list ?? []
    } catch (error) {
      console.error('获取预警列表失败:', error)
      alertList.value = []
    } finally {
      loading.value = false
    }
  }

  return {
    stats,
    alertList,
    trendData,
    fraudTypeDistribution,
    loading,
    fetchDashboardStats,
    fetchAlertList,
  }
})