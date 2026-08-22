<script setup>
import { ref, onMounted } from 'vue'
import { getBlacklist, addBlacklist, updateBlacklist, deleteBlacklist, toggleBlacklistStatus } from '@/api/blacklist'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const queryParams = ref({
  page: 1,
  pageSize: 10,
  keyword: '',
  type: '',
  status: '',
})

const typeOptions = [
  { value: '', label: '全部' },
  { value: 'IP', label: 'IP地址' },
  { value: 'PHONE', label: '电话号码' },
  { value: 'ACCOUNT', label: '账号' },
  { value: 'WECHAT', label: '微信' },
  { value: 'BANK_CARD', label: '银行卡' },
  { value: 'OTHER', label: '其他' },
]

const statusOptions = [
  { value: '', label: '全部' },
  { value: 1, label: '启用' },
  { value: 0, label: '禁用' },
]

// 编辑弹窗
const dialogVisible = ref(false)
const dialogTitle = ref('')
const dialogLoading = ref(false)
const formRef = ref(null)
const formData = ref({
  id: null,
  type: '',
  value: '',
  source: '',
  reason: '',
  status: 1,
})

async function fetchData() {
  loading.value = true
  try {
    const params = { ...queryParams.value }
    Object.keys(params).forEach((k) => {
      if (params[k] === '' || params[k] === undefined) {
        delete params[k]
      }
    })
    const res = await getBlacklist(params)
    const data = res.data || res
    tableData.value = data.records || data.list || []
    total.value = data.total || 0
  } catch (err) {
    ElMessage.error('获取黑名单列表失败')
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
    keyword: '',
    type: '',
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

function handleAdd() {
  dialogTitle.value = '新增黑名单'
  formData.value = {
    id: null,
    type: '',
    value: '',
    source: '',
    reason: '',
    status: 1,
  }
  dialogVisible.value = true
}

function handleEdit(row) {
  dialogTitle.value = '编辑黑名单'
  formData.value = { ...row }
  dialogVisible.value = true
}

function handleDelete(row) {
  ElMessageBox.confirm('确认删除该黑名单记录吗？', '提示', {
    type: 'warning',
    confirmButtonText: '确认',
    cancelButtonText: '取消',
  }).then(async () => {
    try {
      await deleteBlacklist(row.id)
      ElMessage.success('删除成功')
      fetchData()
    } catch (err) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

async function handleToggleStatus(row) {
  const newStatus = row.status === 1 ? 0 : 1
  const label = newStatus === 1 ? '启用' : '禁用'
  try {
    await toggleBlacklistStatus(row.id, newStatus)
    ElMessage.success(`${label}成功`)
    fetchData()
  } catch (err) {
    ElMessage.error(`${label}失败`)
  }
}

function handleSubmit() {
  formRef.value.validate(async (valid) => {
    if (!valid) return
    dialogLoading.value = true
    try {
      if (formData.value.id) {
        await updateBlacklist(formData.value)
        ElMessage.success('更新成功')
      } else {
        await addBlacklist(formData.value)
        ElMessage.success('新增成功')
      }
      dialogVisible.value = false
      fetchData()
    } catch (err) {
      ElMessage.error('操作失败')
    } finally {
      dialogLoading.value = false
    }
  })
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="blacklist-page">
    <div class="page-title">黑名单管理</div>

    <!-- 搜索区域 -->
    <div class="search-section card">
      <el-form :model="queryParams" inline>
        <el-form-item label="关键词">
          <el-input v-model="queryParams.keyword" placeholder="搜索值/来源/原因" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="queryParams.type" placeholder="请选择" clearable style="width: 140px">
            <el-option
              v-for="item in typeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
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
      <div class="table-toolbar">
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新增
        </el-button>
      </div>

      <el-table
        v-loading="loading"
        :data="tableData"
        stripe
        style="width: 100%"
        empty-text="暂无黑名单数据"
      >
        <el-table-column prop="id" label="ID" width="60" align="center" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag size="small">
              {{ typeOptions.find(t => t.value === row.type)?.label || row.type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="value" label="值" min-width="160" show-overflow-tooltip />
        <el-table-column prop="source" label="来源" width="120" />
        <el-table-column prop="reason" label="原因" min-width="160" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">
              {{ row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="operator" label="操作人" width="120" />
        <el-table-column prop="createTime" label="创建时间" min-width="160" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button
              :type="row.status === 1 ? 'warning' : 'success'"
              link
              size="small"
              @click="handleToggleStatus(row)"
            >
              {{ row.status === 1 ? '禁用' : '启用' }}
            </el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">
              删除
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

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        label-width="80px"
        :rules="{
          type: [{ required: true, message: '请选择类型', trigger: 'change' }],
          value: [{ required: true, message: '请输入值', trigger: 'blur' }],
          reason: [{ required: true, message: '请输入原因', trigger: 'blur' }],
        }"
      >
        <el-form-item label="类型" prop="type">
          <el-select v-model="formData.type" placeholder="请选择类型" style="width: 100%">
            <el-option
              v-for="item in typeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
              :disabled="!item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="值" prop="value">
          <el-input v-model="formData.value" placeholder="请输入IP/电话/账号等" />
        </el-form-item>
        <el-form-item label="来源" prop="source">
          <el-input v-model="formData.source" placeholder="数据来源" />
        </el-form-item>
        <el-form-item label="原因" prop="reason">
          <el-input v-model="formData.reason" type="textarea" :rows="3" placeholder="加入黑名单的原因" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="formData.status">
            <el-radio :value="1">启用</el-radio>
            <el-radio :value="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="dialogLoading" @click="handleSubmit">确认</el-button>
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

.table-toolbar {
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding: 16px 20px;
}
</style>