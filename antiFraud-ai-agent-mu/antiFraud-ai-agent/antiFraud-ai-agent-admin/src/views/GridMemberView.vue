<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const gridWorker = ref({
  name: '张建国',
  avatar: '',
  area: '朝阳区建国路街道',
  todayProcessed: 8,
  totalProcessed: 156,
  phone: '138****9012',
})

const pendingTasks = ref([])
const completedTasks = ref([])
const activeTaskNames = ref([])

const riskLevelOptions = [
  { value: 'high', label: '高风险', type: 'danger' },
  { value: 'medium', label: '中风险', type: 'warning' },
  { value: 'low', label: '低风险', type: 'info' },
]

function generateMockTasks() {
  const names = ['王**', '李**', '赵**', '孙**', '周**', '吴**', '郑**']
  const addresses = ['建国路 88 号', '朝阳路 56 号', '光华路 12 号', '东三环中路 33 号', '西大望路 8 号', '望京西路 45 号', '酒仙桥路 18 号']
  const contents = [
    '疑似遭遇刷单诈骗，已向陌生账户转账 3 次',
    '接到可疑投资理财电话，已提供个人信息',
    '点击不明链接并下载了陌生 APP',
    '收到冒充公检法的诈骗电话，通话时长 30 分钟',
    '在虚假购物网站支付了定金',
    '被诱导参与网络博彩活动',
    '收到虚假中奖短信并点击了链接',
  ]

  const pending = []
  const completed = []

  for (let i = 0; i < 7; i++) {
    const riskIdx = Math.floor(Math.random() * 3)
    const risk = riskLevelOptions[riskIdx]
    const hour = String(Math.floor(Math.random() * 24)).padStart(2, '0')
    const minute = String(Math.floor(Math.random() * 60)).padStart(2, '0')
    const day = String(1 + Math.floor(Math.random() * 14)).padStart(2, '0')

    const task = {
      id: 2001 + i,
      userName: names[i],
      address: addresses[i],
      content: contents[i],
      riskLevel: risk.value,
      riskLabel: risk.label,
      riskType: risk.type,
      time: `2026-07-${day} ${hour}:${minute}`,
      userPhone: '138****' + String(1000 + Math.floor(Math.random() * 9000)),
    }

    if (i < 4) {
      pending.push(task)
    } else {
      task.completedTime = `2026-07-${String(parseInt(day) - 1).padStart(2, '0')} ${hour}:${minute}`
      completed.push(task)
    }
  }

  return { pending, completed }
}

function loadTasks() {
  const data = generateMockTasks()
  pendingTasks.value = data.pending
  completedTasks.value = data.completed
}

function handleContactUser(task) {
  ElMessage.success(`正在联系用户 ${task.userName}...`)
}

function handleMarkCompleted(task) {
  ElMessageBox.confirm(
    `确认将 ${task.userName} 的任务标记为已完成？`,
    '确认',
    {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'success',
    }
  ).then(() => {
    ElMessage.success('任务已标记为已完成')
    pendingTasks.value = pendingTasks.value.filter((t) => t.id !== task.id)
    task.completedTime = new Date().toLocaleString()
    completedTasks.value.unshift(task)
    gridWorker.value.todayProcessed++
  }).catch(() => {})
}

function handleReportUp(task) {
  ElMessageBox.confirm(
    `确认将 ${task.userName} 的预警上报至上级？`,
    '确认上报',
    {
      confirmButtonText: '确认上报',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    ElMessage.success('已成功上报至上级管理部门')
    pendingTasks.value = pendingTasks.value.filter((t) => t.id !== task.id)
  }).catch(() => {})
}

function getRiskBadgeClass(level) {
  return `risk-${level}`
}

onMounted(() => {
  loadTasks()
})
</script>

