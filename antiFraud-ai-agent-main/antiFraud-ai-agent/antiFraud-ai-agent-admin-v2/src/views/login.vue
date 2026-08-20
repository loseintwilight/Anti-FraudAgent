<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import LightParticleBackground from '@/components/LightParticleBackground.vue'
import { login } from '@/api/login'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()

const loginForm = reactive({
  username: '',
  password: '',
  code: '',
  uuid: '',
})

const loading = ref(false)
const captchaImg = ref('')
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  code: [{ required: true, message: '请输入验证码', trigger: 'blur' }],
}

const formRef = ref(null)

async function loadCaptcha() {
  try {
    const res = await fetch('/api/v1/auth/captchaImage').then(r => r.json())
    if (res.success) {
      captchaImg.value = res.img
      loginForm.uuid = res.uuid
    }
  } catch (e) {
    console.error('加载验证码失败:', e)
  }
}

function handleLogin() {
  formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      const res = await login(loginForm.username, loginForm.password, loginForm.code, loginForm.uuid)
      const token = res.token || res.data?.token
      if (token) {
        userStore.setToken(token)
        if (res.user || res.data?.user) {
          userStore.setUserInfo(res.user || res.data?.user)
        }
        ElMessage.success('登录成功')
        router.push('/dashboard')
      } else {
        ElMessage.error(res.msg || res.message || '登录失败')
        loadCaptcha()
      }
    } catch (err) {
      ElMessage.error(err.message || '登录失败，请检查网络连接')
      loadCaptcha()
    } finally {
      loading.value = false
    }
  })
}

onMounted(() => {
  loadCaptcha()
})
</script>

<template>
  <div class="login-container">
    <LightParticleBackground />
    <div class="login-header">
      <img src="@/assets/logo.png" class="logo" />
      <span class="title">反诈卫士管理后台</span>
    </div>
    <div class="login-card">
      <h2 class="login-title">欢迎登录</h2>
      <p class="login-subtitle">请使用管理员账号登录</p>
      <el-form
        ref="formRef"
        :model="loginForm"
        :rules="rules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="用户名"
            :prefix-icon="'User'"
            size="large"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="密码"
            show-password
            :prefix-icon="'Lock'"
            size="large"
          />
        </el-form-item>
        <!-- 验证码 -->
        <el-form-item prop="code">
          <div class="captcha-row">
            <el-input
              v-model="loginForm.code"
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
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="login-btn"
            @click="handleLogin"
          >
            登 录
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  position: relative;
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #333;
  overflow: hidden;
  background: #f0f4ff;
}

.login-header {
  position: absolute;
  top: 30px;
  left: 30px;
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 10;
}

.logo {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(74, 144, 217, 0.15);
}

.title {
  font-size: 20px;
  font-weight: 700;
  color: #2c3e50;
  letter-spacing: 0.5px;
}

.login-card {
  width: 420px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(74, 144, 217, 0.12);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(74, 144, 217, 0.08);
  z-index: 1;
  animation: fadeInUp 0.6s ease-out;
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

.login-title {
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 8px;
  text-align: center;
}

.login-subtitle {
  font-size: 14px;
  color: #8a9bb5;
  margin: 0 0 32px;
  text-align: center;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.login-form :deep(.el-input__wrapper) {
  background: #fff;
  border: 1px solid #dce3ef;
  border-radius: 10px;
  box-shadow: none;
  padding: 4px 16px;
}

.login-form :deep(.el-input__wrapper:hover) {
  border-color: rgba(74, 144, 217, 0.5);
}

.login-form :deep(.el-input__wrapper.is-focus) {
  border-color: #4A90D9;
  box-shadow: 0 0 0 3px rgba(74, 144, 217, 0.12);
}

.login-form :deep(.el-input__inner) {
  color: #333;
  height: 48px;
}

.login-form :deep(.el-input__inner::placeholder) {
  color: #b0bccf;
}

.login-form :deep(.el-input__prefix-inner) {
  color: #8a9bb5;
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.05em;
  border-radius: 10px;
  background: linear-gradient(135deg, #4A90D9 0%, #357ABD 100%);
  border: none;
  color: #fff;
  margin-top: 8px;
}

.login-btn:hover {
  background: linear-gradient(135deg, #5B9EE0 0%, #3D86C9 100%);
  box-shadow: 0 4px 16px rgba(74, 144, 217, 0.35);
}

/* 覆盖 Element Plus 默认样式 */
.login-form :deep(.el-form-item) {
  margin-bottom: 22px;
}

.login-form :deep(.el-form-item__error) {
  color: #ff4d4f;
  font-size: 12px;
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
  height: 48px;
  border-radius: 8px;
  cursor: pointer;
  border: 1px solid #dce3ef;
  flex-shrink: 0;
}

.captcha-btn {
  flex-shrink: 0;
  height: 48px;
  font-size: 13px;
}
</style>