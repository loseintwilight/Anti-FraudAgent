import { createStore } from 'vuex'
import { getHistory, getUserProfile } from '@/api/index.js'

const store = createStore({
  state: {
    userInfo: null,
    token: uni.getStorageSync('token') || '',
    historyList: [],
    currentReport: null
  },
  mutations: {
    SET_USER(state, userInfo) {
      state.userInfo = userInfo
    },
    SET_TOKEN(state, token) {
      state.token = token
      uni.setStorageSync('token', token)
    },
    SET_HISTORY(state, list) {
      state.historyList = list
    },
    APPEND_HISTORY(state, list) {
      state.historyList = [...state.historyList, ...list]
    },
    SET_REPORT(state, report) {
      state.currentReport = report
    },
    CLEAR_USER(state) {
      state.userInfo = null
      state.token = ''
      state.historyList = []
      state.currentReport = null
      uni.removeStorageSync('token')
      uni.removeStorageSync('userInfo')
    }
  },
  actions: {
    // 获取用户信息
    async fetchUserProfile({ commit }) {
      try {
        const res = await getUserProfile()
        commit('SET_USER', res.data || res)
        uni.setStorageSync('userInfo', res.data || res)
        return res
      } catch (err) {
        console.error('获取用户信息失败:', err)
        throw err
      }
    },
    // 获取历史记录
    async fetchHistory({ commit }, { page = 1, size = 10 } = {}) {
      try {
        const res = await getHistory(page, size)
        const list = res.data?.records || res.data || []
        if (page === 1) {
          commit('SET_HISTORY', list)
        } else {
          commit('APPEND_HISTORY', list)
        }
        return res
      } catch (err) {
        console.error('获取历史记录失败:', err)
        throw err
      }
    }
  }
})

export default store