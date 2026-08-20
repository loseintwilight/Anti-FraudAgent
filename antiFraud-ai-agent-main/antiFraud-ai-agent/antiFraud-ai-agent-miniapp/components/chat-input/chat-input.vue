<template>
  <view class="chat-input">
    <view class="input-wrapper">
      <textarea
        v-model="content"
        class="input-area"
        :placeholder="placeholder"
        placeholder-style="color: #c0c4cc; font-size: 28rpx;"
        :maxlength="maxlength"
        auto-height
        :adjust-position="false"
        @confirm="handleSubmit"
      />
    </view>
    <view class="send-btn" :class="{ 'send-btn-active': content.trim() }" @tap="handleSubmit">
      <text class="send-text">发送</text>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  placeholder: {
    type: String,
    default: '请输入您要检测的内容...'
  },
  maxlength: {
    type: Number,
    default: 2000
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit'])

const content = ref('')

function handleSubmit() {
  const text = content.value.trim()
  if (!text) return
  if (props.loading) return
  emit('submit', text)
  content.value = ''
}
</script>

<style scoped>
.chat-input {
  display: flex;
  align-items: flex-end;
  padding: 16rpx 24rpx;
  background-color: #ffffff;
  border-top: 1rpx solid #ebeef5;
  box-shadow: 0 -2rpx 10rpx rgba(0, 0, 0, 0.05);
  position: relative;
  z-index: 10;
}

.input-wrapper {
  flex: 1;
  background-color: #f5f7fa;
  border-radius: 16rpx;
  padding: 16rpx 20rpx;
  margin-right: 16rpx;
  min-height: 80rpx;
  max-height: 200rpx;
}

.input-area {
  width: 100%;
  font-size: 28rpx;
  color: #333;
  background: transparent;
  line-height: 1.6;
  max-height: 160rpx;
}

.send-btn {
  flex-shrink: 0;
  width: 120rpx;
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #e8f0fe;
  border-radius: 40rpx;
  transition: all 0.3s ease;
}

.send-btn-active {
  background-color: #409EFF;
}

.send-text {
  font-size: 28rpx;
  color: #409EFF;
  font-weight: 500;
}

.send-btn-active .send-text {
  color: #ffffff;
}
</style>