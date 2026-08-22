<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { getDashboardStats, getRiskDistribution, getDetectionTrend, getLatestRecords } from '@/api/dashboard'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const loading = ref(true)
const stats = ref({
  totalDetections: 0,
  highRiskCount: 0,
  todayNew: 0,
  pendingBlacklist: 0,
})

const latestRecords = ref([])
let pieChart = null
let lineChart = null

async function fetchData() {
  loading.value = true
  try {
    const [statsRes, riskRes, trendRes, recordsRes] = await Promise.allSettled([
      getDashboardStats(),
      getRiskDistribution(),
      getDetectionTrend(),
      getLatestRecords(),
    ])

    if (statsRes.status === 'fulfilled' && statsRes.value) {
      const d = statsRes.value.data || statsRes.value
      stats.value = {
        totalDetections: d.totalDetections ?? d.total ?? 0,
        highRiskCount: d.highRiskCount ?? d.highRisk ?? 0,
        todayNew: d.todayNew ?? d.today ?? 0,
        pendingBlacklist: d.pendingBlacklist ?? d.pending ?? 0,
      }
    }

    if (recordsRes.status === 'fulfilled' && recordsRes.value) {
      latestRecords.value = recordsRes.value.data || recordsRes.value.records || []
    }

    // 渲染图表
    nextTick(() => {
      const riskData = riskRes.status === 'fulfilled' ? (riskRes.value.data || riskRes.value) : null
      const trendData = trendRes.status === 'fulfilled' ? (trendRes.value.data || trendRes.value) : null
      renderPieChart(riskData)
      renderLineChart(trendData)
    })
  } catch (err) {
    ElMessage.error('获取仪表盘数据失败')
  } finally {
    loading.value = false
  }
}

function renderPieChart(data) {
  const el = document.getElementById('pieChart')
  if (!el) return
  if (pieChart) pieChart.dispose()
  pieChart = echarts.init(el)

  const defaultData = [
    { name: '低风险', value: 45 },
    { name: '中风险', value: 30 },
    { name: '高风险', value: 18 },
    { name: '极高风险', value: 7 },
  ]

  const seriesData = data?.list || data || defaultData

  pieChart.setOption({
    tooltip: { trigger: 'item' },
    legend: {
      bottom: 0,
      textStyle: { color: '#606266' },
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '45%'],
        avoidLabelOverlap: false,
        label: { show: false },
        emphasis: {
          label: { show: true, fontSize: 14, fontWeight: 'bold' },
        },
        data: seriesData,
        color: ['#67C23A', '#E6A23C', '#F56C6C', '#ff4d4f'],
      },
    ],
  })
}

function renderLineChart(data) {
  const el = document.getElementById('lineChart')
  if (!el) return
  if (lineChart) lineChart.dispose()
  lineChart = echarts.init(el)

  const defaultData = {
    dates: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
    counts: [120, 132, 101, 134, 90, 230, 210],
  }

  const chartData = data || defaultData

  lineChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: {
      data: ['检测次数'],
      textStyle: { color: '#606266' },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: chartData.dates || [],
      axisLine: { lineStyle: { color: '#e4e7ed' } },
      axisLabel: { color: '#909399' },
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#f0f2f5' } },
      axisLabel: { color: '#909399' },
    },
    series: [
      {
        name: '检测次数',
        type: 'line',
        smooth: true,
        lineStyle: { color: '#165DFF', width: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(22, 93, 255, 0.3)' },
            { offset: 1, color: 'rgba(22, 93, 255, 0.05)' },
          ]),
        },
        itemStyle: { color: '#165DFF' },
        data: chartData.counts || [],
      },
    ],
  })
}

function handleResize() {
  pieChart?.resize()
  lineChart?.resize()
}

onMounted(() => {
  fetchData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  pieChart?.dispose()
  lineChart?.dispose()
})
</script>

<template>
  <div class="dashboard">
    <div class="page-title">仪表盘</div>

    <div v-loading="loading" class="dashboard-content">
      <!-- 统计卡片 -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon total">
            <el-icon :size="28"><DataBoard /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.totalDetections.toLocaleString() }}</span>
            <span class="stat-label">总检测次数</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon high-risk">
            <el-icon :size="28"><WarningFilled /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.highRiskCount.toLocaleString() }}</span>
            <span class="stat-label">高风险预警数</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon today">
            <el-icon :size="28"><Timer /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.todayNew.toLocaleString() }}</span>
            <span class="stat-label">今日新增</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon pending">
            <el-icon :size="28"><List /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.pendingBlacklist.toLocaleString() }}</span>
            <span class="stat-label">待处理黑名单</span>
          </div>
        </div>
      </div>

      <!-- 图表区域 -->
      <div class="charts-grid">
        <div class="chart-card">
          <h3 class="chart-title">风险等级分布</h3>
          <div id="pieChart" class="chart-container"></div>
        </div>
        <div class="chart-card">
          <h3 class="chart-title">近期检测趋势</h3>
          <div id="lineChart" class="chart-container"></div>
        </div>
      </div>

      <!-- 最新检测记录 -->
      <div class="records-card">
        <h3 class="chart-title">最新检测记录</h3>
        <el-table :data="latestRecords" stripe style="width: 100%" v-if="latestRecords.length > 0">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="userId" label="用户ID" width="100" />
          <el-table-column prop="inputType" label="输入类型" width="100" />
          <el-table-column prop="fraudType" label="诈骗类型" min-width="120" />
          <el-table-column prop="riskLevel" label="风险等级" width="100">
            <template #default="{ row }">
              <el-tag
                :type="row.riskLevel === 'HIGH' || row.riskLevel === 'CRITICAL' ? 'danger' : row.riskLevel === 'MEDIUM' ? 'warning' : 'success'"
                size="small"
              >
                {{ row.riskLevel }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="score" label="评分" width="80" />
          <el-table-column prop="createTime" label="时间" min-width="160" />
        </el-table>
        <el-empty v-else description="暂无检测记录" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  padding: 0;
}

.dashboard-content {
  min-height: 400px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon.total {
  background: rgba(22, 93, 255, 0.1);
  color: #165DFF;
}

.stat-icon.high-risk {
  background: rgba(245, 108, 108, 0.1);
  color: #F56C6C;
}

.stat-icon.today {
  background: rgba(103, 194, 58, 0.1);
  color: #67C23A;
}

.stat-icon.pending {
  background: rgba(230, 162, 60, 0.1);
  color: #E6A23C;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #909399;
}

.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 20px;
}

.chart-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.chart-title {
  font-size: 15px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 16px;
}

.chart-container {
  width: 100%;
  height: 300px;
}

.records-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>