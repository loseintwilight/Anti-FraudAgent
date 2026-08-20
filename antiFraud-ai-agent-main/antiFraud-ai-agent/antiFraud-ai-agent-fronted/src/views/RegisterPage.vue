<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import LightParticleBackground from '../components/LightParticleBackground.vue'

const router = useRouter()

const form = ref({
  username: '',
  phone: '',
  password: '',
  confirmPassword: '',
})

const errors = ref({
  username: '',
  phone: '',
  password: '',
  confirmPassword: '',
})

const errorMsg = ref('')
const loading = ref(false)
const registerSuccess = ref(false)

function validateForm() {
  let valid = true
  errors.value = {
    username: '',
    phone: '',
    password: '',
    confirmPassword: '',
  }

  if (!form.value.username.trim()) {
    errors.value.username = '请输入用户名'
    valid = false
  }

  if (!form.value.phone.trim()) {
    errors.value.phone = '请输入手机号'
    valid = false
  } else if (!/^1\d{10}$/.test(form.value.phone.trim())) {
    errors.value.phone = '请输入正确的手机号'
    valid = false
  }

  if (!form.value.password) {
    errors.value.password = '请输入密码'
    valid = false
  } else if (form.value.password.length < 6) {
    errors.value.password = '密码长度不少于6位'
    valid = false
  }

  if (!form.value.confirmPassword) {
    errors.value.confirmPassword = '请确认密码'
    valid = false
  } else if (form.value.password !== form.value.confirmPassword) {
    errors.value.confirmPassword = '两次密码不一致'
    valid = false
  }

  return valid
}

function handleRegister() {
  if (!validateForm()) return

  loading.value = true
  errorMsg.value = ''

  const API_BASE = '/admin-api/api'

  fetch(`${API_BASE}/v1/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: form.value.username.trim(),
      password: form.value.password,
      phone: form.value.phone.trim(),
    }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.code === 200) {
        loading.value = false
        registerSuccess.value = true
        // 初始化用户信息到 localStorage
        localStorage.setItem('antiFraud-user-info', JSON.stringify({
          nickname: form.value.username.trim() || '用户',
          role: 'youth',
          roleLabel: '青年',
          roleIcon: '',
          loginTime: new Date().toLocaleString('zh-CN'),
        }))
        setTimeout(() => {
          router.push('/login')
        }, 1500)
      } else {
        errorMsg.value = data.msg || '注册失败'
        loading.value = false
      }
    })
    .catch(() => {
      errorMsg.value = '网络错误，请检查后端服务是否启动'
      loading.value = false
    })
}
</script>

<template>
  <div class="register-page">
    <LightParticleBackground />

    <!-- 左上角 Logo -->
    <router-link to="/" class="logo-link">
      <img src="/src/assets/logo.png" alt="反诈卫士" class="logo-img" />
      <span class="logo-text">反诈卫士</span>
    </router-link>

    <div class="register-container">
      <!-- 左栏：品牌展示 -->
      <div class="brand-section">
        <div class="brand-content">
          <h1 class="brand-title">反诈卫士</h1>
          <p class="brand-desc">加入我们，共同守护数字安全</p>
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

      <!-- 右栏：注册表单 -->
      <div class="form-section">
        <div class="form-card">
          <!-- 注册成功提示 -->
          <div v-if="registerSuccess" class="success-overlay">
            <div class="success-icon">✓</div>
            <h2 class="success-title">注册成功！</h2>
            <p class="success-desc">正在跳转到登录页面...</p>
          </div>

          <!-- 注册表单 -->
          <template v-else>
            <h2 class="form-title">创建账号</h2>
            <p class="form-subtitle">注册成为反诈卫士用户</p>

            <form class="register-form" @submit.prevent="handleRegister">
              <div class="form-group">
                <label class="form-label" for="reg-username">用户名</label>
                <input
                  id="reg-username"
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
                <label class="form-label" for="reg-phone">手机号</label>
                <input
                  id="reg-phone"
                  v-model="form.phone"
                  type="tel"
                  class="form-input"
                  :class="{ 'input-error': errors.phone }"
                  placeholder="请输入手机号"
                  autocomplete="tel"
                />
                <span v-if="errors.phone" class="error-msg">{{ errors.phone }}</span>
              </div>

              <div class="form-group">
                <label class="form-label" for="reg-password">密码</label>
                <input
                  id="reg-password"
                  v-model="form.password"
                  type="password"
                  class="form-input"
                  :class="{ 'input-error': errors.password }"
                  placeholder="请输入密码（不少于6位）"
                  autocomplete="new-password"
                />
                <span v-if="errors.password" class="error-msg">{{ errors.password }}</span>
              </div>

              <div class="form-group">
                <label class="form-label" for="reg-confirm-password">确认密码</label>
                <input
                  id="reg-confirm-password"
                  v-model="form.confirmPassword"
                  type="password"
                  class="form-input"
                  :class="{ 'input-error': errors.confirmPassword }"
                  placeholder="请再次输入密码"
                  autocomplete="new-password"
                />
                <span v-if="errors.confirmPassword" class="error-msg">{{ errors.confirmPassword }}</span>
              </div>

              <div v-if="errorMsg" class="error-msg error-msg-global">{{ errorMsg }}</div>

              <button type="submit" class="submit-btn" :disabled="loading">
                <span v-if="loading" class="btn-loading"></span>
                <span v-else>注 册</span>
              </button>
            </form>

            <p class="form-footer">
              已有账号？
              <router-link to="/login" class="form-link">立即登录</router-link>
            </p>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.register-page {
  position: relative;
  width: 100%;
  min-height: 100dvh;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
  font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'PingFang SC', 'Microsoft YaHei', sans-serif;
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
.register-container {
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
  position: relative;
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
.register-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
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
  margin-top: 4px;
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

/* ===== 注册成功 ===== */
.success-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  animation: fadeInUp 0.5s ease-out;
}

.success-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4A90D9, #357ABD);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  font-weight: 700;
  color: #fff;
  margin-bottom: 20px;
  box-shadow: 0 4px 20px rgba(74, 144, 217, 0.4);
}

.success-title {
  font-size: 1.4rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 8px;
}

.success-desc {
  font-size: 0.9rem;
  color: #7a8ba8;
  margin: 0;
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .register-container {
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