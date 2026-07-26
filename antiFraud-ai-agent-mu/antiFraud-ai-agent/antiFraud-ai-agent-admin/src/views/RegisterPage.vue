<template>
  <div class="register-page">
    <LightParticleBackground />
    <div class="register-card">
      <div class="register-header">
        <div class="register-logo">
          <el-icon :size="32"><Shield /></el-icon>
        </div>
        <h2 class="register-title">创建账号</h2>
        <p class="register-subtitle">注册反诈卫士管理后台</p>
      </div>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        class="register-form"
        @keyup.enter="handleRegister"
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
        <el-form-item prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="请确认密码"
            :prefix-icon="Lock"
            size="large"
            show-password
          />
        </el-form-item>
        <el-form-item prop="role">
          <el-radio-group v-model="form.role" class="role-group">
            <el-radio-button value="admin">管理员</el-radio-button>
            <el-radio-button value="grid">网格员</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="register-btn"
            :loading="loading"
            @click="handleRegister"
          >
            注 册
          </el-button>
        </el-form-item>
      </el-form>
      <div class="register-footer">
        <span>已有账号？</span>
        <router-link to="/login" class="login-link">立即登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import LightParticleBackground from '../components/LightParticleBackground.vue'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  role: 'admin',
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' },
  ],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
}

async function handleRegister() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    // 模拟注册请求
    await new Promise((resolve) => setTimeout(resolve, 500))
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (e) {
    ElMessage.error('注册失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  background: #f0f4ff;
}

.register-card {
  width: 420px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(74, 144, 217, 0.12);
  box-shadow: 0 8px 32px rgba(74, 144, 217, 0.08);
  position: relative;
  z-index: 1;
}

.register-header {
  text-align: center;
  margin-bottom: 32px;
}

.register-logo {
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

.register-title {
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 8px;
  letter-spacing: 1px;
}

.register-subtitle {
  font-size: 14px;
  color: #8a9bb5;
  margin: 0;
}

.register-form {
  margin-bottom: 8px;
}

.register-form :deep(.el-input__wrapper) {
  background: #fff;
  border: 1px solid #dce3ef;
  box-shadow: none;
  border-radius: 8px;
  transition: all 0.3s;
}

.register-form :deep(.el-input__wrapper:hover) {
  border-color: rgba(74, 144, 217, 0.5);
}

.register-form :deep(.el-input__wrapper.is-focus) {
  border-color: #4A90D9;
  box-shadow: 0 0 0 2px rgba(74, 144, 217, 0.12);
}

.register-form :deep(.el-input__inner) {
  color: #333;
  height: 44px;
}

.register-form :deep(.el-input__inner::placeholder) {
  color: #b0bccf;
}

.register-form :deep(.el-input__prefix) {
  color: #8a9bb5;
}

.register-form :deep(.el-radio-button__inner) {
  background: #fff;
  border: 1px solid #dce3ef;
  color: #7a8ba8;
  box-shadow: none;
  padding: 10px 32px;
  font-size: 14px;
  transition: all 0.3s;
}

.register-form :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: linear-gradient(135deg, #4A90D9, #357ABD);
  border-color: #4A90D9;
  color: #fff;
  box-shadow: none;
}

.register-form :deep(.el-radio-button:first-child .el-radio-button__inner) {
  border-radius: 8px 0 0 8px;
}

.register-form :deep(.el-radio-button:last-child .el-radio-button__inner) {
  border-radius: 0 8px 8px 0;
}

.role-group {
  width: 100%;
  display: flex;
}

.role-group :deep(.el-radio-button) {
  flex: 1;
}

.register-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  border-radius: 8px;
  background: linear-gradient(135deg, #4A90D9, #357ABD);
  border: none;
  letter-spacing: 2px;
  transition: all 0.3s;
}

.register-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(74, 144, 217, 0.35);
}

.register-footer {
  text-align: center;
  color: #8a9bb5;
  font-size: 14px;
}

.login-link {
  color: #4A90D9;
  text-decoration: none;
  margin-left: 4px;
  transition: color 0.2s;
}

.login-link:hover {
  color: #357ABD;
  text-decoration: underline;
}
</style>