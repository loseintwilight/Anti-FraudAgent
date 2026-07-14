import { createRouter, createWebHistory } from 'vue-router'
import LoveAppView from '../views/LoveAppView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'fraud', component: LoveAppView },
    { path: '/fraud', redirect: '/' },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

export default router
