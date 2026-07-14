<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { updateAlertStatus } from '../api/index.js'
import AlertDetail from '../components/AlertDetail.vue'

const loading = ref(false)
const alertData = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

const riskLevelOptions = [
  { value: '', label: '全部' },
  { value: 'high', label: '高风险' },
  { value: 'medium', label: '中风险' },
  { value: 'low', label: '低风险' },
]

const statusOptions = [
  { value: '', label: '全部' },
  { value: 'pending', label: '待处理' },
  { value: 'processing', label: '处理中' },
  { value: 'resolved', label: '已处理' },
  { value: 'ignored', label: '已忽略' },
]

const filters = ref({
  riskLevel: '',
  status: '',
  startTime: '',
  endTime: '',
})

const alertDetailVisible = ref(false)
const currentAlertId = ref(null)

function generateMockData() {
  const riskLevels = ['high', 'medium', 'low']
  const statuses = ['pending', 'processing', 'resolved', 'ignored']
  const names = ['王**', '李**', '赵**', '孙**', '周**', '吴**', '郑**', '冯**', '陈**', '褚**']
  const contents = [
    '向陌生账户转账 5 万元，疑似刷单诈骗',
    '接到冒充公检法诈骗电话，通话时长 45 分钟',
    '点击不明链接并填写银行卡信息',
    '下载虚假投资理财 APP 并充值 2 万元',
    '收到冒充客服退款诈骗短信',
    '在陌生网站填写个人身份信息及银行卡号',
    '被诱导购买虚拟货币进行投资',
    '收到虚假中奖信息并支付手续费',
    '被冒充熟人诈骗转账',
    '参与刷单返利活动投入资金',
  ]
  const data = []
  for (let i = 0; i < 56; i++) {
    const id = 1001 + i
    const riskLevel = riskLevels[Math.floor(Math.random() * riskLevels.length)]
    const status = statuses[Math.floor(Math.random() * statuses.length)]
    const name = names[Math.floor(Math.random() * names.length)]
    const content = contents[Math.floor(Math.random() * contents.length)]
    const hour = String(Math.floor(Math.random() * 24)).padStart(2, '0')
    const minute = String(Math.floor(Math.random() * 60)).padStart(2, '0')
    const second = String(Math.floor(Math.random() * 60)).padStart(2, '0')
    const day = String(1 + Math.floor(Math.random() * 14)).padStart(2, '0')
    data.push({
      id,
      userName: name,
      content,
      riskLevel,
      time: `2026-07-${day} ${hour}:${minute}:${second}`,
      status,
    })
  }
  return data
}

const mockData = generateMockData()

function fetchData() {
  loading.value = true
  setTimeout(() => {
    let filtered = [...mockData]

    if (filters.value.riskLevel) {
      filtered = filtered.filter((item) => item.riskLevel === filters.value.riskLevel)
    }
    if (filters.value.status) {
      filtered = filtered.filter((item) => item.status === filters.value.status)
    }
    if (filters.value.startTime) {
      filtered = filtered.filter((item) => item.time >= filters.value.startTime)
    }
    if (filters.value.endTime) {
      filtered = filtered.filter((item) => item.time <= filters.value.endTime + ' 23:59:59')
    }

    filtered.sort((a, b) => new Date(b.time) - new Date(a.time))

    total.value = filtered.length
    const start = (currentPage.value - 1) * pageSize.value
    const end = start + pageSize.value
    alertData.value = filtered.slice(start, end)
    loading.value = false
  }, 300)
}

function handleSearch() {
  currentPage.value = 1
  fetchData()
}

function handleReset() {
  filters.value = {
    riskLevel: '',
    status: '',
    startTime: '',
    endTime: '',
  }
  currentPage.value = 1
  fetchData()
}

function handlePageChange(page) {
  currentPage.value = page
  fetchData()
}

function handlePageSizeChange(size) {
  pageSize.value = size
  currentPage.value = 1
  fetchData()
}

function getRiskTagType(level) {
  const map = { high: 'danger', medium: 'warning', low: 'info' }
  return map[level] || 'info'
}

function getRiskLabel(level) {
  const map = { high: '高风险', medium: '中风险', low: '低风险' }
  return map[level] || '未知'
}

function getStatusTagType(status) {
  const map = { pending: 'danger', processing: 'warning', resolved: 'success', ignored: 'info' }
  return map[status] || 'info'
}

function getStatusLabel(status) {
  const map = { pending: '待处理', processing: '处理中', resolved: '已处理', ignored: '已忽略' }
  return map[status] || '未知'
}

