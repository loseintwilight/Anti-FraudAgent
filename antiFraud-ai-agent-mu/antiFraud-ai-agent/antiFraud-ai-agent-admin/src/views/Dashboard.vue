<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useDashboardStore } from '../store/dashboard.js'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { LineChart, PieChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

use([
  LineChart,
  PieChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
  CanvasRenderer,
])

const router = useRouter()
const dashboardStore = useDashboardStore()

const recentAlerts = ref([
  {
    id: 1001,
    userName: '王**',
    content: '向陌生账户转账 5 万元，疑似刷单诈骗',
    riskLevel: 'high',
    time: '2026-07-14 09:45:00',
    status: '待处理',
  },
  {
    id: 1002,
    userName: '李**',
    content: '接到冒充公检法诈骗电话，通话时长 45 分钟',
    riskLevel: 'high',
    time: '2026-07-14 09:30:00',
    status: '处理中',
  },
  {
    id: 1003,
    userName: '赵**',
    content: '点击不明链接并填写银行卡信息',
    riskLevel: 'medium',
    time: '2026-07-14 08:55:00',
    status: '待处理',
  },
  {
    id: 1004,
    userName: '孙**',
    content: '下载虚假投资理财 APP 并充值 2 万元',
    riskLevel: 'high',
    time: '2026-07-14 08:20:00',
    status: '已处理',
  },
  {
    id: 1005,
    userName: '周**',
    content: '收到冒充客服退款诈骗短信',
    riskLevel: 'low',
    time: '2026-07-14 07:50:00',
    status: '待处理',
  },
])

const statsCards = computed(() => [
  {
    label: '今日检测数',
    value: dashboardStore.stats.todayDetections,
    change: dashboardStore.stats.todayDetectionChange,
    icon: 'Search',
    color: 'blue',
  },
  {
    label: '待处理预警',
    value: dashboardStore.stats.pendingAlerts,
    change: dashboardStore.stats.pendingAlertChange,
    icon: 'WarningFilled',
    color: 'orange',
  },
  {
    label: '高风险用户',
    value: dashboardStore.stats.highRiskUsers,
    change: dashboardStore.stats.highRiskChange,
    icon: 'UserFilled',
    color: 'red',
  },
  {
    label: '本月拦截数',
    value: dashboardStore.stats.monthlyInterceptions,
    change: dashboardStore.stats.interceptionChange,
    icon: 'Lock',
    color: 'green',
  },
])

const trendOption = computed(() => ({
  title: {
    text: '风险趋势',
    textStyle: {
      fontSize: 14,
      fontWeight: 600,
    },
    left: 'center',
    top: 0,
  },
  tooltip: {
    trigger: 'axis',
    formatter: function (params) {
      const p = params[0]
      return `${p.axisValue}<br/>检测数: ${p.value}`
    },
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    top: '15%',
    containLabel: true,
  },
  xAxis: {
    type: 'category',
    data: dashboardStore.trendData.map((d) => d.date),
    boundaryGap: false,
    axisLabel: {
      fontSize: 12,
    },
  },
  yAxis: {
    type: 'value',
    splitLine: {
      lineStyle: {
        type: 'dashed',
      },
    },
  },
  series: [
    {
      type: 'line',
      data: dashboardStore.trendData.map((d) => d.value),
      smooth: true,
      lineStyle: {
        width: 3,
        color: '#409EFF',
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' },
          ],
        },
      },
      itemStyle: {
        color: '#409EFF',
      },
      markPoint: {
        data: [
          { type: 'max', name: '最大值' },
          { type: 'min', name: '最小值' },
        ],
      },
    },
  ],
}))

const pieOption = computed(() => ({
  title: {
    text: '诈骗类型分布',
    textStyle: {
      fontSize: 14,
      fontWeight: 600,
    },
    left: 'center',
    top: 0,
  },
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c} ({d}%)',
  },
  legend: {
    orient: 'vertical',
    right: '5%',
    top: 'center',
    itemWidth: 12,
    itemHeight: 12,
  },
  series: [
    {
      type: 'pie',
      radius: ['40%', '65%'],
      center: ['35%', '55%'],
      avoidLabelOverlap: true,
      itemStyle: {
        borderRadius: 6,
        borderColor: '#fff',
        borderWidth: 2,
      },
      label: {
        show: false,
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 14,
          fontWeight: 'bold',
        },
      },
      labelLine: {
        show: false,
      },
      data: dashboardStore.fraudTypeDistribution.map((item) => ({
        name: item.name,
        value: item.value,
      })),
      color: ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399'],
    },
  ],
}))

function getRiskTagType(level) {
  const map = { high: 'danger', medium: 'warning', low: 'info' }
  return map[level] || 'info'
}

function getRiskLabel(level) {
  const map = { high: '高风险', medium: '中风险', low: '低风险' }
  return map[level] || '未知'
}

function getStatusTagType(status) {
  const map = { '待处理': 'danger', '处理中': 'warning', '已处理': 'success' }
  return map[status] || 'info'
}

function viewAlertDetail(row) {
  router.push('/alerts')
}

onMounted(() => {
  dashboardStore.fetchDashboardStats()
})
</script>

<template>
  <div class="dashboard-page">
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div
        v-for="(card, index) in statsCards"
        :key="index"
        class="stats-card"
      >
        <div class="stats-icon" :class="card.color">
          <el-icon :size="28">
            <component :is="card.icon" />
          </el-icon>
        </div>
        <div class="stats-info">
          <div class="stats-label">{{ card.label }}</div>
          <div class="stats-value">{{ card.value.toLocaleString() }}</div>
          <div class="stats-change" :class="card.change >= 0 ? 'up' : 'down'">
            <el-icon :size="12">
              <Top v-if="card.change >= 0" />
              <Bottom v-else />
            </el-icon>
            {{ Math.abs(card.change) }}% 较昨日
          </div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px">
      <div class="chart-container">
        <VChart :option="trendOption" autoresize class="chart-box" />
      </div>
      <div class="chart-container">
        <VChart :option="pieOption" autoresize class="chart-box" />
      </div>
    </div>

    <!-- 最近预警列表 -->
    <div class="page-container">
      <div class="page-header">
        <h2>最近的预警</h2>
        <el-button type="primary" size="small" @click="router.push('/alerts')">
          查看全部
        </el-button>
      </div>
      <el-table :data="recentAlerts" stripe style="width: 100%">
        <el-table-column prop="id" label="预警 ID" width="80" />
        <el-table-column prop="userName" label="用户" width="100" />
        <el-table-column prop="content" label="内容摘要" min-width="300" show-overflow-tooltip />
        <el-table-column prop="riskLevel" label="风险等级" width="100">
          <template #default="{ row }">
            <el-tag :type="getRiskTagType(row.riskLevel)" size="small" effect="dark">
              {{ getRiskLabel(row.riskLevel) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="time" label="检测时间" width="170" />
        <el-table-column prop="status" label="处理状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewAlertDetail(row)">
              查看
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<style scoped>
.dashboard-page {
  max-width: 1600px;
  margin: 0 auto;
}
</style>