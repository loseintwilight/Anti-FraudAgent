import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const request = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json;charset=utf-8',
  },
})

// 是否显示重新登录
let isRelogin = { show: false }

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('admin_token')
    if (token) {
      config.headers['Authorization'] = 'Bearer ' + token
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const res = response.data
    // 如果后端返回了 code，按 code 处理
    if (res.code !== undefined) {
      if (res.code === 401) {
        if (!isRelogin.show) {
          isRelogin.show = true
          ElMessageBox.confirm('登录状态已过期，请重新登录', '系统提示', {
            confirmButtonText: '重新登录',
            cancelButtonText: '取消',
            type: 'warning',
          })
            .then(() => {
              isRelogin.show = false
              localStorage.removeItem('admin_token')
              window.location.href = '/login'
            })
            .catch(() => {
              isRelogin.show = false
            })
        }
        return Promise.reject(new Error('登录状态已过期'))
      } else if (res.code === 403) {
        ElMessage.error('没有权限访问该资源')
        return Promise.reject(new Error('权限不足'))
      } else if (res.code !== 200) {
        ElMessage.error(res.msg || res.message || '请求失败')
        return Promise.reject(new Error(res.msg || res.message || '请求失败'))
      }
      return res
    }
    // 如果后端没有 code 字段，直接返回数据
    return res
  },
  (error) => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          if (!isRelogin.show) {
            isRelogin.show = true
            ElMessageBox.confirm('登录状态已过期，请重新登录', '系统提示', {
              confirmButtonText: '重新登录',
              cancelButtonText: '取消',
              type: 'warning',
            })
              .then(() => {
                isRelogin.show = false
                localStorage.removeItem('admin_token')
                window.location.href = '/login'
              })
              .catch(() => {
                isRelogin.show = false
              })
          }
          break
        case 403:
          ElMessage.error('没有权限访问该资源')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(`请求失败: ${error.response.status}`)
      }
    } else if (error.request) {
      ElMessage.error('网络错误，请检查网络连接')
    }
    return Promise.reject(error)
  }
)

export default request