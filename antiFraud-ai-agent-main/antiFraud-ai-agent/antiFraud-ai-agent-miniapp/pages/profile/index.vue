<template>
  <view class="page-container">
    <!-- 用户信息卡片 -->
    <view class="user-card">
      <view class="avatar">
        <text class="avatar-text">{{ userName }}</text>
      </view>
      <view class="user-info">
        <text class="nickname">{{ userInfo?.nickname || userInfo?.nickName || '未登录用户' }}</text>
        <text class="phone" v-if="userInfo?.phone">已绑定手机号</text>
      </view>
      <view class="edit-btn" @tap="handleEditProfile">
        <text class="edit-text">编辑</text>
      </view>
    </view>

    <!-- 统计卡片 -->
    <view class="stats-card">
      <view class="stat-item">
        <text class="stat-number">{{ stats.detectionCount || 0 }}</text>
        <text class="stat-label">检测次数</text>
      </view>
      <view class="stat-divider"></view>
      <view class="stat-item">
        <text class="stat-number">{{ stats.highRiskCount || 0 }}</text>
        <text class="stat-label">高风险</text>
      </view>
      <view class="stat-divider"></view>
      <view class="stat-item">
        <text class="stat-number">{{ stats.safeCount || 0 }}</text>
        <text class="stat-label">安全信息</text>
      </view>
    </view>

    <!-- 功能列表 -->
    <view class="menu-list">
      <view class="menu-item" @tap="handleMenuClick('profile')">
        <text class="menu-icon">&#x1F464;</text>
        <text class="menu-label">个人信息</text>
        <text class="menu-arrow">&gt;</text>
      </view>
      <view class="menu-item" @tap="handleMenuClick('about')">
        <text class="menu-icon">&#x2139;</text>
        <text class="menu-label">关于我们</text>
        <text class="menu-arrow">&gt;</text>
      </view>
      <view class="menu-item" @tap="handleMenuClick('feedback')">
        <text class="menu-icon">&#x1F4AC;</text>
        <text class="menu-label">意见反馈</text>
        <text class="menu-arrow">&gt;</text>
      </view>
    </view>

    <!-- 退出登录 -->
    <view class="logout-section">
      <button class="logout-btn" @tap="handleLogout">退出登录</button>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { useStore } from 'vuex'
import { getUserProfile } from '@/api/index.js'

const store = useStore()
const userInfo = ref(null)
const stats = ref({
  detectionCount: 0,
  highRiskCount: 0,
  safeCount: 0
})

const userName = ref('U')

onShow(async () => {
  await loadUserInfo()
})

async function loadUserInfo() {
  const cached = uni.getStorageSync('userInfo')
  if (cached) {
    userInfo.value = typeof cached === 'string' ? JSON.parse(cached) : cached
    userName.value = getFirstChar(userInfo.value)
  }
  try {
    const res = await getUserProfile()
    const data = res.data || res
    userInfo.value = data
    store.commit('SET_USER', data)
    uni.setStorageSync('userInfo', data)
    userName.value = getFirstChar(data)
    if (data.stats) {
      stats.value = data.stats
    }
  } catch (err) {
    console.error('获取用户信息失败:', err)
  }
}

function getFirstChar(user) {
  if (!user) return 'U'
  const name = user.nickname || user.nickName || '用户'
  return name.charAt(0).toUpperCase()
}

function handleEditProfile() {
  uni.showToast({ title: '功能开发中', icon: 'none' })
}

function handleMenuClick(type) {
  const titles = {
    profile: '个人信息',
    about: '关于我们',
    feedback: '意见反馈'
  }
  uni.showToast({
    title: `${titles[type] || '功能'}开发中`,
    icon: 'none'
  })
}

function handleLogout() {
  uni.showModal({
    title: '确认退出',
    content: '确定要退出登录吗？',
    success: (res) => {
      if (res.confirm) {
        store.commit('CLEAR_USER')
        uni.showToast({ title: '已退出登录', icon: 'success' })
      }
    }
  })
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding-bottom: 100rpx;
}

/* 用户信息卡片 */
.user-card {
  display: flex;
  align-items: center;
  padding: 48rpx 32rpx;
  background-color: #409EFF;
  margin-bottom: 24rpx;
}

.avatar {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50rpx;
  background-color: rgba(255, 255, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 24rpx;
}

.avatar-text {
  font-size: 40rpx;
  font-weight: 700;
  color: #ffffff;
}

.user-info {
  flex: 1;
}

.nickname {
  font-size: 34rpx;
  font-weight: 600;
  color: #ffffff;
  display: block;
  margin-bottom: 8rpx;
}

.phone {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.7);
}

.edit-btn {
  padding: 8rpx 24rpx;
  border: 2rpx solid rgba(255, 255, 255, 0.6);
  border-radius: 24rpx;
}

.edit-text {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.9);
}

/* 统计卡片 */
.stats-card {
  display: flex;
  align-items: center;
  padding: 32rpx 24rpx;
  background-color: #ffffff;
  margin: 0 32rpx 24rpx;
  border-radius: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.06);
}

.stat-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-number {
  font-size: 40rpx;
  font-weight: 700;
  color: #333;
  margin-bottom: 8rpx;
}

.stat-label {
  font-size: 24rpx;
  color: #909399;
}

.stat-divider {
  width: 1rpx;
  height: 60rpx;
  background-color: #ebeef5;
}

/* 功能列表 */
.menu-list {
  background-color: #ffffff;
  margin: 0 32rpx;
  border-radius: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 28rpx 24rpx;
  border-bottom: 1rpx solid #f5f7fa;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-icon {
  font-size: 32rpx;
  margin-right: 20rpx;
  width: 40rpx;
  text-align: center;
}

.menu-label {
  flex: 1;
  font-size: 28rpx;
  color: #333;
}

.menu-arrow {
  font-size: 28rpx;
  color: #c0c4cc;
}

/* 退出登录 */
.logout-section {
  margin: 60rpx 32rpx;
}

.logout-btn {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  text-align: center;
  background-color: #ffffff;
  color: #F56C6C;
  border-radius: 44rpx;
  font-size: 30rpx;
  font-weight: 500;
  border: 2rpx solid #f0f0f0;
  padding: 0;
}

.logout-btn::after {
  border: none;
}
</style>