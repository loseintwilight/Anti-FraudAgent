<template>
  <view class="page-container">
    <view class="loading-container" v-if="loading">
      <text class="loading-text">加载中...</text>
    </view>

    <template v-else-if="report">
      <!-- 风险总览卡片 -->
      <view class="overview-card" :style="{ background: getOverviewBg() }">
        <view class="overview-header">
          <text class="overview-title">风险检测报告</text>
          <risk-badge :level="report.riskLevel" />
        </view>
        <view class="overview-score">
          <text class="score-number" :style="{ color: getScoreColor() }">{{ report.score }}</text>
          <text class="score-unit">分</text>
        </view>
        <view class="overview-time">
          <text class="time-label">检测时间：</text>
          <text class="time-value">{{ report.detectTime || report.createTime || '--' }}</text>
        </view>
      </view>

      <!-- 详细信息卡片 -->
      <view class="detail-card">
        <view class="detail-section">
          <text class="section-title">&#x1F4CB; 基本信息</text>
          <view class="info-row">
            <text class="info-label">风险等级</text>
            <risk-badge :level="report.riskLevel" />
          </view>
          <view class="info-row">
            <text class="info-label">风险评分</text>
            <text class="info-value" :style="{ color: getScoreColor() }">{{ report.score }} 分</text>
          </view>
          <view class="info-row" v-if="report.fraudType">
            <text class="info-label">诈骗类型</text>
            <text class="info-value">{{ report.fraudType }}</text>
          </view>
          <view class="info-row">
            <text class="info-label">检测时间</text>
            <text class="info-value">{{ report.detectTime || report.createTime || '--' }}</text>
          </view>
        </view>

        <view class="divider"></view>

        <view class="detail-section" v-if="report.keywords && report.keywords.length > 0">
          <text class="section-title">&#x1F50D; 匹配关键词</text>
          <view class="keyword-list">
            <text class="keyword-tag" v-for="(kw, index) in report.keywords" :key="index">{{ kw }}</text>
          </view>
        </view>

        <view class="divider" v-if="report.keywords && report.keywords.length > 0"></view>

        <view class="detail-section" v-if="report.suggestion">
          <text class="section-title">&#x1F4AC; AI 建议</text>
          <view class="suggestion-box">
            <text class="suggestion-text">{{ report.suggestion }}</text>
          </view>
        </view>

        <view class="divider" v-if="report.suggestion && report.persuasion"></view>

        <view class="detail-section" v-if="report.persuasion">
          <text class="section-title">&#x1F4A1; 劝导话术</text>
          <view class="persuasion-box">
            <text class="persuasion-text">{{ report.persuasion }}</text>
          </view>
        </view>
      </view>

      <!-- 底部操作按钮 -->
      <view class="action-bar">
        <button class="action-btn share-btn" open-type="share">
          <text class="btn-icon">&#x1F517;</text>
          <text class="btn-text">分享报告</text>
        </button>
        <button class="action-btn report-btn" @tap="handleReport">
          <text class="btn-icon">&#x1F6A8;</text>
          <text class="btn-text">举报</text>
        </button>
      </view>
    </template>

    <view class="empty-container" v-else>
      <text class="empty-text">暂无报告数据</text>
    </view>
  </view>
</template>

<script setup>
import { ref, onLoad } from 'vue'
import { getReport } from '@/api/index.js'
import RiskBadge from '@/components/risk-badge/risk-badge.vue'

const report = ref(null)
const loading = ref(true)

onLoad(async (options) => {
  const reportId = options.reportId
  if (!reportId) {
    loading.value = false
    return
  }
  try {
    const res = await getReport(reportId)
    report.value = res.data || res
  } catch (err) {
    uni.showToast({ title: '获取报告失败', icon: 'none' })
  } finally {
    loading.value = false
  }
})

