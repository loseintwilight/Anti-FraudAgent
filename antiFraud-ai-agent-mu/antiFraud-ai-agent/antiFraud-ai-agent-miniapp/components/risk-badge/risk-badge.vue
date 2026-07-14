<template>
  <view class="risk-badge" :style="{ backgroundColor: bgColor }">
    <text class="risk-text">{{ label }}</text>
  </view>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  level: {
    type: String,
    default: 'UNKNOWN'
  }
})

const riskConfig = {
  LOW: { label: '低', color: '#67C23A' },
  MEDIUM: { label: '中', color: '#E6A23C' },
  HIGH: { label: '高', color: '#F56C6C' },
  CRITICAL: { label: '极高', color: '#F56C6C' },
  UNKNOWN: { label: '未知', color: '#909399' }
}

const bgColor = computed(() => {
  const config = riskConfig[props.level] || riskConfig.UNKNOWN
  return config.color
})

const label = computed(() => {
  const config = riskConfig[props.level] || riskConfig.UNKNOWN
  return config.label
})
</script>

<style scoped>
.risk-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 6rpx 16rpx;
  border-radius: 20rpx;
  min-width: 60rpx;
}

.risk-text {
  font-size: 22rpx;
  color: #ffffff;
  font-weight: 600;
  line-height: 1.4;
}
</style>