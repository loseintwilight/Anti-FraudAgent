<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const searchKeyword = ref('')
const caseData = ref([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const activeCaseId = ref(null)

const fraudTypeOptions = [
  { value: '', label: '全部' },
  { value: '刷单诈骗', label: '刷单诈骗' },
  { value: '冒充客服', label: '冒充客服' },
  { value: '投资理财', label: '投资理财' },
  { value: '网络贷款', label: '网络贷款' },
  { value: '冒充公检法', label: '冒充公检法' },
  { value: '虚假购物', label: '虚假购物' },
]

const caseStatusOptions = [
  { value: '', label: '全部' },
  { value: 'pending', label: '待处理' },
  { value: 'processing', label: '处理中' },
  { value: 'closed', label: '已结案' },
]

const selectedFraudType = ref('')
const selectedStatus = ref('')

const caseDetails = ref({})

function generateMockCases() {
  const names = ['王**', '李**', '赵**', '孙**', '周**', '吴**', '郑**', '冯**', '陈**', '褚**', '卫**', '蒋**']
  const fraudTypes = ['刷单诈骗', '冒充客服', '投资理财', '网络贷款', '冒充公检法', '虚假购物']
  const riskLevels = ['high', 'medium', 'low']
  const statuses = ['pending', 'processing', 'closed']
  const contents = [
    '用户被诱导进行刷单返利活动，累计损失 12.5 万元',
    '冒充客服以退款为由骗取用户银行卡信息',
    '虚假投资理财平台诱导用户充值 20 万元',
    '以低息贷款为幌子骗取用户手续费 1.5 万元',
    '冒充公检法人员恐吓用户转账至安全账户',
    '在虚假购物网站购买商品后无法联系卖家',
    '通过社交平台诱导用户参与虚拟货币投资',
    '冒充领导要求财务人员转账',
    '以高薪兼职为名收取培训费后失联',
    '冒充银行客服以提升额度为由骗取验证码',
    '虚假中奖信息要求用户先支付税费',
    '以婚恋交友为名诱导用户进行投资',
  ]

  const data = []
  for (let i = 0; i < 48; i++) {
    const id = 3001 + i
    const fraudType = fraudTypes[Math.floor(Math.random() * fraudTypes.length)]
    const riskLevel = riskLevels[Math.floor(Math.random() * riskLevels.length)]
    const status = statuses[Math.floor(Math.random() * statuses.length)]
    const name = names[Math.floor(Math.random() * names.length)]
    const content = contents[Math.floor(Math.random() * contents.length)]
    const month = String(4 + Math.floor(Math.random() * 4)).padStart(2, '0')
    const day = String(1 + Math.floor(Math.random() * 28)).padStart(2, '0')

    data.push({
      id,
      caseNo: `AF${2026}${month}${String(id).slice(-4)}`,
      userName: name,
      fraudType,
      riskLevel,
      status,
      content,
      amount: Math.round(Math.random() * 500000 + 1000),
      createdTime: `2026-${month}-${day} ${String(Math.floor(Math.random() * 24)).padStart(2, '0')}:${String(Math.floor(Math.random() * 60)).padStart(2, '0')}:00`,
    })
  }
  return data
}

const mockCases = generateMockCases()

function generateCaseDetail(caseItem) {
  return {
    id: caseItem.id,
    caseNo: caseItem.caseNo,
    userName: caseItem.userName,
    fraudType: caseItem.fraudType,
    riskLevel: caseItem.riskLevel,
    status: caseItem.status,
    amount: caseItem.amount,
    createdTime: caseItem.createdTime,
    content: caseItem.content,
    processRecords: [
      { time: caseItem.createdTime, action: '系统自动检测到异常行为', operator: '系统', result: '生成预警' },
      { time: '2026-07-10 14:30:00', action: '网格员介入调查', operator: '张建国', result: '联系用户核实情况' },
      { time: '2026-07-11 09:20:00', action: '调取通话记录和转账记录', operator: '李警官', result: '确认诈骗事实' },
      { time: '2026-07-12 16:45:00', action: '提交案件报告', operator: '张建国', result: '等待审核' },
    ],
    chatRecords: [
      { time: '2026-07-10 14:35:00', sender: '网格员', content: '您好，我是反诈中心网格员张建国，我们检测到您近期有异常转账行为，请问您最近是否接到过可疑电话？' },
      { time: '2026-07-10 14:38:00', sender: '用户', content: '是的，昨天有人给我打电话说我在网上买的商品有问题要退款，让我下载了一个APP操作。' },
      { time: '2026-07-10 14:40:00', sender: '网格员', content: '这是典型的冒充客服诈骗，请您立即停止操作，不要再向任何账户转账。我们马上安排人员上门核实。' },
      { time: '2026-07-10 14:42:00', sender: '用户', content: '好的，谢谢你们提醒，我已经转了 2 万了，现在怎么办？' },
      { time: '2026-07-10 14:45:00', sender: '网格员', content: '请保留好所有转账记录和通话记录，我们已启动紧急止付程序，会尽力为您追回损失。' },
    ],
    reportInfo: {
      totalLoss: caseItem.amount,
      recoveredAmount: Math.round(caseItem.amount * 0.3),
      involvedAccounts: 3,
      involvedPhones: 2,
      caseLevel: caseItem.riskLevel === 'high' ? '重大案件' : caseItem.riskLevel === 'medium' ? '一般案件' : '轻微案件',
      summary: '经调查，该案件为典型的冒充客服退款诈骗。诈骗分子通过非法渠道获取用户购物信息，冒充平台客服以商品质量问题为由，诱导用户下载远程控制APP并输入银行卡信息，最终实施盗刷。',
      suggestion: '建议加强反诈宣传教育，提高群众防范意识。同时加强与电商平台的信息共享，从源头上阻断诈骗链条。',
    },
  }
}

function fetchData() {
  loading.value = true
  setTimeout(() => {
    let filtered = [...mockCases]

    if (searchKeyword.value) {
      const keyword = searchKeyword.value.toLowerCase()
      filtered = filtered.filter(
        (item) =>
          item.caseNo.toLowerCase().includes(keyword) ||
          item.userName.includes(keyword) ||
          item.fraudType.includes(keyword)
      )
    }
    if (selectedFraudType.value) {
      filtered = filtered.filter((item) => item.fraudType === selectedFraudType.value)
    }
    if (selectedStatus.value) {
      filtered = filtered.filter((item) => item.status === selectedStatus.value)
    }

    filtered.sort((a, b) => new Date(b.createdTime) - new Date(a.createdTime))
    total.value = filtered.length
    const start = (currentPage.value - 1) * pageSize.value
    const end = start + pageSize.value
    caseData.value = filtered.slice(start, end)
    loading.value = false
  }, 300)
}

function handleSearch() {
  currentPage.value = 1
  fetchData()
}

function handleReset() {
  searchKeyword.value = ''
  selectedFraudType.value = ''
  selectedStatus.value = ''
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
  const map = { pending: 'danger', processing: 'warning', closed: 'success' }
  return map[status] || 'info'
}

function getStatusLabel(status) {
  const map = { pending: '待处理', processing: '处理中', closed: '已结案' }
  return map[status] || '未知'
}

function handleExpandChange(row, expandedRows) {
  if (expandedRows.includes(row.id)) {
    activeCaseId.value = row.id
    if (!caseDetails.value[row.id]) {
      caseDetails.value[row.id] = generateCaseDetail(row)
    }
  } else {
    activeCaseId.value = null
  }
}

function handleChangeStatus(row, newStatus) {
  const statusMap = { processing: '处理中', closed: '已结案' }
  ElMessageBox.confirm(
    `确认将案件 ${row.caseNo} 状态变更为"${statusMap[newStatus]}"？`,
    '确认',
    { confirmButtonText: '确认', cancelButtonText: '取消', type: 'info' }
  ).then(() => {
    row.status = newStatus
    ElMessage.success(`案件状态已变更为"${statusMap[newStatus]}"`)
  }).catch(() => {})
}

function formatAmount(amount) {
  return '¥' + amount.toLocaleString()
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="page-container">
    <div class="page-header">
      <h2>案件追踪</h2>
    </div>

    <!-- 搜索和筛选 -->
    <div class="filter-bar">
      <div class="filter-item">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索案件编号、用户、诈骗类型"
          clearable
          style="width: 280px"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      <div class="filter-item">
        <span class="filter-label">诈骗类型：</span>
        <el-select
          v-model="selectedFraudType"
          placeholder="选择诈骗类型"
          clearable
          style="width: 140px"
          @change="handleSearch"
        >
          <el-option
            v-for="opt in fraudTypeOptions"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </el-select>
      </div>
      <div class="filter-item">
        <span class="filter-label">案件状态：</span>
        <el-select
          v-model="selectedStatus"
          placeholder="选择状态"
          clearable
          style="width: 140px"
          @change="handleSearch"
        >
          <el-option
            v-for="opt in caseStatusOptions"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </el-select>
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

    <!-- 案件表格 -->
    <el-table
      :data="caseData"
      v-loading="loading"
      stripe
      style="width: 100%"
      row-key="id"
      @expand-change="handleExpandChange"
    >
      <el-table-column type="expand" width="50">
        <template #default="{ row }">
          <div v-if="caseDetails[row.id]" class="case-detail-container">
            <el-tabs type="border-card">
              <el-tab-pane label="处理记录">
                <el-timeline>
                  <el-timeline-item
                    v-for="(record, idx) in caseDetails[row.id].processRecords"
                    :key="idx"
                    :timestamp="record.time"
                    placement="top"
                  >
                    <div class="process-record">
                      <span class="record-action">{{ record.action }}</span>
                      <span class="record-operator">操作人：{{ record.operator }}</span>
                      <el-tag size="small" type="info">{{ record.result }}</el-tag>
                    </div>
                  </el-timeline-item>
                </el-timeline>
              </el-tab-pane>
              <el-tab-pane label="聊天记录">
                <div class="chat-records">
                  <div
                    v-for="(chat, idx) in caseDetails[row.id].chatRecords"
                    :key="idx"
                    class="chat-item"
                    :class="{ 'chat-grid': chat.sender === '网格员', 'chat-user': chat.sender === '用户' }"
                  >
                    <div class="chat-sender">{{ chat.sender }}</div>
                    <div class="chat-bubble">{{ chat.content }}</div>
                    <div class="chat-time">{{ chat.time }}</div>
                  </div>
                </div>
              </el-tab-pane>
              <el-tab-pane label="报告信息">
                <el-descriptions :column="2" border size="small">
                  <el-descriptions-item label="总损失金额">{{ formatAmount(caseDetails[row.id].reportInfo.totalLoss) }}</el-descriptions-item>
                  <el-descriptions-item label="已追回金额">{{ formatAmount(caseDetails[row.id].reportInfo.recoveredAmount) }}</el-descriptions-item>
                  <el-descriptions-item label="涉及账户数">{{ caseDetails[row.id].reportInfo.involvedAccounts }} 个</el-descriptions-item>
                  <el-descriptions-item label="涉及电话号码">{{ caseDetails[row.id].reportInfo.involvedPhones }} 个</el-descriptions-item>
                  <el-descriptions-item label="案件等级">{{ caseDetails[row.id].reportInfo.caseLevel }}</el-descriptions-item>
                  <el-descriptions-item label="创建时间">{{ caseDetails[row.id].createdTime }}</el-descriptions-item>
                </el-descriptions>
                <div style="margin-top: 16px">
                  <h4 style="font-size: 14px; font-weight: 600; margin-bottom: 8px">案件摘要</h4>
                  <p style="font-size: 13px; color: #606266; line-height: 1.8">{{ caseDetails[row.id].reportInfo.summary }}</p>
                </div>
                <div style="margin-top: 12px">
                  <h4 style="font-size: 14px; font-weight: 600; margin-bottom: 8px">处置建议</h4>
                  <p style="font-size: 13px; color: #606266; line-height: 1.8">{{ caseDetails[row.id].reportInfo.suggestion }}</p>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="caseNo" label="案件编号" width="140" />
      <el-table-column prop="userName" label="用户" width="90" />
      <el-table-column prop="fraudType" label="诈骗类型" width="110" />
      <el-table-column prop="riskLevel" label="风险等级" width="90">
        <template #default="{ row }">
          <el-tag :type="getRiskTagType(row.riskLevel)" size="small" effect="dark">
            {{ getRiskLabel(row.riskLevel) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="getStatusTagType(row.status)" size="small">
            {{ getStatusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="amount" label="涉案金额" width="120" sortable>
        <template #default="{ row }">
          <span style="color: #F56C6C; font-weight: 600">{{ formatAmount(row.amount) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="createdTime" label="创建时间" width="160" sortable />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button
            type="primary"
            link
            size="small"
            :disabled="row.status === 'processing' || row.status === 'closed'"
            @click="handleChangeStatus(row, 'processing')"
          >
            开始处理
          </el-button>
          <el-button
            type="success"
            link
            size="small"
            :disabled="row.status === 'closed'"
            @click="handleChangeStatus(row, 'closed')"
          >
            结案
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

.case-detail-container {
  padding: 12px 0;
}

.process-record {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.record-action {
  font-size: 13px;
  color: #303133;
}

.record-operator {
  font-size: 12px;
  color: #909399;
}

.chat-records {
  max-height: 400px;
  overflow-y: auto;
}

.chat-item {
  margin-bottom: 16px;
}

.chat-sender {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.chat-grid .chat-sender {
  color: #409EFF;
}

.chat-user .chat-sender {
  color: #67C23A;
}

.chat-bubble {
  display: inline-block;
  max-width: 80%;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.6;
  background: #f0f2f5;
  color: #303133;
}

.chat-grid .chat-bubble {
  background: #ecf5ff;
  border-bottom-left-radius: 2px;
}

.chat-user .chat-bubble {
  background: #f0f9eb;
  border-bottom-right-radius: 2px;
}

.chat-time {
  font-size: 11px;
  color: #c0c4cc;
  margin-top: 4px;
}
</style>