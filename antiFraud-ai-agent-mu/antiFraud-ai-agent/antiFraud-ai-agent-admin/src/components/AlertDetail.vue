<script setup>
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  alertId: {
    type: [Number, String],
    default: null,
  },
  visible: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:visible', 'status-updated'])

const dialogVisible = ref(false)
const alertDetail = ref(null)
const loading = ref(false)

watch(
  () => props.visible,
  (val) => {
    dialogVisible.value = val
    if (val && props.alertId) {
      fetchAlertDetail()
    }
  }
)

watch(
  () => dialogVisible.value,
  (val) => {
    emit('update:visible', val)
  }
)

const riskScore = computed(() => {
  if (!alertDetail.value) return 0
  return alertDetail.value.riskScore || 0
})

const riskLevel = computed(() => {
  if (riskScore.value >= 80) return '高风险'
  if (riskScore.value >= 60) return '中风险'
  return '低风险'
})

const riskType = computed(() => {
  if (riskScore.value >= 80) return 'danger'
  if (riskScore.value >= 60) return 'warning'
  return 'success'
})

function fetchAlertDetail() {
  loading.value = true
  // 模拟获取详情
  setTimeout(() => {
    alertDetail.value = {
      id: props.alertId,
      userName: '张**',
      userPhone: '138****5678',
      userIdCard: '110***********1234',
      detectionTime: '2026-07-14 10:23:45',
      riskScore: 85,
      alertContent: '用户短时间内向多个陌生账户进行大额转账，涉及金额 12.5 万元，疑似遭遇刷单诈骗。',
      aiAnalysis: '通过分析用户行为模式，发现该用户在过去 2 小时内与 5 个可疑号码通话，同时向 3 个不同账户转账。行为模式与刷单诈骗高度吻合，建议立即干预。',
      historyRecords: [
        { time: '2026-07-14 08:12:00', action: '首次检测到异常转账行为', result: '标记为可疑' },
        { time: '2026-07-14 09:30:00', action: 'AI 二次分析', result: '风险等级提升至高风险' },
        { time: '2026-07-14 10:23:45', action: '系统自动预警', result: '已通知网格员' },
      ],
    }
    loading.value = false
  }, 500)
}

function handleMarkProcessed() {
  ElMessage.success('已标记为处理中')
  emit('status-updated', { id: props.alertId, status: 'processing' })
  dialogVisible.value = false
}

function handleExportReport() {
  ElMessage.success('报告导出中，请稍候...')
}
</script>

<template>
  <el-dialog
    v-model="dialogVisible"
    title="预警详情"
    width="720px"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <template v-if="loading">
      <div style="text-align: center; padding: 40px 0">
        <el-icon class="is-loading" :size="32">
          <Loading />
        </el-icon>
        <p style="margin-top: 12px; color: #909399">加载中...</p>
      </div>
    </template>

    <template v-else-if="alertDetail">
      <div class="detail-section">
        <h3 class="section-title">基础信息</h3>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="预警编号">{{ alertDetail.id }}</el-descriptions-item>
          <el-descriptions-item label="用户姓名">{{ alertDetail.userName }}</el-descriptions-item>
          <el-descriptions-item label="联系电话">{{ alertDetail.userPhone }}</el-descriptions-item>
          <el-descriptions-item label="身份证号">{{ alertDetail.userIdCard }}</el-descriptions-item>
          <el-descriptions-item label="检测时间">{{ alertDetail.detectionTime }}</el-descriptions-item>
          <el-descriptions-item label="风险评分">
            <el-tag :type="riskType" effect="dark">
              {{ riskScore }} 分 - {{ riskLevel }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <div class="detail-section">
        <h3 class="section-title">检测内容</h3>
        <el-card shadow="never" class="content-card">
          {{ alertDetail.alertContent }}
        </el-card>
      </div>

      <div class="detail-section">
        <h3 class="section-title">AI 分析结果</h3>
        <el-card shadow="never" class="content-card ai-card">
          <el-icon color="#409EFF" :size="18" style="margin-right: 8px; vertical-align: middle">
            <MagicStick />
          </el-icon>
          {{ alertDetail.aiAnalysis }}
        </el-card>
      </div>

      <div class="detail-section">
        <h3 class="section-title">历史记录</h3>
        <el-timeline>
          <el-timeline-item
            v-for="(record, index) in alertDetail.historyRecords"
            :key="index"
            :timestamp="record.time"
            placement="top"
          >
            <div class="timeline-content">
              <span class="timeline-action">{{ record.action }}</span>
              <el-tag size="small" type="info">{{ record.result }}</el-tag>
            </div>
          </el-timeline-item>
        </el-timeline>
      </div>
    </template>

    <template #footer>
      <el-button @click="dialogVisible = false">关闭</el-button>
      <el-button type="primary" @click="handleMarkProcessed">标记处理</el-button>
      <el-button plain @click="handleExportReport">导出报告</el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.detail-section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
  padding-left: 10px;
  border-left: 3px solid #409EFF;
}

.content-card {
  background: #f5f7fa;
  border: none;
  font-size: 14px;
  line-height: 1.8;
  color: #606266;
}

.ai-card {
  background: #ecf5ff;
}

.timeline-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.timeline-action {
  font-size: 13px;
  color: #606266;
}
</style>