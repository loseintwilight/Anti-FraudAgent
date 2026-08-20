<template>
  <view class="page-container">
    <!-- 加载状态 -->
    <view class="loading-container" v-if="loading && list.length === 0">
      <text class="loading-text">加载中...</text>
    </view>

    <!-- 空状态 -->
    <view class="empty-container" v-else-if="list.length === 0">
      <text class="empty-icon">&#x1F4CB;</text>
      <text class="empty-text">暂无检测记录</text>
      <text class="empty-desc">去首页检测可疑信息吧</text>
      <button class="go-btn" @tap="goToIndex">去检测</button>
    </view>

    <!-- 历史记录列表 -->
    <scroll-view
      v-else
      class="list-scroll"
      scroll-y
      @scrolltolower="loadMore"
      :refresher-enabled="true"
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh"
    >
      <view
        class="history-item"
        v-for="(item, index) in list"
        :key="item.id || index"
        @tap="goToReport(item.id || item.reportId)"
      >
        <view class="item-header">
          <risk-badge :level="item.riskLevel" />
          <text class="item-time">{{ item.detectTime || item.createTime || '--' }}</text>
        </view>
        <view class="item-content">
          <text class="content-text">{{ item.content || item.summary || '无内容' }}</text>
        </view>
        <view class="item-footer">
          <text class="item-score">风险评分：{{ item.score || 0 }}</text>
          <text class="item-arrow">&gt;</text>
        </view>
      </view>

      <!-- 加载更多 -->
      <view class="load-more" v-if="hasMore">
        <text class="load-more-text">加载更多...</text>
      </view>
      <view class="load-more" v-else-if="list.length > 0">
        <text class="load-more-text no-more">没有更多了</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { getHistory } from '@/api/index.js'
import RiskBadge from '@/components/risk-badge/risk-badge.vue'

const list = ref([])
const loading = ref(true)
const refreshing = ref(false)
const page = ref(1)
const hasMore = ref(true)
const pageSize = 10

onLoad(() => {
  fetchHistory(true)
})

async function fetchHistory(reset = false) {
  if (reset) {
    page.value = 1
    hasMore.value = true
  }
  if (!hasMore.value && !reset) return

  try {
    const res = await getHistory(page.value, pageSize)
    const records = res.data?.records || res.data || []
    if (reset) {
      list.value = records
    } else {
      list.value = [...list.value, ...records]
    }
    hasMore.value = records.length >= pageSize
    page.value++
  } catch (err) {
    console.error('获取历史记录失败:', err)
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

async function loadMore() {
  if (hasMore.value && !loading.value) {
    await fetchHistory(false)
  }
}

async function onRefresh() {
  refreshing.value = true
  await fetchHistory(true)
}

function goToReport(reportId) {
  if (!reportId) return
  uni.navigateTo({
    url: `/pages/report/index?reportId=${reportId}`
  })
}

function goToIndex() {
  uni.switchTab({
    url: '/pages/index/index'
  })
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background-color: #f5f7fa;
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
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 60vh;
}

.empty-icon {
  font-size: 80rpx;
  margin-bottom: 20rpx;
}

.empty-text {
  font-size: 32rpx;
  color: #333;
  margin-bottom: 12rpx;
}

.empty-desc {
  font-size: 26rpx;
  color: #909399;
  margin-bottom: 40rpx;
}

.go-btn {
  width: 200rpx;
  height: 72rpx;
  line-height: 72rpx;
  text-align: center;
  background-color: #409EFF;
  color: #ffffff;
  border-radius: 36rpx;
  font-size: 28rpx;
  border: none;
  padding: 0;
}

.list-scroll {
  height: 100vh;
  padding: 24rpx 32rpx;
}

.history-item {
  background-color: #ffffff;
  border-radius: 20rpx;
  padding: 28rpx 24rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.06);
}

.item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16rpx;
}

.item-time {
  font-size: 24rpx;
  color: #909399;
}

.item-content {
  margin-bottom: 16rpx;
}

.content-text {
  font-size: 28rpx;
  color: #333;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 16rpx;
  border-top: 1rpx solid #f0f0f0;
}

.item-score {
  font-size: 24rpx;
  color: #909399;
}

.item-arrow {
  font-size: 28rpx;
  color: #c0c4cc;
}

.load-more {
  text-align: center;
  padding: 24rpx 0 48rpx;
}

.load-more-text {
  font-size: 24rpx;
  color: #909399;
}

.no-more {
  color: #c0c4cc;
}
</style>