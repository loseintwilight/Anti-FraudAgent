// HTTP 请求工具 - 基于 uni.request 封装

const BASE_URL = 'http://localhost:8123'

// 请求拦截器
function requestInterceptor(config) {
  const token = uni.getStorageSync('token')
  if (token) {
    config.header = {
      ...config.header,
      'Authorization': `Bearer ${token}`
    }
  }
  return config
}

// 响应拦截器
function responseInterceptor(response) {
  const { statusCode, data } = response
  if (statusCode === 200) {
    return data
  } else if (statusCode === 401) {
    // token 过期，清除登录状态
    uni.removeStorageSync('token')
    uni.removeStorageSync('userInfo')
    uni.showToast({ title: '登录已过期，请重新登录', icon: 'none' })
    return Promise.reject(new Error('登录已过期'))
  } else {
    uni.showToast({
      title: data?.message || '请求失败',
      icon: 'none'
    })
    return Promise.reject(new Error(data?.message || '请求失败'))
  }
}

/**
 * 发起 HTTP 请求
 * @param {Object} options - 请求配置
 * @param {string} options.url - 请求地址
 * @param {string} [options.method='GET'] - 请求方法
 * @param {Object} [options.data] - 请求参数
 * @param {Object} [options.header] - 请求头
 * @returns {Promise}
 */
function request(options) {
  const config = requestInterceptor({
    url: `${BASE_URL}${options.url}`,
    method: options.method || 'GET',
    data: options.data || {},
    header: {
      'Content-Type': 'application/json',
      ...options.header
    }
  })

  return new Promise((resolve, reject) => {
    uni.request({
      ...config,
      success: (res) => {
        try {
          const result = responseInterceptor(res)
          resolve(result)
        } catch (err) {
          reject(err)
        }
      },
      fail: (err) => {
        uni.showToast({
          title: '网络连接失败，请检查网络',
          icon: 'none'
        })
        reject(err)
      }
    })
  })
}

export default request

export { BASE_URL }