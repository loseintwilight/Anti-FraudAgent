<template>
  <div class="login-page">
    <LightParticleBackground />

    <!-- 左上角 Logo -->
    <router-link to="/" class="logo-link">
      <img src="/src/assets/logo.png" alt="反诈卫士" class="logo-img" />
      <span class="logo-text">反诈卫士</span>
    </router-link>

    <div class="login-card">
      <div class="login-header">
        <div class="login-logo">
          <el-icon :size="32"><Shield /></el-icon>
        </div>
        <h2 class="login-title">管理后台</h2>
        <p class="login-subtitle">请登录您的账号</p>
      </div>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            :prefix-icon="User"
            size="large"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            size="large"
            show-password
          />
        </el-form-item>
        <!-- 验证码 -->
        <el-form-item prop="code">
          <div class="captcha-row">
            <el-input
              v-model="form.code"
              placeholder="验证码"
              size="large"
              class="captcha-input"
              maxlength="4"
            />
            <img
              v-if="captchaImg"
              :src="captchaImg"
              class="captcha-img"
              @click="loadCaptcha"
              title="点击刷新验证码"
            />
            <el-button v-else size="large" @click="loadCaptcha" class="captcha-btn">
              获取验证码
            </el-button>
          </div>
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="form.remember" class="custom-checkbox">记住我</el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-btn"
            :loading="loading"
            @click="handleLogin"
          >
            登 录
          </el-button>
        </el-form-item>
      </el-form>
      <div class="login-footer">
        <span>还没有账号?</span>
        <router-link to="/register" class="register-link">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user.js'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import LightParticleBackground from '../components/LightParticleBackground.vue'
import http from '../api/index.js'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)
const captchaImg = ref('')
const captchaUuid = ref('')

const form = reactive({
  username: '',
  password: '',
  code: '',
  remember: false,
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6位', trigger: 'blur' },
  ],
  code: [{ required: true, message: '请输入验证码', trigger: 'blur' }],
}

async function loadCaptcha() {
  try {
    const res = await http.get('/v1/auth/captchaImage')
    if (res.success) {
      captchaImg.value = res.img
      captchaUuid.value = res.uuid
    }
  } catch (e) {
    console.error('加载验证码失败:', e)
  }
}

async function handleLogin() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await userStore.login({
      username: form.username,
      password: form.password,
      code: form.code,
      uuid: captchaUuid.value,
    })
    ElMessage.success('登录成功')
    router.push('/')
  } catch (e) {
    ElMessage.error(e.message || '登录失败，请重试')
    // 刷新验证码
    loadCaptcha()
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadCaptcha()
})
</script>

<style scoped>
.login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100dvh;
  position: relative;
  overflow: hidden;
  background: #f0f4ff;
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

.login-card {
  width: 420px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-radius: 20px;
  border: 1px solid rgba(74, 144, 217, 0.12);
  box-shadow: 0 8px 32px rgba(74, 144, 217, 0.08);
  position: relative;
  z-index: 1;
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

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-logo {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  background: linear-gradient(135deg, #4A90D9, #7B68EE);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.login-title {
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 8px;
  letter-spacing: 1px;
}

.login-subtitle {
  font-size: 14px;
  color: #8a9bb5;
  margin: 0;
}

.login-form {
  margin-bottom: 8px;
}

.login-form :deep(.el-input__wrapper) {
  background: #fff;
  border: 1px solid #dce3ef;
  box-shadow: none;
  border-radius: 10px;
  transition: all 0.3s;
}

.login-form :deep(.el-input__wrapper:hover) {
  border-color: rgba(74, 144, 217, 0.5);
}

.login-form :deep(.el-input__wrapper.is-focus) {
  border-color: #4A90D9;
  box-shadow: 0 0 0 2px rgba(74, 144, 217, 0.12);
}

.login-form :deep(.el-input__inner) {
  color: #333;
  height: 44px;
}

.login-form :deep(.el-input__inner::placeholder) {
  color: #b0bccf;
}

.login-form :deep(.el-input__prefix) {
  color: #8a9bb5;
}

.login-form :deep(.el-checkbox__label) {
  color: #7a8ba8;
}

.custom-checkbox {
  color: #7a8ba8;
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  border-radius: 10px;
  background: linear-gradient(135deg, #4A90D9, #357ABD);
  border: none;
  letter-spacing: 2px;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.login-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(74, 144, 217, 0.35);
}

.login-footer {
  text-align: center;
  color: #8a9bb5;
  font-size: 14px;
}

.register-link {
  color: #4A90D9;
  text-decoration: none;
  margin-left: 4px;
  transition: color 0.2s;
}

.register-link:hover {
  color: #357ABD;
  text-decoration: underline;
}

/* 验证码 */
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
}

.captcha-btn {
  flex-shrink: 0;
  height: 44px;
  font-size: 13px;
}
</style>