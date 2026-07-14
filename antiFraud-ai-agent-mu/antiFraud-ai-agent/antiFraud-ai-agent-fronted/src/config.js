/** 后端接口前缀，可通过环境变量 VITE_API_BASE 覆盖 */
export const API_BASE =
  import.meta.env.VITE_API_BASE?.replace(/\/$/, '') ||
  'http://localhost:8123/api'
