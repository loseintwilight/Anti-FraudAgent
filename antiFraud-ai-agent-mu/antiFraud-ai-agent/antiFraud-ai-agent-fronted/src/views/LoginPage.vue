<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import LightParticleBackground from '../components/LightParticleBackground.vue'

const router = useRouter()

const form = ref({
  username: '',
  password: '',
  code: '',
  remember: false,
})

const errors = ref({
  username: '',
  password: '',
  code: '',
})

const errorMsg = ref('')
const loading = ref(false)
const captchaImg = ref('')
const captchaUuid = ref('')

const API_BASE = import.meta.env.VITE_API_BASE?.replace(/\/$/, '') || 'http://localhost:8123/api'

async function loadCaptcha() {
  try {
    const res = await fetch(`${API_BASE}/v1/auth/captchaImage`).then(r => r.json())
    if (res.success) {
      captchaImg.value = res.img
      captchaUuid.value = res.uuid
    }
  } catch (e) {
    console.error('加载验证码失败:', e)
  }
}

function validateForm() {
  let valid = true
  errors.value = { username: '', password: '', code: '' }

  if (!form.value.username.trim()) {
    errors.value.username = '请输入用户名'
    valid = false
  }

  if (!form.value.password) {
    errors.value.password = '请输入密码'
    valid = false
  }

  if (!form.value.code) {
    errors.value.code = '请输入验证码'
    valid = false
  }

  return valid
}

