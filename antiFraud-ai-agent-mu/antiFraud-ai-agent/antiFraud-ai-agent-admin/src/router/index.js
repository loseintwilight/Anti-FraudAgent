import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { title: '数据看板', icon: 'DataBoard' },
  },
  {
    path: '/alerts',
    name: 'AlertList',
    component: () => import('../views/AlertList.vue'),
    meta: { title: '预警列表', icon: 'Warning' },
  },
  {
    path: '/grid',
    name: 'GridMemberView',
    component: () => import('../views/GridMemberView.vue'),
    meta: { title: '网格员工作台', icon: 'User' },
  },
  {
    path: '/cases',
    name: 'CaseTracking',
    component: () => import('../views/CaseTracking.vue'),
    meta: { title: '案件追踪', icon: 'Document' },
  },
  {
    path: '/stats',
    name: 'ReportStats',
    component: () => import('../views/ReportStats.vue'),
    meta: { title: '统计报表', icon: 'DataAnalysis' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router