import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const userInfo = ref({
    id: null,
    username: 'admin',
    avatar: '',
    role: 'admin',
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

  function login(credentials) {
    // 模拟登录
    return new Promise((resolve) => {
      setTimeout(() => {
        const mockToken = 'mock_token_' + Date.now()
        setToken(mockToken)
        setUserInfo({
          id: 1,
          username: credentials.username || 'admin',
          role: 'admin',
        })
        resolve({
          token: mockToken,
          user: userInfo.value,
        })
      }, 300)
    })
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

  function getUserInfo() {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(userInfo.value)
      }, 200)
    })
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