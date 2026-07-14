<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { BarChart, PieChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

use([
  BarChart,
  PieChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
  CanvasRenderer,
])

const dateRange = ref('7d')
const customDateRange = ref([])

const dateRangeOptions = [
  { value: '7d', label: '最近 7 天' },
  { value: '30d', label: '最近 30 天' },
  { value: 'custom', label: '自定义' },
]

const mockData = {
  '7d': {
    trend: {
      categories: ['07-08', '07-09', '07-10', '07-11', '07-12', '07-13', '07-14'],
      series: [
        { name: '刷单诈骗', data: [12, 15, 8, 20, 18, 14, 22] },
        { name: '冒充客服', data: [8, 10, 12, 7, 15, 11, 9] },
        { name: '投资理财', data: [6, 5, 9, 11, 7, 8, 13] },
        { name: '网络贷款', data: [4, 6, 3, 5, 7, 4, 6] },
        { name: '其他', data: [3, 2, 4, 3, 5, 2, 4] },
      ],
    },
    ageDistribution: [
      { name: '18-25 岁', value: 18 },
      { name: '26-35 岁', value: 32 },
      { name: '36-45 岁', value: 25 },
      { name: '46-55 岁', value: 15 },
      { name: '55 岁以上', value: 10 },
    ],
    riskDistribution: [
      { name: '高风险', value: 28 },
      { name: '中风险', value: 45 },
      { name: '低风险', value: 27 },
    ],
  },
  '30d': {
    trend: {
      categories: ['06-15', '06-18', '06-21', '06-24', '06-27', '06-30', '07-03', '07-06', '07-09', '07-12'],
      series: [
        { name: '刷单诈骗', data: [45, 52, 38, 60, 55, 48, 62, 50, 58, 70] },
        { name: '冒充客服', data: [30, 35, 42, 28, 45, 38, 32, 40, 36, 42] },
        { name: '投资理财', data: [22, 18, 28, 35, 25, 30, 38, 28, 32, 40] },
        { name: '网络贷款', data: [15, 20, 12, 18, 22, 16, 20, 14, 18, 24] },
        { name: '其他', data: [10, 8, 12, 14, 9, 11, 13, 10, 8, 15] },
      ],
    },
    ageDistribution: [
      { name: '18-25 岁', value: 82 },
      { name: '26-35 岁', value: 145 },
      { name: '36-45 岁', value: 108 },
      { name: '46-55 岁', value: 65 },
      { name: '55 岁以上', value: 42 },
    ],
    riskDistribution: [
      { name: '高风险', value: 128 },
      { name: '中风险', value: 195 },
      { name: '低风险', value: 119 },
    ],
  },
}

const currentData = computed(() => {
  if (dateRange.value === 'custom') {
    return mockData['30d']
  }
  return mockData[dateRange.value] || mockData['7d']
})

const trendOption = computed(() => ({
  title: {
    text: '诈骗类型趋势图',
    textStyle: {
      fontSize: 14,
      fontWeight: 600,
    },
    left: 'center',
    top: 0,
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'shadow' },
  },
  legend: {
    type: 'scroll',
    top: 28,
    left: 'center',
    itemWidth: 12,
    itemHeight: 12,
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    top: '22%',
    containLabel: true,
  },
  xAxis: {
    type: 'category',
    data: currentData.value.trend.categories,
    axisLabel: {
      fontSize: 11,
    },
  },
  yAxis: {
    type: 'value',
    splitLine: {
      lineStyle: { type: 'dashed' },
    },
  },
  series: currentData.value.trend.series.map((s, idx) => ({
    type: 'bar',
    name: s.name,
    data: s.data,
    barWidth: '15%',
    barGap: '10%',
    itemStyle: {
      borderRadius: [2, 2, 0, 0],
      color: [
        '#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399',
      ][idx],
    },
  })),
  color: ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399'],
}))

const ageOption = computed(() => ({
  title: {
    text: '各年龄段受骗分布',
    textStyle: {
      fontSize: 14,
      fontWeight: 600,
    },
    left: 'center',
    top: 0,
  },
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c} 例 ({d}%)',
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
      data: currentData.value.ageDistribution.map((item) => ({
        name: item.name,
        value: item.value,
      })),
      color: ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399'],
    },
  ],
}))

