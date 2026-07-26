import request from '@/utils/request'

/**
 * 登录
 * @param {string} username 用户名
 * @param {string} password 密码
 * @param {string} code 验证码
 * @param {string} uuid 验证码uuid
 */
export function login(username, password, code, uuid) {
  return request.post('/v1/auth/login', { username, password, code, uuid })
}

/**
 * 退出登录
 */
export function logout() {
  return request.post('/v1/auth/logout')
}

/**
 * 获取用户信息
 */
export function getUserInfo() {
  return request.get('/v1/auth/userinfo')
}

/**
 * 注册
 * @param {string} username 用户名
 * @param {string} password 密码
 */
export function register(username, password) {
  return request.post('/v1/auth/register', { username, password })
}