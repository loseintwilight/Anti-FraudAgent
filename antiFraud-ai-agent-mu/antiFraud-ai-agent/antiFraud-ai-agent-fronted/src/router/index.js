import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'landing', component: () => import('../views/LandingPage.vue') },
    { path: '/login', name: 'login', component: () => import('../views/LoginPage.vue') },
    { path: '/register', name: 'register', component: () => import('../views/RegisterPage.vue') },
    { path: '/fraud', name: 'fraud', component: () => import('../views/LoveAppView.vue') },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

export default router