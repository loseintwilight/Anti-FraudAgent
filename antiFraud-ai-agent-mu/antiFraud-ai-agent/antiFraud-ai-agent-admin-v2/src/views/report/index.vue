<script setup>
import { ref, onMounted } from 'vue'
import { getReportList, getReportDetail } from '@/api/report'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const queryParams = ref({
  page: 1,
  pageSize: 10,
  title: '',
  status: '',
})

const statusOptions = [
  { value: '', label: '全部' },
  { value: 'DRAFT', label: '草稿' },
  { value: 'PUBLISHED', label: '已发布' },
  { value: 'ARCHIVED', label: '已归档' },
]

// 详情弹窗
const detailVisible = ref(false)
const detailData = ref(null)
const detailLoading = ref(false)

async function fetchData() {
  loading.value = true
  try {
    const params = { ...queryParams.value }
    Object.keys(params).forEach((k) => {
      if (params[k] === '' || params[k] === undefined) {
        delete params[k]
      }
    })
    const res = await getReportList(params)
    const data = res.data || res
    tableData.value = data.records || data.list || []
    total.value = data.total || 0
  } catch (err) {
    ElMessage.error('获取报告列表失败')
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
    title: '',
    status: '',
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
    const res = await getReportDetail(row.id)
    detailData.value = res.data || res
  } catch (err) {
    ElMessage.error('获取报告详情失败')
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
  <div class="report-page">
    <div class="page-title">报告管理</div>

    <!-- 搜索区域 -->
    <div class="search-section card">
      <el-form :model="queryParams" inline>
        <el-form-item label="报告标题">
          <el-input v-model="queryParams.title" placeholder="请输入报告标题" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="queryParams.status" placeholder="请选择" clearable style="width: 140px">
            <el-option
              v-for="item in statusOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
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
        empty-text="暂无报告"
      >
        <el-table-column prop="id" label="ID" width="60" align="center" />
        <el-table-column prop="title" label="报告标题" min-width="180" show-overflow-tooltip />
        <el-table-column prop="type" label="报告类型" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag
              :type="row.status === 'PUBLISHED' ? 'success' : row.status === 'ARCHIVED' ? 'info' : 'warning'"
              size="small"
            >
              {{ row.status === 'PUBLISHED' ? '已发布' : row.status === 'ARCHIVED' ? '已归档' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="author" label="创建人" width="120" />
        <el-table-column prop="createTime" label="创建时间" min-width="160" />
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
      title="报告详情"
      width="700px"
      :close-on-click-modal="false"
    >
      <div v-loading="detailLoading" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="报告ID">{{ detailData?.id }}</el-descriptions-item>
          <el-descriptions-item label="报告类型">{{ detailData?.type }}</el-descriptions-item>
          <el-descriptions-item label="报告标题" :span="2">{{ detailData?.title }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag
              :type="detailData?.status === 'PUBLISHED' ? 'success' : detailData?.status === 'ARCHIVED' ? 'info' : 'warning'"
              size="small"
            >
              {{ detailData?.status === 'PUBLISHED' ? '已发布' : detailData?.status === 'ARCHIVED' ? '已归档' : '草稿' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建人">{{ detailData?.author }}</el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">{{ detailData?.createTime }}</el-descriptions-item>
          <el-descriptions-item label="报告内容" :span="2">
            <div class="detail-text">{{ detailData?.content || detailData?.summary || '暂无内容' }}</div>
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
  max-height: 300px;
  overflow-y: auto;
  line-height: 1.6;
  font-size: 13px;
  color: #606266;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>