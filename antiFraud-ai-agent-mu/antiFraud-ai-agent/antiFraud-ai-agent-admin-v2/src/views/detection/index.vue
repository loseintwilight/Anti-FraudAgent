<script setup>
import { ref, onMounted } from 'vue'
import { getDetectionList, getDetectionDetail } from '@/api/detection'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const queryParams = ref({
  page: 1,
  pageSize: 10,
  userId: '',
  fraudType: '',
  riskLevel: '',
  startTime: '',
  endTime: '',
})

const riskLevelOptions = [
  { value: '', label: '全部' },
  { value: 'LOW', label: '低风险' },
  { value: 'MEDIUM', label: '中风险' },
  { value: 'HIGH', label: '高风险' },
  { value: 'CRITICAL', label: '极高风险' },
]

const fraudTypeOptions = [
  { value: '', label: '全部' },
  { value: 'TELECOM', label: '电信诈骗' },
  { value: 'NETWORK', label: '网络诈骗' },
  { value: 'SMS', label: '短信诈骗' },
  { value: 'SOCIAL', label: '社交诈骗' },
  { value: 'OTHER', label: '其他' },
]

// 详情弹窗
const detailVisible = ref(false)
const detailData = ref(null)
const detailLoading = ref(false)

async function fetchData() {
  loading.value = true
  try {
    const params = { ...queryParams.value }
    // 清理空值
    Object.keys(params).forEach((k) => {
      if (params[k] === '' || params[k] === undefined) {
        delete params[k]
      }
    })
    const res = await getDetectionList(params)
    const data = res.data || res
    tableData.value = data.records || data.list || []
    total.value = data.total || 0
  } catch (err) {
    ElMessage.error('获取检测记录失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  queryParams.value.page = 1
  fetchData()
}

function handleReset() {
  queryParams.value = {
    page: 1,
    pageSize: 10,
    userId: '',
    fraudType: '',
    riskLevel: '',
    startTime: '',
    endTime: '',
  }
  fetchData()
}

function handleSizeChange(size) {
  queryParams.value.pageSize = size
  fetchData()
}

function handlePageChange(page) {
  queryParams.value.page = page
  fetchData()
}

async function handleViewDetail(row) {
  detailLoading.value = true
  detailVisible.value = true
  try {
    const res = await getDetectionDetail(row.id)
    detailData.value = res.data || res
  } catch (err) {
    ElMessage.error('获取详情失败')
    detailData.value = row
  } finally {
    detailLoading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="detection-page">
    <div class="page-title">检测记录管理</div>

    <!-- 搜索区域 -->
    <div class="search-section card">
      <el-form :model="queryParams" inline>
        <el-form-item label="用户ID">
          <el-input v-model="queryParams.userId" placeholder="请输入用户ID" clearable style="width: 160px" />
        </el-form-item>
        <el-form-item label="诈骗类型">
          <el-select v-model="queryParams.fraudType" placeholder="请选择" clearable style="width: 140px">
            <el-option
              v-for="item in fraudTypeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="风险等级">
          <el-select v-model="queryParams.riskLevel" placeholder="请选择" clearable style="width: 140px">
            <el-option
              v-for="item in riskLevelOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="queryParams.startTime"
            type="date"
            placeholder="开始日期"
            style="width: 140px"
            value-format="YYYY-MM-DD"
          />
          <span style="margin: 0 8px; color: #909399;">至</span>
          <el-date-picker
            v-model="queryParams.endTime"
            type="date"
            placeholder="结束日期"
            style="width: 140px"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 表格区域 -->
    <div class="table-section card" style="margin-top: 16px;">
      <el-table
        v-loading="loading"
        :data="tableData"
        stripe
        style="width: 100%"
        empty-text="暂无检测记录"
      >
        <el-table-column prop="id" label="ID" width="60" align="center" />
        <el-table-column prop="userId" label="用户ID" width="100" />
        <el-table-column prop="inputType" label="输入类型" width="100" />
        <el-table-column prop="fraudType" label="诈骗类型" min-width="120" />
        <el-table-column prop="riskLevel" label="风险等级" width="100">
          <template #default="{ row }">
            <el-tag
              :type="row.riskLevel === 'HIGH' || row.riskLevel === 'CRITICAL' ? 'danger' : row.riskLevel === 'MEDIUM' ? 'warning' : 'success'"
              size="small"
            >
              {{ row.riskLevel }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="score" label="评分" width="80" align="center" />
        <el-table-column prop="createTime" label="检测时间" min-width="160" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleViewDetail(row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:page="queryParams.page"
          :page-size="queryParams.pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- 详情弹窗 -->
    <el-dialog
      v-model="detailVisible"
      title="检测记录详情"
      width="600px"
      :close-on-click-modal="false"
    >
      <div v-loading="detailLoading" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="ID">{{ detailData?.id }}</el-descriptions-item>
          <el-descriptions-item label="用户ID">{{ detailData?.userId }}</el-descriptions-item>
          <el-descriptions-item label="输入类型">{{ detailData?.inputType }}</el-descriptions-item>
          <el-descriptions-item label="诈骗类型">{{ detailData?.fraudType }}</el-descriptions-item>
          <el-descriptions-item label="风险等级">
            <el-tag
              :type="detailData?.riskLevel === 'HIGH' || detailData?.riskLevel === 'CRITICAL' ? 'danger' : detailData?.riskLevel === 'MEDIUM' ? 'warning' : 'success'"
              size="small"
            >
              {{ detailData?.riskLevel }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="评分">{{ detailData?.score }}</el-descriptions-item>
          <el-descriptions-item label="检测时间" :span="2">{{ detailData?.createTime }}</el-descriptions-item>
          <el-descriptions-item label="检测内容" :span="2">
            <div class="detail-text">{{ detailData?.content || detailData?.inputText || '无' }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="检测结果" :span="2">
            <div class="detail-text">{{ detailData?.result || detailData?.description || '无' }}</div>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.search-section {
  padding: 16px 20px;
}

.search-section :deep(.el-form-item) {
  margin-bottom: 0;
  margin-right: 16px;
}

.table-section {
  padding: 0;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding: 16px 20px;
}

.detail-content {
  padding: 0;
}

.detail-text {
  max-height: 200px;
  overflow-y: auto;
  line-height: 1.6;
  font-size: 13px;
  color: #606266;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>