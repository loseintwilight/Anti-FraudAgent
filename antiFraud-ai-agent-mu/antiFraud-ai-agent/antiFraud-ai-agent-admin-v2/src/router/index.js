import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/login.vue'),
    meta: { title: '登录', noLayout: true },
  },
  {
    path: '/',
    component: () => import('../layout/index.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/dashboard.vue'),
        meta: { title: '仪表盘', icon: 'DataBoard' },
      },
      {
        path: 'detection',
        name: 'Detection',
        component: () => import('../views/detection/index.vue'),
        meta: { title: '检测记录', icon: 'Search' },
      },
      {
        path: 'report',
        name: 'Report',
        component: () => import('../views/report/index.vue'),
        meta: { title: '报告管理', icon: 'Document' },
      },
      {
        path: 'blacklist',
        name: 'Blacklist',
        component: () => import('../views/blacklist/index.vue'),
        meta: { title: '黑名单管理', icon: 'WarningFilled' },
      },
      {
        path: 'system/user',
        name: 'SystemUser',
        component: () => import('../views/system/user.vue'),
        meta: { title: '用户管理', icon: 'User' },
      },
      {
        path: 'system/role',
        name: 'SystemRole',
        component: () => import('../views/system/role.vue'),
        meta: { title: '角色管理', icon: 'Avatar' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('admin_token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router