const riskOption = computed(() => ({
  title: {
    text: '风险等级分布',
    textStyle: {
      fontSize: 14,
      fontWeight: 600,
    },
    left: 'center',
    top: 0,
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'shadow' },
    formatter: function (params) {
      const p = params[0]
      return `${p.name}<br/>数量: ${p.value} 例`
    },
  },
  grid: {
    left: '3%',
    right: '10%',
    bottom: '3%',
    top: '15%',
    containLabel: true,
  },
  xAxis: {
    type: 'value',
    splitLine: {
      lineStyle: { type: 'dashed' },
    },
    axisLabel: {
      fontSize: 11,
    },
  },
  yAxis: {
    type: 'category',
    data: currentData.value.riskDistribution.map((item) => item.name),
    axisLabel: {
      fontSize: 12,
    },
  },
  series: [
    {
      type: 'bar',
      data: currentData.value.riskDistribution.map((item) => ({
        value: item.value,
        itemStyle: {
          color:
            item.name === '高风险'
              ? '#F56C6C'
              : item.name === '中风险'
              ? '#E6A23C'
              : '#67C23A',
          borderRadius: [0, 4, 4, 0],
        },
      })),
      barWidth: '50%',
      label: {
        show: true,
        position: 'right',
        fontSize: 12,
        fontWeight: 600,
      },
    },
  ],
}))

function handleDateRangeChange() {
  if (dateRange.value !== 'custom') {
    customDateRange.value = []
  }
}

function handleExport() {
  ElMessage.success('报表导出中，请稍候...')
  setTimeout(() => {
    ElMessage.success('报表已生成，请查看下载目录')
  }, 2000)
}

function handlePreview() {
  ElMessage.info('报表预览功能开发中...')
}

onMounted(() => {})
</script>

<template>
  <div class="page-container">
    <div class="page-header">
      <h2>统计报表</h2>
      <div style="display: flex; gap: 8px">
        <el-button @click="handlePreview">
          <el-icon><View /></el-icon>
          预览
        </el-button>
        <el-button type="primary" @click="handleExport">
          <el-icon><Download /></el-icon>
          导出报表
        </el-button>
      </div>
    </div>

    <!-- 时间范围选择 -->
    <div class="filter-bar">
      <div class="filter-item">
        <span class="filter-label">时间范围：</span>
        <el-radio-group
          v-model="dateRange"
          @change="handleDateRangeChange"
        >
          <el-radio-button
            v-for="opt in dateRangeOptions"
            :key="opt.value"
            :value="opt.value"
          >
            {{ opt.label }}
          </el-radio-button>
        </el-radio-group>
      </div>
      <div v-if="dateRange === 'custom'" class="filter-item">
        <el-date-picker
          v-model="customDateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          style="width: 280px"
        />
      </div>
    </div>

    <!-- 图表区域 -->
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px">
      <div class="chart-container">
        <VChart :option="trendOption" autoresize class="chart-box" />
      </div>
      <div class="chart-container">
        <VChart :option="ageOption" autoresize class="chart-box" />
      </div>
    </div>

    <div class="chart-container">
      <VChart :option="riskOption" autoresize class="chart-box" style="height: 320px" />
    </div>

    <!-- 统计摘要 -->
    <div class="stats-summary">
      <div class="summary-header">
        <h3>数据摘要</h3>
      </div>
      <el-descriptions :column="4" border size="small">
        <el-descriptions-item label="案件总数">
          <span style="font-weight: 600; color: #409EFF">
            {{ currentData.riskDistribution.reduce((a, b) => a + b.value, 0) }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="高风险案件">
          <span style="font-weight: 600; color: #F56C6C">
            {{ currentData.riskDistribution[0].value }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="主要诈骗类型">
          <span style="font-weight: 600">
            {{ currentData.trend.series[0].name }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="高发年龄段">
          <span style="font-weight: 600">26-35 岁</span>
        </el-descriptions-item>
      </el-descriptions>
    </div>
  </div>
</template>

<style scoped>
.filter-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 6px;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 13px;
  color: #909399;
  white-space: nowrap;
}

.stats-summary {
  margin-top: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.summary-header {
  margin-bottom: 16px;
}

.summary-header h3 {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}
</style>