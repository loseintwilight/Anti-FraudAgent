<template>
  <view class="page-container">
    <!-- 顶部标题栏 -->
    <view class="header">
      <view class="header-title">
        <text class="title-icon">&#x1F6E1;</text>
        <text class="title-text">反诈卫士</text>
      </view>
      <risk-badge v-if="lastResult" :level="lastResult.riskLevel" />
    </view>

    <!-- 对话消息列表 -->
    <scroll-view
      class="message-list"
      scroll-y
      :scroll-top="scrollTop"
      @scrolltoupper="scrollToBottom"
      :ref="setScrollViewRef"
    >
      <view class="welcome-card" v-if="messages.length === 0">
        <view class="welcome-icon">&#x1F6E1;</view>
        <text class="welcome-title">反诈卫士</text>
        <text class="welcome-desc">请输入您收到的可疑信息，AI将为您智能检测诈骗风险</text>
        <view class="tip-list">
          <view class="tip-item">&#x1F4E5; 可疑短信内容</view>
          <view class="tip-item">&#x1F4F1; 陌生来电内容</view>
          <view class="tip-item">&#x1F4AC; 社交聊天记录</view>
          <view class="tip-item">&#x1F4B0; 投资理财信息</view>
        </view>
      </view>

      <view
        v-for="(msg, index) in messages"
        :key="index"
        class="message-item"
      >
        <!-- 用户消息 -->
        <view v-if="msg.role === 'user'" class="msg-row msg-row-user">
          <view class="msg-bubble msg-bubble-user">
            <text class="msg-text">{{ msg.content }}</text>
          </view>
          <view class="msg-avatar msg-avatar-user">我</view>
        </view>

        <!-- AI 检测结果 -->
        <view v-else class="msg-row msg-row-ai">
          <view class="msg-avatar msg-avatar-ai">AI</view>
          <view class="msg-bubble msg-bubble-ai">
            <view class="result-header">
              <risk-badge :level="msg.result.riskLevel" />
              <text class="fraud-type" v-if="msg.result.fraudType">诈骗类型：{{ msg.result.fraudType }}</text>
            </view>
            <view class="result-score">
              <text class="score-label">风险评分：</text>
              <text class="score-value" :style="{ color: getScoreColor(msg.result.score) }">{{ msg.result.score }}</text>
              <text class="score-suffix">分</text>
            </view>
            <view class="result-confidence" v-if="msg.result.confidence !== undefined">
              <text class="confidence-label">置信度：</text>
              <text class="confidence-value">{{ (msg.result.confidence * 100).toFixed(0) }}%</text>
            </view>
            <view class="result-suggestion" v-if="msg.result.suggestion">
              <text class="suggestion-label">&#x1F4AC; 建议：</text>
              <text class="suggestion-text">{{ msg.result.suggestion }}</text>
            </view>
            <view class="result-detail" v-if="msg.result.keywords && msg.result.keywords.length > 0">
              <text class="detail-label">&#x1F50D; 匹配关键词：</text>
              <view class="keyword-list">
                <text class="keyword-tag" v-for="(kw, ki) in msg.result.keywords" :key="ki">{{ kw }}</text>
              </view>
            </view>
            <view class="result-action">
              <text class="action-btn" @tap="goToReport(msg.result.reportId)">查看详细报告 &gt;</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 加载中状态 -->
      <view class="loading-row" v-if="isLoading">
        <view class="msg-avatar msg-avatar-ai">AI</view>
        <view class="loading-bubble">
          <text class="loading-dot">.</text>
          <text class="loading-dot">.</text>
          <text class="loading-dot">.</text>
        </view>
      </view>
    </scroll-view>

    <!-- 底部输入区 -->
    <view class="input-area">
      <chat-input
        :loading="isLoading"
        @submit="handleSubmit"
      />
    </view>
  </view>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { assessRisk } from '@/api/index.js'
import ChatInput from '@/components/chat-input/chat-input.vue'
import RiskBadge from '@/components/risk-badge/risk-badge.vue'

const messages = ref([])
const isLoading = ref(false)
const lastResult = ref(null)
const scrollTop = ref(0)
let scrollViewRef = null

function setScrollViewRef(el) {
  if (el) {
    scrollViewRef = el
  }
}

function scrollToBottom() {
  nextTick(() => {
    scrollTop.value = 999999
  })
}

function getScoreColor(score) {
  if (score >= 80) return '#F56C6C'
  if (score >= 60) return '#E6A23C'
  if (score >= 30) return '#67C23A'
  return '#909399'
}

async function handleSubmit(text) {
  messages.value.push({
    role: 'user',
    content: text
  })
  scrollToBottom()

  isLoading.value = true
  try {
    const res = await assessRisk(text)
    const result = res.data || res
    lastResult.value = result
    messages.value.push({
      role: 'ai',
      result
    })
    scrollToBottom()
  } catch (err) {
    messages.value.push({
      role: 'ai',
      result: {
        riskLevel: 'UNKNOWN',
        score: 0,
        fraudType: '检测失败',
        suggestion: '检测服务暂时不可用，请稍后重试。',
        keywords: []
      }
    })
    scrollToBottom()
  } finally {
    isLoading.value = false
  }
}

