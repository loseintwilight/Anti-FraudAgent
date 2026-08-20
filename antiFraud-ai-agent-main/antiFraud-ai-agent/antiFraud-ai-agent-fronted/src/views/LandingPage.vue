<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import LightParticleBackground from '../components/LightParticleBackground.vue'

const router = useRouter()

// 打字效果
const typedText = ref('')
const fullText = '实时检测 | 智能识别 | 即时预警'
let charIndex = 0
let typingTimer = null

function startTyping() {
  typingTimer = setInterval(() => {
    if (charIndex < fullText.length) {
      typedText.value += fullText[charIndex]
      charIndex++
    } else {
      clearInterval(typingTimer)
    }
  }, 80)
}

// 数字动画增长
const stats = ref([
  { label: '已检测', value: 0, target: 12860, suffix: '次' },
  { label: '拦截诈骗', value: 0, target: 3842, suffix: '起' },
  { label: '保护用户', value: 0, target: 9571, suffix: '人' },
  { label: '预警准确率', value: 0, target: 99, suffix: '%' },
])
let statsTimer = null

function animateStats() {
  const duration = 2000
  const startTime = Date.now()
  const initialValues = stats.value.map(() => 0)

  statsTimer = setInterval(() => {
    const elapsed = Date.now() - startTime
    const progress = Math.min(elapsed / duration, 1)
    const eased = 1 - Math.pow(1 - progress, 3)

    stats.value.forEach((stat, i) => {
      stat.value = Math.floor(initialValues[i] + (stat.target - initialValues[i]) * eased)
    })

    if (progress >= 1) {
      clearInterval(statsTimer)
    }
  }, 30)
}

onMounted(() => {
  startTyping()
  animateStats()
})

onUnmounted(() => {
  if (typingTimer) clearInterval(typingTimer)
  if (statsTimer) clearInterval(statsTimer)
})
</script>

<template>
  <div class="landing">
    <LightParticleBackground />

    <!-- 左上角 Logo + 右上角导航 -->
    <header class="navbar">
      <router-link to="/" class="logo-link">
        <img src="/src/assets/logo.png" alt="反诈卫士" class="logo-img" />
        <span class="logo-text">反诈卫士</span>
      </router-link>
      <nav class="nav-links">
        <button class="nav-btn" @click="router.push('/login')">登录</button>
        <button class="nav-btn nav-btn-primary" @click="router.push('/register')">注册</button>
      </nav>
    </header>

    <!-- 主内容区：左对齐布局 -->
    <main class="hero">
      <div class="hero-content">
        <span class="hero-badge">AI 智能反诈系统</span>
        <h1 class="hero-title">
          守护你的<br />
          <span class="hero-title-accent">数字安全</span>
        </h1>
        <p class="hero-subtitle">
          基于深度学习的智能反诈检测平台，实时识别诈骗信息，
          智能分析风险行为，全方位守护你的财产安全。
        </p>
        <div class="hero-typing">
          <span class="typing-text">{{ typedText }}</span>
          <span class="typing-cursor">|</span>
        </div>
        <div class="hero-actions">
          <button class="cta-btn" @click="router.push('/register')">立即体验</button>
          <button class="cta-btn cta-btn-outline" @click="router.push('/login')">登录使用</button>
        </div>
      </div>

      <!-- 右侧数据展示 -->
      <div class="hero-stats">
        <div v-for="(stat, index) in stats" :key="index" class="stat-card">
          <span class="stat-value">{{ stat.value.toLocaleString() }}{{ stat.suffix }}</span>
          <span class="stat-label">{{ stat.label }}</span>
        </div>
      </div>
    </main>

    <!-- 功能特点 -->
    <section class="features">
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#165DFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
          </div>
          <h3 class="feature-title">实时检测</h3>
          <p class="feature-desc">7x24 小时不间断监测，毫秒级识别诈骗信息，守护每一刻安全。</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#165DFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
            </svg>
          </div>
          <h3 class="feature-title">智能识别</h3>
          <p class="feature-desc">深度学习模型精准分析诈骗套路，持续进化识别新型诈骗手法。</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#165DFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
              <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
            </svg>
          </div>
          <h3 class="feature-title">即时预警</h3>
          <p class="feature-desc">多通道预警通知，第一时间推送风险信息，防止财产损失。</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#165DFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
          </div>
          <h3 class="feature-title">多端防护</h3>
          <p class="feature-desc">覆盖 Web、移动端等多场景，全方位构建反诈安全屏障。</p>
        </div>
      </div>
    </section>

    <!-- 底部 -->
    <footer class="footer">
      <p class="footer-text">反诈卫士 &copy; 2026 | AI 智能反诈检测系统</p>
    </footer>
  </div>
</template>

<style scoped>
.landing {
  position: relative;
  width: 100%;
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  color: #333;
  font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* ===== 导航栏 ===== */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  height: 64px;
  z-index: 100;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(74, 144, 217, 0.08);
}

.logo-link {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
}

.logo-img {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  object-fit: cover;
}

.logo-text {
  font-size: 1.1rem;
  font-weight: 700;
  color: #2c3e50;
  letter-spacing: -0.02em;
}

.nav-links {
  display: flex;
  gap: 10px;
}

.nav-btn {
  padding: 8px 24px;
  border: 1px solid #dce3ef;
  border-radius: 10px;
  background: #fff;
  color: #5a6a7e;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  font-family: inherit;
  letter-spacing: 0.02em;
}

.nav-btn:hover {
  background: #f0f4ff;
  border-color: rgba(74, 144, 217, 0.5);
  box-shadow: 0 2px 8px rgba(74, 144, 217, 0.15);
  transform: translateY(-1px);
}

