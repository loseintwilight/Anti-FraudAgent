<script setup>
import { computed, watch, ref } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { HeatmapChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, VisualMapComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

use([HeatmapChart, GridComponent, TooltipComponent, VisualMapComponent, CanvasRenderer])

const props = defineProps({
  data: {
    type: Array,
    default: () => [],
  },
  title: {
    type: String,
    default: '区域风险热力图',
  },
})

const chartData = computed(() => {
  if (!props.data || props.data.length === 0) {
    return generateMockData()
  }
  return props.data
})

function generateMockData() {
  const hours = ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00']
  const districts = ['朝阳区', '海淀区', '丰台区', '通州区', '大兴区', '东城区', '西城区', '昌平区']
  const data = []
  for (let i = 0; i < districts.length; i++) {
    for (let j = 0; j < hours.length; j++) {
      data.push([j, i, Math.round(Math.random() * 100)])
    }
  }
  return { hours, districts, data }
}

const option = computed(() => ({
  title: {
    text: props.title,
    textStyle: {
      fontSize: 14,
      fontWeight: 600,
    },
    left: 'center',
    top: 0,
  },
  tooltip: {
    position: 'top',
    formatter: function (params) {
      const d = chartData.value
      return `${d.districts[params.value[1]]}<br/>${d.hours[params.value[0]]}<br/>风险指数: ${params.value[2]}`
    },
  },
  grid: {
    left: '8%',
    right: '10%',
    bottom: '8%',
    top: '15%',
    containLabel: true,
  },
  xAxis: {
    type: 'category',
    data: chartData.value.hours,
    splitArea: {
      show: true,
    },
    axisLabel: {
      fontSize: 11,
    },
  },
  yAxis: {
    type: 'category',
    data: chartData.value.districts,
    splitArea: {
      show: true,
    },
    axisLabel: {
      fontSize: 11,
    },
  },
  visualMap: {
    min: 0,
    max: 100,
    calculable: true,
    orient: 'horizontal',
    left: 'center',
    bottom: 0,
    inRange: {
      color: ['#ecf5ff', '#b3d8ff', '#66b1ff', '#409eff', '#337ecc', '#1d5b9e'],
    },
  },
  series: [
    {
      type: 'heatmap',
      data: chartData.value.data,
      label: {
        show: false,
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.5)',
        },
      },
    },
  ],
}))
</script>

<template>
  <div class="risk-heatmap">
    <VChart :option="option" autoresize class="chart-content" />
  </div>
</template>

<style scoped>
.risk-heatmap {
  width: 100%;
  height: 100%;
  min-height: 400px;
}

.chart-content {
  width: 100%;
  height: 100%;
  min-height: 400px;
}
</style>