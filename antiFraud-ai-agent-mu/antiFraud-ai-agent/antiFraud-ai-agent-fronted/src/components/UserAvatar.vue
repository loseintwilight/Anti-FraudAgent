<script setup>
defineProps({
  size: {
    type: String,
    default: 'md',
    validator: (v) => ['sm', 'md', 'lg'].includes(v),
  },
})
</script>

<template>
  <div
    class="user-avatar"
    :class="`user-avatar--${size}`"
    role="img"
    aria-label="我"
  >
    <svg class="glyph" viewBox="0 0 40 40" fill="none" aria-hidden="true">
      <circle cx="20" cy="14" r="6" stroke="currentColor" stroke-width="2.2" />
      <path
        d="M10 34c0-5.5 4.5-10 10-10s10 4.5 10 10"
        stroke="currentColor"
        stroke-width="2.2"
        stroke-linecap="round"
      />
    </svg>
  </div>
</template>

<style scoped>
.user-avatar {
  --user-avatar-bg: linear-gradient(160deg, #f3f4f6 0%, #e5e7eb 100%);
  --user-avatar-fg: #4b5563;
  --user-avatar-ring: rgba(107, 114, 128, 0.25);
  flex-shrink: 0;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: var(--user-avatar-bg);
  color: var(--user-avatar-fg);
  border: 2px solid var(--user-avatar-ring);
  box-shadow: var(--shadow-avatar, 0 2px 10px rgba(0, 0, 0, 0.08));
}

.user-avatar--sm {
  width: 2.25rem;
  height: 2.25rem;
}
.user-avatar--md {
  width: 2.625rem;
  height: 2.625rem;
}
.user-avatar--lg {
  width: 3rem;
  height: 3rem;
}

.glyph {
  width: 55%;
  height: 55%;
}

@media (prefers-color-scheme: dark) {
  .user-avatar {
    --user-avatar-bg: linear-gradient(160deg, #374151 0%, #1f2937 100%);
    --user-avatar-fg: #d1d5db;
    --user-avatar-ring: rgba(156, 163, 175, 0.35);
  }
}
</style>

