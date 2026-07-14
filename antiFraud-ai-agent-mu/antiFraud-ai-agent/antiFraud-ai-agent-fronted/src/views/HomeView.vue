<script setup>
import { RouterLink } from 'vue-router'
import AiAvatar from '../components/AiAvatar.vue'
</script>

<template>
  <div class="home">
    <section class="hero">
      <p class="eyebrow">YU AI Agent</p>
      <h1 class="title">选择应用</h1>
      <p class="desc">统一聊天体验，支持流式回复与多端适配。</p>
    </section>

    <div class="cards">
      <RouterLink class="card" to="/fraud">
        <div class="card-top">
          <AiAvatar variant="fraud" size="lg" />
          <div class="card-headings">
            <h2>AI 反诈骗大师</h2>
            <p class="card-sub">防骗建议 · SSE 流式</p>
          </div>
        </div>
        <p class="card-body">按会话 ID 记忆上下文，帮你分析各种诈骗套路并给出应对建议。</p>
        <span class="card-cta">
          进入应用
          <span class="card-cta-arrow" aria-hidden="true">→</span>
        </span>
      </RouterLink>

      <RouterLink class="card" to="/manus">
        <div class="card-top">
          <AiAvatar variant="manus" size="lg" />
          <div class="card-headings">
            <h2>AI 超级智能体</h2>
            <p class="card-sub">多步推理 · 实时推送</p>
          </div>
        </div>
        <p class="card-body">AntiFraudManus 智能体逐步执行并推送步骤结果。</p>
        <span class="card-cta">
          进入应用
          <span class="card-cta-arrow" aria-hidden="true">→</span>
        </span>
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
.home {
  width: 100%;
  max-width: 48rem;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: clamp(1.5rem, 4vw, 2.25rem);
}

.hero {
  text-align: center;
  padding: 0 0.25rem;
}

.eyebrow {
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--accent);
  margin: 0 0 0.5rem;
}

.title {
  margin: 0 0 0.5rem;
}

.desc {
  margin: 0 auto;
  max-width: 26rem;
  color: var(--text-muted);
  font-size: 0.95rem;
  line-height: 1.55;
}

.cards {
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr;
}

@media (min-width: 700px) {
  .cards {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.15rem;
  }
}

.card {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  padding: 1.25rem 1.2rem;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
  background: var(--surface);
  text-decoration: none;
  color: inherit;
  text-align: left;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.2s ease;
  box-shadow: 0 1px 0 rgba(15, 13, 20, 0.04);
}

@media (prefers-color-scheme: dark) {
  .card {
    box-shadow: none;
    background: color-mix(in srgb, var(--surface) 100%, #000 4%);
  }
}

.card:hover {
  border-color: var(--accent-border);
  box-shadow: var(--shadow);
  transform: translateY(-2px);
}

.card:active {
  transform: translateY(0);
}

.card-top {
  display: flex;
  align-items: flex-start;
  gap: 0.85rem;
  margin-bottom: 0.65rem;
}

.card-headings {
  min-width: 0;
  flex: 1;
  padding-top: 0.15rem;
}

.card-headings h2 {
  margin: 0 0 0.2rem;
}

.card-sub {
  margin: 0;
  font-size: 0.8rem;
  color: var(--text-muted);
  font-weight: 500;
}

.card-body {
  flex: 1;
  margin: 0 0 1rem;
  font-size: 0.9rem;
  line-height: 1.55;
  color: var(--text);
}

.card-cta {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-weight: 600;
  font-size: 0.88rem;
  color: var(--accent);
}

.card-cta-arrow {
  transition: transform 0.2s ease;
}

.card:hover .card-cta-arrow {
  transform: translateX(3px);
}
</style>