<template>
  <div class="grid-page">
    <!-- 网格员信息卡片 -->
    <div class="worker-card">
      <div class="worker-avatar">
        <el-avatar :size="72" icon="UserFilled" style="background: #409EFF" />
      </div>
      <div class="worker-info">
        <h3 class="worker-name">{{ gridWorker.name }}</h3>
        <div class="worker-meta">
          <span>
            <el-icon><Location /></el-icon>
            辖区：{{ gridWorker.area }}
          </span>
          <span>
            <el-icon><Phone /></el-icon>
            {{ gridWorker.phone }}
          </span>
        </div>
      </div>
      <div class="worker-stats">
        <div class="stat-item">
          <div class="stat-value">{{ gridWorker.todayProcessed }}</div>
          <div class="stat-label">今日处理</div>
        </div>
        <div class="stat-divider" />
        <div class="stat-item">
          <div class="stat-value">{{ gridWorker.totalProcessed }}</div>
          <div class="stat-label">累计处理</div>
        </div>
        <div class="stat-divider" />
        <div class="stat-item">
          <div class="stat-value">{{ pendingTasks.length }}</div>
          <div class="stat-label">待处理</div>
        </div>
      </div>
    </div>

    <!-- 待处理任务 -->
    <div class="section-header">
      <h3>待处理任务 ({{ pendingTasks.length }})</h3>
    </div>
    <div v-if="pendingTasks.length === 0" class="empty-state">
      <el-icon :size="48" color="#C0C4CC"><CircleCheck /></el-icon>
      <p>暂无待处理任务</p>
    </div>
    <div v-else class="task-card-list">
      <div
        v-for="task in pendingTasks"
        :key="task.id"
        class="task-card"
        :class="getRiskBadgeClass(task.riskLevel)"
      >
        <div class="task-header">
          <div class="task-user">
            <el-avatar :size="32" icon="User" style="background: #909399; margin-right: 8px" />
            {{ task.userName }}
          </div>
          <el-tag :type="task.riskType" size="small" effect="dark">
            {{ task.riskLabel }}
          </el-tag>
        </div>
        <div class="task-body">
          <div class="task-desc">{{ task.content }}</div>
          <div class="task-meta">
            <span>
              <el-icon><Location /></el-icon>
              {{ task.address }}
            </span>
            <span>
              <el-icon><Phone /></el-icon>
              {{ task.userPhone }}
            </span>
          </div>
          <div class="task-time">
            <el-icon><Clock /></el-icon>
            检测时间：{{ task.time }}
          </div>
        </div>
        <div class="task-footer">
          <div class="task-actions">
            <el-button type="primary" size="small" @click="handleContactUser(task)">
              <el-icon><Message /></el-icon>
              联系用户
            </el-button>
            <el-button type="success" size="small" @click="handleMarkCompleted(task)">
              <el-icon><CircleCheck /></el-icon>
              标记已完成
            </el-button>
            <el-button type="warning" size="small" @click="handleReportUp(task)">
              <el-icon><Top /></el-icon>
              上报
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 已完成任务 -->
    <div class="section-header" style="margin-top: 24px">
      <h3>已完成任务</h3>
    </div>
    <el-collapse v-model="activeTaskNames" accordion>
      <el-collapse-item
        v-for="task in completedTasks"
        :key="task.id"
        :title="task.userName + ' - ' + task.content"
        :name="String(task.id)"
      >
        <div class="completed-task-detail">
          <el-descriptions :column="2" size="small" border>
            <el-descriptions-item label="用户姓名">{{ task.userName }}</el-descriptions-item>
            <el-descriptions-item label="联系电话">{{ task.userPhone }}</el-descriptions-item>
            <el-descriptions-item label="地址">{{ task.address }}</el-descriptions-item>
            <el-descriptions-item label="风险等级">
              <el-tag :type="task.riskType" size="small">{{ task.riskLabel }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="检测时间">{{ task.time }}</el-descriptions-item>
            <el-descriptions-item label="完成时间">{{ task.completedTime }}</el-descriptions-item>
          </el-descriptions>
          <div class="completed-task-content">
            <p>{{ task.content }}</p>
          </div>
        </div>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<style scoped>
.grid-page {
  max-width: 1400px;
  margin: 0 auto;
}

.worker-card {
  background: linear-gradient(135deg, #409EFF 0%, #337ecc 100%);
  border-radius: 12px;
  padding: 28px 32px;
  display: flex;
  align-items: center;
  gap: 24px;
  color: #fff;
  margin-bottom: 24px;
  box-shadow: 0 4px 20px rgba(64, 158, 255, 0.3);
}

.worker-avatar {
  flex-shrink: 0;
}

.worker-info {
  flex: 1;
}

.worker-name {
  font-size: 22px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #fff;
}

.worker-meta {
  display: flex;
  gap: 24px;
  font-size: 13px;
  opacity: 0.9;
}

.worker-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.worker-stats {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-shrink: 0;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.2;
}

.stat-label {
  font-size: 12px;
  opacity: 0.8;
  margin-top: 2px;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: rgba(255, 255, 255, 0.3);
}

.section-header {
  margin-bottom: 16px;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.empty-state {
  text-align: center;
  padding: 48px 0;
  color: #C0C4CC;
}

.empty-state p {
  margin-top: 12px;
  font-size: 14px;
}

.task-meta {
  display: flex;
  gap: 16px;
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

.task-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.task-time {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.completed-task-detail {
  padding: 12px 0;
}

.completed-task-content {
  margin-top: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
}
</style>