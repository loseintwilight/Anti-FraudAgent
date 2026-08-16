<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  /** fraud | manus */
  variant: {
    type: String,
    default: 'fraud',
    validator: (v) => v === 'fraud' || v === 'manus',
  },
  size: {
    type: String,
    default: 'md',
    validator: (v) => ['sm', 'md', 'lg'].includes(v),
  },
})

const imgLoaded = ref(false)
const imgError = ref(false)

onMounted(() => {
  const img = new Image()
  img.onload = () => { imgLoaded.value = true }
  img.onerror = () => { imgError.value = true }
  img.src = '/src/assets/load.jpg'
})
</script>

<template>
  <div
    class="ai-avatar"
    :class="[`ai-avatar--${variant}`, `ai-avatar--${size}`]"
    role="img"
    :aria-label="variant === 'fraud' ? '反诈卫士 AI' : '超级智能体 AI'"
  >
    <!-- 反诈卫士：使用真实头像图片 -->
    <template v-if="variant === 'fraud'">
      <img
        v-if="!imgError"
        src="/src/assets/load.jpg"
        alt="反诈卫士"
        class="avatar-img"
        :class="{ 'avatar-img--loaded': imgLoaded }"
      />
      <!-- 加载失败时显示默认SVG -->
      <svg v-else class="glyph" viewBox="0 0 40 40" fill="none" aria-hidden="true">
        <path
          d="M20 5.7c-4.2 3.1-8.5 3.6-11.2 3.7v10.6c0 7.2 5.3 11.6 11.2 14.3 5.9-2.7 11.2-7.1 11.2-14.3V9.4c-2.7-.1-7-.6-11.2-3.7Z"
          stroke="currentColor"
          stroke-width="2.2"
        />
        <path
          d="M14.2 20.2l3 3 8.6-9"
          stroke="currentColor"
          stroke-width="2.2"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
    </template>
    <!-- 超级智能体：保持原样 -->
    <svg v-else class="glyph" viewBox="0 0 40 40" fill="none" aria-hidden="true">
      <rect x="9" y="12" width="22" height="18" rx="4" stroke="currentColor" stroke-width="2.2" fill="none" />
      <circle cx="16" cy="21" r="2.2" fill="currentColor" />
      <circle cx="24" cy="21" r="2.2" fill="currentColor" />
      <path d="M14 27h12" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
      <path d="M20 8v4" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
    </svg>
  </div>
</template>

<style scoped>
.ai-avatar {
  flex-shrink: 0;
  border-radius: 50%;
  display: grid;
  place-items: center;
  overflow: hidden;
}

.ai-avatar--sm {
  width: 2.25rem;
  height: 2.25rem;
}
.ai-avatar--md {
  width: 2.625rem;
  height: 2.625rem;
}
.ai-avatar--lg {
  width: 3rem;
  height: 3rem;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.avatar-img--loaded {
  opacity: 1;
}

.glyph {
  width: 55%;
  height: 55%;
}

.ai-avatar--fraud {
  background: transparent;
  color: #c2410c;
}

.ai-avatar--manus {
  --avatar-ring: rgba(59, 130, 246, 0.35);
  background: linear-gradient(145deg, #dbeafe 0%, #e0e7ff 50%, #cffafe 100%);
  color: #1d4ed8;
}

@media (prefers-color-scheme: dark) {
  .ai-avatar--manus {
    --avatar-ring: rgba(96, 165, 250, 0.45);
    background: linear-gradient(145deg, #172554 0%, #312e81 50%, #164e63 100%);
    color: #93c5fd;
  }
}
</style>