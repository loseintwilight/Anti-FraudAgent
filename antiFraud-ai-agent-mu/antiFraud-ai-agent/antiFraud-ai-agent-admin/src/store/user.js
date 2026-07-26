import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import http from '../api/index.js'

export const useUserStore = defineStore('user', () => {
  const userInfo = ref({
    id: null,
    username: '',
    avatar: '',
    role: '',
    gridArea: '',
  })
  const token = ref(localStorage.getItem('admin_token') || '')
  const isAdmin = ref(true)

  const isLoggedIn = computed(() => !!token.value)

  function setUserInfo(info) {
    userInfo.value = { ...userInfo.value, ...info }
  }

  function setToken(newToken) {
    token.value = newToken
    localStorage.setItem('admin_token', newToken)
  }

  async function login(credentials) {
    const res = await http.post('/v1/auth/login', {
      username: credentials.username,
      password: credentials.password,
      code: credentials.code,
      uuid: credentials.uuid,
    })
    if (res.success) {
      setToken(res.token)
      setUserInfo(res.user)
      return res
    }
    throw new Error(res.message || '登录失败')
  }

  function logout() {
    token.value = ''
    userInfo.value = {
      id: null,
      username: '',
      avatar: '',
      role: '',
      gridArea: '',
    }
    isAdmin.value = false
    localStorage.removeItem('admin_token')
  }

  async function getUserInfo() {
    if (!token.value) return null
    try {
      const res = await http.get('/v1/auth/userinfo', {
        headers: { Authorization: `Bearer ${token.value}` },
      })
      if (res.success) {
        setUserInfo(res.user)
        return res.user
      }
    } catch {
      return null
    }
  }

  return {
    userInfo,
    token,
    isAdmin,
    isLoggedIn,
    setUserInfo,
    setToken,
    login,
    logout,
    getUserInfo,
  }
})