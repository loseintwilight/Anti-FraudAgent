<script setup>
defineProps({
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
</script>

<template>
  <div
    class="ai-avatar"
    :class="[`ai-avatar--${variant}`, `ai-avatar--${size}`]"
    role="img"
    :aria-label="variant === 'fraud' ? '反诈骗大师 AI' : '超级智能体 AI'"
  >
    <svg v-if="variant === 'fraud'" class="glyph" viewBox="0 0 40 40" fill="none" aria-hidden="true">
      <!-- 简单盾牌 + 勾选图标 -->
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
  box-shadow: var(--shadow-avatar, 0 2px 10px rgba(0, 0, 0, 0.12));
  border: 2px solid var(--avatar-ring);
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

.glyph {
  width: 55%;
  height: 55%;
}

.ai-avatar--fraud {
  --avatar-ring: rgba(249, 115, 22, 0.35);
  background: linear-gradient(145deg, #ffedd5 0%, #fed7aa 40%, #fef3c7 100%);
  color: #c2410c;
}

@media (prefers-color-scheme: dark) {
  .ai-avatar--fraud {
    --avatar-ring: rgba(249, 115, 22, 0.4);
    background: linear-gradient(145deg, #3b1a0f 0%, #7c2d12 55%, #4c1d95 100%);
    color: #fb923c;
  }
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