function goToReport(reportId) {
  if (!reportId) return
  uni.navigateTo({
    url: `/pages/report/index?reportId=${reportId}`
  })
}
</script>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f7fa;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 32rpx;
  background-color: #409EFF;
  flex-shrink: 0;
}

.header-title {
  display: flex;
  align-items: center;
}

.title-icon {
  font-size: 40rpx;
  margin-right: 12rpx;
}

.title-text {
  font-size: 36rpx;
  font-weight: 700;
  color: #ffffff;
}

.message-list {
  flex: 1;
  padding: 24rpx 32rpx;
  overflow-y: auto;
}

/* 欢迎卡片 */
.welcome-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60rpx 40rpx;
  background-color: #ffffff;
  border-radius: 24rpx;
  margin-top: 40rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
}

.welcome-icon {
  font-size: 80rpx;
  margin-bottom: 20rpx;
}

.welcome-title {
  font-size: 40rpx;
  font-weight: 700;
  color: #333;
  margin-bottom: 16rpx;
}

.welcome-desc {
  font-size: 28rpx;
  color: #909399;
  text-align: center;
  margin-bottom: 40rpx;
  line-height: 1.6;
}

.tip-list {
  width: 100%;
}

.tip-item {
  font-size: 28rpx;
  color: #606266;
  padding: 16rpx 24rpx;
  background-color: #f5f7fa;
  border-radius: 12rpx;
  margin-bottom: 16rpx;
}

/* 消息列表 */
.message-item {
  margin-bottom: 24rpx;
}

.msg-row {
  display: flex;
  align-items: flex-start;
}

.msg-row-user {
  justify-content: flex-end;
}

.msg-row-ai {
  justify-content: flex-start;
}

.msg-avatar {
  width: 60rpx;
  height: 60rpx;
  border-radius: 30rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  font-weight: 600;
  color: #ffffff;
  flex-shrink: 0;
}

.msg-avatar-user {
  background-color: #409EFF;
  margin-left: 16rpx;
  order: 1;
}

.msg-avatar-ai {
  background-color: #67C23A;
  margin-right: 16rpx;
}

.msg-bubble {
  max-width: 580rpx;
  padding: 20rpx 24rpx;
  border-radius: 16rpx;
  font-size: 28rpx;
  line-height: 1.6;
  word-break: break-all;
}

.msg-bubble-user {
  background-color: #409EFF;
  color: #ffffff;
  border-top-right-radius: 4rpx;
}

.msg-bubble-ai {
  background-color: #ffffff;
  color: #333;
  border-top-left-radius: 4rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.06);
}

.msg-text {
  font-size: 28rpx;
  line-height: 1.6;
}

/* 检测结果样式 */
.result-header {
  display: flex;
  align-items: center;
  margin-bottom: 16rpx;
  flex-wrap: wrap;
  gap: 12rpx;
}

.fraud-type {
  font-size: 24rpx;
  color: #909399;
}

.result-score {
  margin-bottom: 12rpx;
}

.score-label {
  font-size: 26rpx;
  color: #606266;
}

.score-value {
  font-size: 36rpx;
  font-weight: 700;
}

.score-suffix {
  font-size: 24rpx;
  color: #909399;
}

.result-confidence {
  margin-bottom: 12rpx;
}

.confidence-label {
  font-size: 26rpx;
  color: #606266;
}

.confidence-value {
  font-size: 26rpx;
  color: #409EFF;
  font-weight: 600;
}

.result-suggestion {
  margin-bottom: 12rpx;
  padding: 16rpx;
  background-color: #f0f9eb;
  border-radius: 12rpx;
}

.suggestion-label {
  font-size: 26rpx;
  color: #67C23A;
  font-weight: 600;
}

.suggestion-text {
  font-size: 26rpx;
  color: #606266;
  line-height: 1.6;
}

.result-detail {
  margin-bottom: 12rpx;
}

.detail-label {
  font-size: 26rpx;
  color: #606266;
  display: block;
  margin-bottom: 8rpx;
}

.keyword-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8rpx;
}

.keyword-tag {
  font-size: 22rpx;
  color: #409EFF;
  background-color: #ecf5ff;
  padding: 4rpx 14rpx;
  border-radius: 20rpx;
}

.result-action {
  margin-top: 12rpx;
  padding-top: 12rpx;
  border-top: 1rpx solid #ebeef5;
}

.action-btn {
  font-size: 26rpx;
  color: #409EFF;
  font-weight: 500;
}

/* 加载中 */
.loading-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 24rpx;
}

.loading-bubble {
  background-color: #ffffff;
  padding: 24rpx 32rpx;
  border-radius: 16rpx;
  border-top-left-radius: 4rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.06);
}

.loading-dot {
  font-size: 40rpx;
  color: #909399;
  animation: loading 1.4s infinite;
  margin-right: 4rpx;
}

.loading-dot:nth-child(2) {
  animation-delay: 0.2s;
}

.loading-dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes loading {
  0%, 60%, 100% {
    opacity: 0.3;
  }
  30% {
    opacity: 1;
  }
}

.input-area {
  flex-shrink: 0;
  padding-bottom: env(safe-area-inset-bottom);
}
</style>