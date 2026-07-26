<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from './store/user.js'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const isCollapsed = ref(false)
const sidebarWidth = computed(() => (isCollapsed.value ? '64px' : '240px'))

const menuItems = [
  { path: '/', name: '数据看板', icon: 'DataBoard' },
  { path: '/alerts', name: '预警列表', icon: 'WarningFilled' },
  { path: '/grid', name: '网格员工作台', icon: 'UserFilled' },
  { path: '/cases', name: '案件追踪', icon: 'Document' },
  { path: '/stats', name: '统计报表', icon: 'DataAnalysis' },
]

function handleMenuSelect(index) {
  router.push(index)
}

function toggleSidebar() {
  isCollapsed.value = !isCollapsed.value
}

function handleLogout() {
  userStore.logout()
  router.push('/')
}
</script>

<template>
  <template v-if="!route.meta?.noLayout">
    <div class="admin-layout">
      <!-- 侧边栏 -->
      <aside class="admin-sidebar" :class="{ collapsed: isCollapsed }">
        <div class="sidebar-logo">
          <el-icon class="logo-icon" :size="24">
            <Shield />
          </el-icon>
          <span class="logo-text" :class="{ hidden: isCollapsed }">反诈卫士</span>
        </div>
        <div class="sidebar-menu">
          <el-menu
            :default-active="route.path"
            :collapse="isCollapsed"
            :collapse-transition="false"
            background-color="transparent"
            text-color="#a8a3b8"
            active-text-color="#165DFF"
            @select="handleMenuSelect"
          >
            <el-menu-item
              v-for="item in menuItems"
              :key="item.path"
              :index="item.path"
            >
              <el-icon>
                <component :is="item.icon" />
              </el-icon>
              <template #title>
                <span>{{ item.name }}</span>
              </template>
            </el-menu-item>
          </el-menu>
        </div>
        <div class="sidebar-toggle" @click="toggleSidebar">
          <el-icon :size="18">
            <Fold v-if="!isCollapsed" />
            <Expand v-else />
          </el-icon>
        </div>
      </aside>

      <!-- 主内容区 -->
      <div class="admin-main" :class="{ expanded: isCollapsed }">
        <!-- 顶部导航栏 -->
        <header class="admin-header">
          <div class="header-left">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
              <el-breadcrumb-item v-if="route.meta?.title">
                {{ route.meta.title }}
              </el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <div class="header-right">
            <el-tooltip content="消息通知" placement="bottom">
              <el-badge :value="3" :hidden="false" class="header-badge">
                <el-icon :size="20">
                  <Bell />
                </el-icon>
              </el-badge>
            </el-tooltip>
            <el-dropdown trigger="click">
              <div class="header-user">
                <el-avatar
                  :size="32"
                  icon="UserFilled"
                  style="background: #409EFF"
                />
                <span class="username">{{ userStore.userInfo.username || '管理员' }}</span>
                <el-icon>
                  <ArrowDown />
                </el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item>
                    <el-icon><User /></el-icon>
                    个人中心
                  </el-dropdown-item>
                  <el-dropdown-item>
                    <el-icon><Setting /></el-icon>
                    系统设置
                  </el-dropdown-item>
                  <el-dropdown-item divided @click="handleLogout">
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </header>

        <!-- 主内容 -->
        <main class="admin-content">
          <router-view />
        </main>
      </div>
    </div>
  </template>
  <template v-else>
    <router-view />
  </template>
</template>

<style scoped>
.header-badge {
  cursor: pointer;
  color: var(--text-secondary);
  transition: color 0.2s;
}

.header-badge:hover {
  color: var(--primary-color);
}

.el-menu {
  border-right: none;
  background: transparent !important;
}

.el-menu-item {
  display: flex;
  align-items: center;
  height: 44px;
  line-height: 44px;
  margin: 2px 8px;
  border-radius: 10px;
}
</style>