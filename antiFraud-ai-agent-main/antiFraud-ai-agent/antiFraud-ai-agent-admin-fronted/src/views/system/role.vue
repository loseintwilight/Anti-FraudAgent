<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const queryParams = ref({
  page: 1,
  pageSize: 10,
  roleName: '',
  status: '',
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
    const res = await request.get('/system/role/list', { params })
    const data = res.data || res
    tableData.value = data.records || data.list || []
    total.value = data.total || 0
  } catch (err) {
    ElMessage.error('获取角色列表失败')
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
    roleName: '',
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

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="role-page">
    <div class="page-title">角色管理</div>

    <div class="search-section card">
      <el-form :model="queryParams" inline>
        <el-form-item label="角色名称">
          <el-input v-model="queryParams.roleName" placeholder="请输入角色名称" clearable style="width: 160px" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="queryParams.status" placeholder="请选择" clearable style="width: 140px">
            <el-option label="全部" value="" />
            <el-option label="正常" value="1" />
            <el-option label="停用" value="0" />
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

    <div class="table-section card" style="margin-top: 16px;">
      <el-table
        v-loading="loading"
        :data="tableData"
        stripe
        style="width: 100%"
        empty-text="暂无角色数据"
      >
        <el-table-column prop="id" label="ID" width="60" align="center" />
        <el-table-column prop="roleName" label="角色名称" min-width="140" />
        <el-table-column prop="roleKey" label="角色标识" width="140" />
        <el-table-column prop="roleSort" label="排序" width="70" align="center" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 || row.status === '1' ? 'success' : 'danger'" size="small">
              {{ row.status === 1 || row.status === '1' ? '正常' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" min-width="160" />
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
</style>