function getScoreColor() {
  if (!report.value) return '#909399'
  const score = report.value.score
  if (score >= 80) return '#F56C6C'
  if (score >= 60) return '#E6A23C'
  if (score >= 30) return '#67C23A'
  return '#909399'
}

function getOverviewBg() {
  if (!report.value) return 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
  const level = report.value.riskLevel
  switch (level) {
    case 'LOW':
      return 'linear-gradient(135deg, #67C23A 0%, #95de64 100%)'
    case 'MEDIUM':
      return 'linear-gradient(135deg, #E6A23C 0%, #f5c542 100%)'
    case 'HIGH':
      return 'linear-gradient(135deg, #F56C6C 0%, #fa8c8c 100%)'
    case 'CRITICAL':
      return 'linear-gradient(135deg, #F56C6C 0%, #d9363e 100%)'
    default:
      return 'linear-gradient(135deg, #909399 0%, #b0b3b8 100%)'
  }
}

function handleReport() {
  uni.showModal({
    title: '确认举报',
    content: '您确认要举报此内容为诈骗信息吗？',
    success: (res) => {
      if (res.confirm) {
        uni.showToast({ title: '举报成功，感谢您的贡献', icon: 'success' })
      }
    }
  })
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding-bottom: 120rpx;
}

.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 60vh;
}

.loading-text {
  font-size: 28rpx;
  color: #909399;
}

.empty-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 60vh;
}

.empty-text {
  font-size: 28rpx;
  color: #909399;
}

/* 概览卡片 */
.overview-card {
  margin: 24rpx 32rpx;
  padding: 40rpx 32rpx;
  border-radius: 24rpx;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.1);
}

.overview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24rpx;
}

.overview-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #ffffff;
}

.overview-score {
  display: flex;
  align-items: baseline;
  justify-content: center;
  margin-bottom: 16rpx;
}

.score-number {
  font-size: 96rpx;
  font-weight: 800;
  color: #ffffff;
  line-height: 1;
}

.score-unit {
  font-size: 32rpx;
  color: rgba(255, 255, 255, 0.8);
  margin-left: 8rpx;
}

.overview-time {
  display: flex;
  justify-content: center;
}

.time-label {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.7);
}

.time-value {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.9);
}

/* 详细信息卡片 */
.detail-card {
  margin: 0 32rpx 24rpx;
  background-color: #ffffff;
  border-radius: 24rpx;
  padding: 32rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.06);
}

.detail-section {
  margin-bottom: 8rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 20rpx;
  display: block;
}

.info-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16rpx 0;
}

.info-label {
  font-size: 28rpx;
  color: #606266;
}

.info-value {
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
}

.divider {
  height: 1rpx;
  background-color: #ebeef5;
  margin: 20rpx 0;
}

.keyword-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-top: 16rpx;
}

.keyword-tag {
  font-size: 24rpx;
  color: #409EFF;
  background-color: #ecf5ff;
  padding: 8rpx 20rpx;
  border-radius: 24rpx;
}

.suggestion-box,
.persuasion-box {
  background-color: #f0f9eb;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-top: 16rpx;
}

.persuasion-box {
  background-color: #fff7e6;
}

.suggestion-text {
  font-size: 28rpx;
  color: #606266;
  line-height: 1.8;
}

.persuasion-text {
  font-size: 28rpx;
  color: #606266;
  line-height: 1.8;
}

/* 底部操作栏 */
.action-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  padding: 20rpx 32rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  background-color: #ffffff;
  border-top: 1rpx solid #ebeef5;
  gap: 24rpx;
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 88rpx;
  border-radius: 44rpx;
  font-size: 28rpx;
  border: none;
  padding: 0;
  margin: 0;
}

.share-btn {
  background-color: #ecf5ff;
  color: #409EFF;
}

.report-btn {
  background-color: #fef0f0;
  color: #F56C6C;
}

.btn-icon {
  margin-right: 8rpx;
  font-size: 28rpx;
}

.btn-text {
  font-weight: 500;
}
</style>