.nav-btn-primary {
  background: linear-gradient(135deg, #4A90D9, #357ABD);
  border-color: transparent;
  color: #fff;
}

.nav-btn-primary:hover {
  background: linear-gradient(135deg, #5B9EE0, #3D86C9);
  border-color: transparent;
  box-shadow: 0 4px 16px rgba(74, 144, 217, 0.35);
}

/* ===== 主内容区（左对齐非居中） ===== */
.hero {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 80px 48px 48px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  gap: 48px;
  z-index: 1;
}

.hero-content {
  flex: 1;
  max-width: 640px;
  animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) both;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.hero-badge {
  display: inline-block;
  padding: 4px 14px;
  border-radius: 20px;
  border: 1px solid rgba(22, 93, 255, 0.3);
  background: rgba(22, 93, 255, 0.1);
  color: #165DFF;
  font-size: 0.8rem;
  font-weight: 500;
  letter-spacing: 0.06em;
  margin-bottom: 20px;
}

.hero-title {
  font-size: clamp(2.5rem, 6vw, 4.2rem);
  font-weight: 800;
  margin: 0 0 16px;
  line-height: 1.15;
  letter-spacing: -0.03em;
  color: #2c3e50;
  text-align: left;
}

.hero-title-accent {
  background: linear-gradient(135deg, #4A90D9 0%, #7B68EE 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: clamp(1rem, 1.8vw, 1.15rem);
  color: #7a8ba8;
  margin: 0 0 12px;
  line-height: 1.6;
  max-width: 540px;
  text-align: left;
}

.hero-typing {
  font-size: clamp(0.9rem, 1.5vw, 1rem);
  color: #8a9bb5;
  margin: 0 0 32px;
  min-height: 1.5em;
  font-weight: 300;
  letter-spacing: 0.05em;
}

.typing-cursor {
  display: inline-block;
  color: #165DFF;
  animation: blink 0.8s step-end infinite;
  margin-left: 2px;
  font-weight: 300;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.hero-actions {
  display: flex;
  gap: 12px;
}

.cta-btn {
  padding: 12px 32px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #165DFF 0%, #0e42d2 100%);
  color: #fff;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  font-family: inherit;
  letter-spacing: 0.03em;
}

.cta-btn:hover {
  background: linear-gradient(135deg, #1a6aff 0%, #1248e0 100%);
  box-shadow: 0 8px 32px rgba(22, 93, 255, 0.4);
  transform: translateY(-2px);
}

.cta-btn:active {
  transform: translateY(0);
}

.cta-btn-outline {
  background: transparent;
  border: 1px solid #dce3ef;
  color: #5a6a7e;
}

.cta-btn-outline:hover {
  background: #f0f4ff;
  border-color: rgba(74, 144, 217, 0.5);
  box-shadow: none;
  transform: translateY(-2px);
}

/* ===== 右侧数据 ===== */
.hero-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  flex-shrink: 0;
  animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.2s both;
}

.stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 28px 24px;
  border-radius: 16px;
  border: 1px solid rgba(74, 144, 217, 0.1);
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  min-width: 150px;
}

.stat-card:hover {
  border-color: rgba(74, 144, 217, 0.3);
  background: rgba(255, 255, 255, 0.9);
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(74, 144, 217, 0.12);
}

.stat-value {
  font-size: clamp(1.6rem, 3vw, 2.2rem);
  font-weight: 700;
  color: #2c3e50;
  letter-spacing: -0.02em;
  background: linear-gradient(180deg, #2c3e50 0%, rgba(74, 144, 217, 0.8) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: clamp(0.75rem, 1vw, 0.85rem);
  color: #7a8ba8;
  font-weight: 400;
  letter-spacing: 0.05em;
}

/* ===== 功能特点 ===== */
.features {
  padding: 80px 48px 60px;
  z-index: 1;
  position: relative;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.feature-card {
  padding: 32px 24px;
  border-radius: 16px;
  border: 1px solid rgba(74, 144, 217, 0.08);
  background: rgba(255, 255, 255, 0.6);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.feature-card:hover {
  border-color: rgba(74, 144, 217, 0.25);
  background: rgba(255, 255, 255, 0.85);
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(74, 144, 217, 0.08);
}

.feature-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  border: 1px solid rgba(74, 144, 217, 0.2);
  background: rgba(74, 144, 217, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.feature-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 8px;
  letter-spacing: -0.01em;
}

.feature-desc {
  font-size: 0.9rem;
  color: #7a8ba8;
  line-height: 1.6;
  margin: 0;
}

/* ===== 底部 ===== */
.footer {
  padding: 24px 48px;
  border-top: 1px solid rgba(74, 144, 217, 0.08);
  z-index: 1;
  text-align: center;
}

.footer-text {
  font-size: 0.8rem;
  color: #8a9bb5;
  letter-spacing: 0.03em;
}

/* ===== 响应式 ===== */
@media (max-width: 1024px) {
  .hero {
    flex-direction: column;
    padding: 80px 24px 40px;
    text-align: left;
  }

  .hero-content {
    max-width: 100%;
  }

  .hero-stats {
    width: 100%;
    grid-template-columns: repeat(4, 1fr);
  }

  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .navbar {
    padding: 0 16px;
  }

  .hero {
    padding: 72px 16px 32px;
  }

  .hero-stats {
    grid-template-columns: 1fr 1fr;
  }

  .features {
    padding: 48px 16px 32px;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .hero-actions {
    flex-direction: column;
  }

  .cta-btn {
    width: 100%;
    text-align: center;
  }
}
</style>