function handleLogin() {
  if (!validateForm()) return

  loading.value = true
  errorMsg.value = ''

  fetch(`${API_BASE}/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: form.value.username.trim(),
      password: form.value.password,
      code: form.value.code,
      uuid: captchaUuid.value,
    }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.success) {
        localStorage.setItem('auth_token', data.token)
        localStorage.setItem('auth_user', data.user.username)
        router.push('/fraud')
      } else {
        errorMsg.value = data.message || '登录失败'
        loadCaptcha()
      }
    })
    .catch(() => {
      errorMsg.value = '网络错误，请检查后端服务是否启动'
    })
    .finally(() => {
      loading.value = false
    })
}

onMounted(() => {
  loadCaptcha()
})
</script>

<template>
  <div class="login-page">
    <LightParticleBackground />

    <!-- 左上角 Logo -->
    <router-link to="/" class="logo-link">
      <img src="/src/assets/logo.png" alt="反诈卫士" class="logo-img" />
      <span class="logo-text">反诈卫士</span>
    </router-link>

    <div class="login-container">
      <!-- 左栏：品牌展示 -->
      <div class="brand-section">
        <div class="brand-content">
          <h1 class="brand-title">欢迎回来</h1>
          <p class="brand-desc">AI 智能反诈检测系统，守护您的数字安全</p>
          <ul class="feature-list">
            <li class="feature-item">
              <svg class="feature-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#165DFF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <span>实时检测诈骗信息</span>
            </li>
            <li class="feature-item">
              <svg class="feature-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#165DFF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <span>智能识别风险行为</span>
            </li>
            <li class="feature-item">
              <svg class="feature-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#165DFF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <span>即时预警守护安全</span>
            </li>
            <li class="feature-item">
              <svg class="feature-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#165DFF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <span>多场景全方位防护</span>
            </li>
          </ul>
        </div>
      </div>

      <!-- 右栏：登录表单（毛玻璃卡片） -->
      <div class="form-section">
        <div class="form-card">
          <h2 class="form-title">登录账号</h2>
          <p class="form-subtitle">请使用您的账号登录系统</p>

          <form class="login-form" @submit.prevent="handleLogin">
            <div class="form-group">
              <label class="form-label" for="username">用户名</label>
              <input
                id="username"
                v-model="form.username"
                type="text"
                class="form-input"
                :class="{ 'input-error': errors.username }"
                placeholder="请输入用户名"
                autocomplete="username"
              />
              <span v-if="errors.username" class="error-msg">{{ errors.username }}</span>
            </div>

            <div class="form-group">
              <label class="form-label" for="password">密码</label>
              <input
                id="password"
                v-model="form.password"
                type="password"
                class="form-input"
                :class="{ 'input-error': errors.password }"
                placeholder="请输入密码"
                autocomplete="current-password"
              />
              <span v-if="errors.password" class="error-msg">{{ errors.password }}</span>
            </div>

            <!-- 验证码 -->
            <div class="form-group">
              <label class="form-label" for="code">验证码</label>
              <div class="captcha-row">
                <input
                  id="code"
                  v-model="form.code"
                  type="text"
                  class="form-input captcha-input"
                  :class="{ 'input-error': errors.code }"
                  placeholder="验证码"
                  maxlength="4"
                  autocomplete="off"
                />
                <img
                  v-if="captchaImg"
                  :src="captchaImg"
                  class="captcha-img"
                  @click="loadCaptcha"
                  title="点击刷新验证码"
                />
                <button v-else type="button" class="captcha-btn" @click="loadCaptcha">
                  获取验证码
                </button>
              </div>
              <span v-if="errors.code" class="error-msg">{{ errors.code }}</span>
            </div>

            <div v-if="errorMsg" class="error-msg error-msg-global">{{ errorMsg }}</div>

            <div class="form-options">
              <label class="checkbox-label">
                <input type="checkbox" v-model="form.remember" class="checkbox-input" />
                <span class="checkbox-custom"></span>
                <span class="checkbox-text">记住我</span>
              </label>
            </div>

            <button type="submit" class="submit-btn" :disabled="loading">
              <span v-if="loading" class="btn-loading"></span>
              <span v-else>登 录</span>
            </button>
          </form>

          <p class="form-footer">
            还没有账号?
            <router-link to="/register" class="form-link">立即注册</router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  position: relative;
  width: 100%;
  min-height: 100dvh;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
  font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #f0f4ff;
  overflow: hidden;
}

/* ===== Logo ===== */
.logo-link {
  position: fixed;
  top: 24px;
  left: 24px;
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  z-index: 10;
}

.logo-img {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  object-fit: cover;
  box-shadow: 0 2px 8px rgba(74, 144, 217, 0.15);
}

.logo-text {
  font-size: 1.1rem;
  font-weight: 700;
  color: #2c3e50;
  letter-spacing: -0.02em;
}

/* ===== 主容器 ===== */
.login-container {
  display: flex;
  width: 100%;
  max-width: 960px;
  min-height: 520px;
  z-index: 1;
  padding: 20px;
  gap: 0;
  animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) both;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ===== 左栏品牌 ===== */
.brand-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 20px 0 0 20px;
  border: 1px solid rgba(74, 144, 217, 0.12);
  border-right: none;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.brand-content {
  max-width: 320px;
}

.brand-title {
  font-size: 2.4rem;
  font-weight: 800;
  margin: 0 0 12px;
  background: linear-gradient(135deg, #2c3e50 0%, #4A90D9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.02em;
}

.brand-desc {
  font-size: 0.95rem;
  color: #7a8ba8;
  margin: 0 0 32px;
  line-height: 1.6;
}

.feature-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.95rem;
  color: #5a6a7e;
}

.feature-icon {
  flex-shrink: 0;
}

/* ===== 右栏表单 ===== */
.form-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-radius: 0 20px 20px 0;
  border: 1px solid rgba(74, 144, 217, 0.1);
}

.form-card {
  width: 100%;
  max-width: 340px;
}

.form-title {
  font-size: 1.6rem;
  font-weight: 700;
  margin: 0 0 4px;
  color: #2c3e50;
  letter-spacing: -0.02em;
}

.form-subtitle {
  font-size: 0.9rem;
  color: #8a9bb5;
  margin: 0 0 32px;
}

/* ===== 表单 ===== */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 0.85rem;
  color: #5a6a7e;
  font-weight: 500;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #dce3ef;
  border-radius: 10px;
  background: #fff;
  color: #333;
  font-size: 0.95rem;
  font-family: inherit;
  outline: none;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  box-sizing: border-box;
}

.form-input::placeholder {
  color: #b0bccf;
}

.form-input:focus {
  border-color: #4A90D9;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(74, 144, 217, 0.12);
}

.form-input.input-error {
  border-color: #ff4d4f;
  background: #fff;
}

.form-input.input-error:focus {
  box-shadow: 0 0 0 3px rgba(255, 77, 79, 0.12);
}

.error-msg {
  font-size: 0.8rem;
  color: #ff4d4f;
  margin-top: 2px;
}

.error-msg-global {
  text-align: center;
  padding: 8px;
  background: rgba(255, 77, 79, 0.06);
  border-radius: 8px;
  border: 1px solid rgba(255, 77, 79, 0.15);
  color: #ff4d4f;
}

/* ===== 选项 ===== */
.form-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
}

.checkbox-input {
  display: none;
}

.checkbox-custom {
  width: 16px;
  height: 16px;
  border: 1px solid #d0d7e6;
  border-radius: 4px;
  position: relative;
  transition: all 0.2s ease;
  flex-shrink: 0;
  background: #fff;
}

.checkbox-input:checked + .checkbox-custom {
  background: #4A90D9;
  border-color: #4A90D9;
}

.checkbox-input:checked + .checkbox-custom::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 5px;
  width: 4px;
  height: 8px;
  border: solid #fff;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.checkbox-text {
  font-size: 0.85rem;
  color: #7a8ba8;
}

/* ===== 提交按钮 ===== */
.submit-btn {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #4A90D9 0%, #357ABD 100%);
  color: #fff;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  font-family: inherit;
  letter-spacing: 0.05em;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 48px;
}

.submit-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #5B9EE0 0%, #3D86C9 100%);
  box-shadow: 0 4px 16px rgba(74, 144, 217, 0.35);
  transform: translateY(-1px);
}

.submit-btn:active:not(:disabled) {
  transform: translateY(0);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-loading {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ===== 底部链接 ===== */
.form-footer {
  text-align: center;
  margin-top: 24px;
  font-size: 0.85rem;
  color: #8a9bb5;
}

.form-link {
  color: #4A90D9;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s ease;
}

.form-link:hover {
  color: #357ABD;
  text-decoration: underline;
}

/* ===== 验证码 ===== */
.captcha-row {
  display: flex;
  gap: 10px;
  width: 100%;
  align-items: center;
}

.captcha-input {
  flex: 1;
}

.captcha-img {
  height: 44px;
  border-radius: 8px;
  cursor: pointer;
  border: 1px solid #dce3ef;
  flex-shrink: 0;
  width: 120px;
  object-fit: cover;
}

.captcha-btn {
  flex-shrink: 0;
  height: 44px;
  padding: 0 16px;
  border: 1px solid #d0d7e6;
  border-radius: 8px;
  background: #fff;
  color: #5a6a7e;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
  font-family: inherit;
  white-space: nowrap;
}

.captcha-btn:hover {
  background: #f0f4ff;
  border-color: #4A90D9;
  color: #4A90D9;
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
    max-width: 440px;
    min-height: auto;
  }

  .brand-section {
    border-radius: 20px 20px 0 0;
    border-right: 1px solid rgba(74, 144, 217, 0.12);
    border-bottom: none;
    padding: 32px 24px;
  }

  .brand-content {
    max-width: 100%;
    text-align: center;
  }

  .feature-list {
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: center;
  }

  .form-section {
    border-radius: 0 0 20px 20px;
    padding: 32px 24px;
  }
}
</style>