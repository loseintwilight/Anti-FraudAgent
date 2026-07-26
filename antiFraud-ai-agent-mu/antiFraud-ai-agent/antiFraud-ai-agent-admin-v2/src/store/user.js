import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import request from '@/utils/request'

export const useUserStore = defineStore('user', () => {
  const userInfo = ref({
    id: null,
    username: '',
    avatar: '',
    role: '',
  })
  const token = ref(localStorage.getItem('admin_token') || '')

  const isLoggedIn = computed(() => !!token.value)

  function setUserInfo(info) {
    userInfo.value = { ...userInfo.value, ...info }
  }

  function setToken(newToken) {
    token.value = newToken
    localStorage.setItem('admin_token', newToken)
  }

  async function login(credentials) {
    const res = await request.post('/auth/login', {
      username: credentials.username,
      password: credentials.password,
    })
    if (res.code === 200 || res.success) {
      setToken(res.token || res.data?.token)
      setUserInfo(res.user || res.data?.user)
      return res
    }
    throw new Error(res.message || res.msg || '登录失败')
  }

  function logout() {
    token.value = ''
    userInfo.value = {
      id: null,
      username: '',
      avatar: '',
      role: '',
    }
    localStorage.removeItem('admin_token')
  }

  async function getUserInfo() {
    if (!token.value) return null
    try {
      const res = await request.get('/auth/userinfo')
      if (res.code === 200 || res.success) {
        setUserInfo(res.user || res.data)
        return res.user || res.data
      }
    } catch {
      return null
    }
  }

  return {
    userInfo,
    token,
    isLoggedIn,
    setUserInfo,
    setToken,
    login,
    logout,
    getUserInfo,
  }
})