function viewDetail(row) {
  currentAlertId.value = row.id
  alertDetailVisible.value = true
}

function handleMarkProcessed(row) {
  ElMessageBox.confirm('确认将该预警标记为已处理？', '确认', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'info',
  }).then(() => {
    updateAlertStatus(row.id, 'resolved').then(() => {
      row.status = 'resolved'
      ElMessage.success('已标记为已处理')
    }).catch(() => {
      row.status = 'resolved'
      ElMessage.success('已标记为已处理')
    })
  }).catch(() => {})
}

function handleIgnore(row) {
  ElMessageBox.confirm('确认忽略该预警？', '确认', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    updateAlertStatus(row.id, 'ignored').then(() => {
      row.status = 'ignored'
      ElMessage.success('已忽略该预警')
    }).catch(() => {
      row.status = 'ignored'
      ElMessage.success('已忽略该预警')
    })
  }).catch(() => {})
}

function handleStatusUpdated({ id, status }) {
  const item = alertData.value.find((d) => d.id === id)
  if (item) {
    item.status = status
  }
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="page-container">
    <div class="page-header">
      <h2>预警列表</h2>
    </div>

    <!-- 筛选条件 -->
    <div class="filter-bar">
      <div class="filter-item">
        <span class="filter-label">风险等级：</span>
        <el-select
          v-model="filters.riskLevel"
          placeholder="选择风险等级"
          clearable
          style="width: 140px"
          @change="handleSearch"
        >
          <el-option
            v-for="opt in riskLevelOptions"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </el-select>
      </div>
      <div class="filter-item">
        <span class="filter-label">处理状态：</span>
        <el-select
          v-model="filters.status"
          placeholder="选择处理状态"
          clearable
          style="width: 140px"
          @change="handleSearch"
        >
          <el-option
            v-for="opt in statusOptions"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </el-select>
      </div>
      <div class="filter-item">
        <span class="filter-label">时间范围：</span>
        <el-date-picker
          v-model="filters.startTime"
          type="datetime"
          placeholder="开始时间"
          value-format="YYYY-MM-DD HH:mm:ss"
          style="width: 180px"
        />
        <span style="color: #909399">至</span>
        <el-date-picker
          v-model="filters.endTime"
          type="datetime"
          placeholder="结束时间"
          value-format="YYYY-MM-DD HH:mm:ss"
          style="width: 180px"
        />
      </div>
      <div class="filter-actions">
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        <el-button @click="handleReset">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
      </div>
    </div>

    <!-- 预警表格 -->
    <el-table
      :data="alertData"
      v-loading="loading"
      stripe
      style="width: 100%"
      @sort-change="handleSearch"
    >
      <el-table-column prop="id" label="ID" width="80" sortable />
      <el-table-column prop="userName" label="用户" width="100" />
      <el-table-column prop="content" label="内容摘要" min-width="280" show-overflow-tooltip />
      <el-table-column prop="riskLevel" label="风险等级" width="100" sortable>
        <template #default="{ row }">
          <el-tag :type="getRiskTagType(row.riskLevel)" size="small" effect="dark">
            {{ getRiskLabel(row.riskLevel) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="time" label="检测时间" width="170" sortable />
      <el-table-column prop="status" label="处理状态" width="100" sortable>
        <template #default="{ row }">
          <el-tag :type="getStatusTagType(row.status)" size="small">
            {{ getStatusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="viewDetail(row)">
            查看详情
          </el-button>
          <el-button
            type="success"
            link
            size="small"
            :disabled="row.status === 'resolved' || row.status === 'ignored'"
            @click="handleMarkProcessed(row)"
          >
            标记已处理
          </el-button>
          <el-button
            type="warning"
            link
            size="small"
            :disabled="row.status === 'resolved' || row.status === 'ignored'"
            @click="handleIgnore(row)"
          >
            忽略
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div style="display: flex; justify-content: flex-end; margin-top: 20px">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        background
        @size-change="handlePageSizeChange"
        @current-change="handlePageChange"
      />
    </div>

    <!-- 预警详情弹窗 -->
    <AlertDetail
      :alert-id="currentAlertId"
      :visible="alertDetailVisible"
      @update:visible="alertDetailVisible = $event"
      @status-updated="handleStatusUpdated"
    />
  </div>
</template>

<style scoped>
.filter-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 6px;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 13px;
  color: #909399;
  white-space: nowrap;
}

.filter-actions {
  display: flex;
  gap: 8px;
  margin-left: auto;
}
</style>