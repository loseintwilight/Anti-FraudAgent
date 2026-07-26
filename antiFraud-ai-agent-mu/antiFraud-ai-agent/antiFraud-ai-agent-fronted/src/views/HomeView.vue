<script setup>
import { RouterLink } from 'vue-router'
import AiAvatar from '../components/AiAvatar.vue'
</script>

<template>
  <div class="home">
    <section class="hero">
      <h1 class="title">选择应用</h1>
      <p class="desc">统一聊天体验，支持流式回复与多端适配。</p>
    </section>

    <div class="cards">
      <RouterLink class="card" to="/fraud">
        <div class="card-top">
          <AiAvatar variant="fraud" size="lg" />
          <div class="card-headings">
            <h2>反诈卫士</h2>
            <p class="card-sub">防骗建议 | SSE 流式</p>
          </div>
        </div>
        <p class="card-body">按会话 ID 记忆上下文，帮你分析各种诈骗套路并给出应对建议。</p>
        <span class="card-cta">
          进入应用
          <span class="card-cta-arrow" aria-hidden="true">&#8594;</span>
        </span>
      </RouterLink>

      <RouterLink class="card" to="/manus">
        <div class="card-top">
          <AiAvatar variant="manus" size="lg" />
          <div class="card-headings">
            <h2>AI 超级智能体</h2>
            <p class="card-sub">多步推理 | 实时推送</p>
          </div>
        </div>
        <p class="card-body">AntiFraudManus 智能体逐步执行并推送步骤结果。</p>
        <span class="card-cta">
          进入应用
          <span class="card-cta-arrow" aria-hidden="true">&#8594;</span>
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
  padding: 2rem 1rem;
}

.hero {
  text-align: left;
  padding: 0 0.25rem;
}

.title {
  margin: 0 0 0.5rem;
  color: #111111;
  font-size: clamp(1.65rem, 4vw, 2.25rem);
  font-weight: 700;
  letter-spacing: -0.03em;
}

.desc {
  margin: 0;
  max-width: 26rem;
  color: #5a6a7e;
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
  padding: 1.5rem;
  border-radius: 16px;
  border: 1px solid rgba(74, 144, 217, 0.14);
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  text-decoration: none;
  color: inherit;
  text-align: left;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 2px 12px rgba(74, 144, 217, 0.05);
}

.card:hover {
  border-color: rgba(74, 144, 217, 0.4);
  background: rgba(255, 255, 255, 0.95);
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(74, 144, 217, 0.15);
}

.card:active {
  transform: translateY(-1px);
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
  color: #111111;
  font-size: 1.15rem;
  font-weight: 600;
}

.card-sub {
  margin: 0;
  font-size: 0.8rem;
  color: #5a6a7e;
  font-weight: 500;
}

.card-body {
  flex: 1;
  margin: 0 0 1rem;
  font-size: 0.9rem;
  line-height: 1.55;
  color: #5a6a7e;
}

.card-cta {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-weight: 600;
  font-size: 0.88rem;
  color: #4A90D9;
}

.card-cta-arrow {
  transition: transform 0.2s ease;
}

.card:hover .card-cta-arrow {
  transform: translateX(3px);
}
</style>