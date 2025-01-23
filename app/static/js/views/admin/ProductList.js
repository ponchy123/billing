const ProductList = {
  name: 'ProductList',
  setup() {
    const loading = Vue.ref(false)
    const error = Vue.ref('')
    const products = Vue.ref([])
    const showConfirmDialog = Vue.ref(false)
    const confirmMessage = Vue.ref('')
    const selectedProduct = Vue.ref(null)
    const fileInput = Vue.ref(null)
    const excelData = Vue.ref(null)
    const showExcelData = Vue.ref(false)

    const fetchProducts = async () => {
      try {
        loading.value = true
        error.value = ''
        console.log('开始获取产品列表...')
        
        const response = await fetch('/api/products')
        console.log('产品列表响应:', response)
        
        if (!response.ok) {
          throw new Error(`获取产品列表失败: ${response.status}`)
        }
        
        const result = await response.json()
        console.log('获取到的响应数据:', result)
        
        if (result.success && Array.isArray(result.data)) {
          products.value = result.data
          console.log('产品列表已更新:', products.value)
        } else {
          console.warn('返回的数据格式不正确:', result)
          error.value = result.message || '获取产品列表失败'
          products.value = []
        }
      } catch (err) {
        console.error('获取产品列表失败:', err)
        error.value = err.message || '获取产品列表失败'
        products.value = []
      } finally {
        loading.value = false
      }
    }

    const handleDelete = (product) => {
      selectedProduct.value = product
      confirmMessage.value = `确定要删除产品 "${product.name}" 吗？此操作不可恢复。`
      showConfirmDialog.value = true
    }

    const confirmDelete = async () => {
      if (!selectedProduct.value) return

      try {
        loading.value = true
        error.value = ''
        
        const response = await fetch(`/api/products/${selectedProduct.value.id}`, {
          method: 'DELETE'
        })
        
        if (!response.ok) {
          const result = await response.json()
          throw new Error(result.message || '删除失败')
        }
        
        await fetchProducts()
      } catch (err) {
        console.error('删除产品失败:', err)
        error.value = err.message || '删除产品失败'
        alert(error.value)
      } finally {
        loading.value = false
        selectedProduct.value = null
        showConfirmDialog.value = false
      }
    }

    const handleImportClick = () => {
      fileInput.value.click()
    }

    const handleFileUpload = async (event) => {
      const file = event.target.files[0]
      if (!file) return

      const formData = new FormData()
      formData.append('file', file)

      try {
        loading.value = true
        error.value = ''
        
        const response = await fetch('/api/products/import', {
          method: 'POST',
          body: formData,
          headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'X-Requested-With': Date.now().toString()
          }
        })

        const result = await response.json()
        console.log('服务器返回数据:', result)
        
        if (!response.ok) {
          throw new Error(result.error || '上传失败')
        }

        if (result.data) {
          excelData.value = result.data
          showExcelData.value = true
          console.log('设置预览数据:', excelData.value)
        } else {
          throw new Error('服务器返回的数据格式不正确')
        }
      } catch (err) {
        console.error('上传失败:', err)
        error.value = err.message || '上传失败'
        alert(error.value)
      } finally {
        loading.value = false
        if (event.target) {
          event.target.value = ''
        }
      }
    }

    const importExcelData = async () => {
      try {
        if (!excelData.value) {
          alert('没有可导入的数据')
          return
        }

        loading.value = true
        error.value = ''

        console.log('开始处理导入数据...')
        
        // 发送数据到后端进行处理
        const response = await fetch('/api/products/batch-import', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(excelData.value)
        })

        const result = await response.json()
        console.log('导入结果:', result)
        
        if (!result.success) {
          throw new Error(result.message || '导入失败')
        }

        // 关闭预览窗口
        showExcelData.value = false
        excelData.value = null
        
        // 刷新产品列表
        await fetchProducts()
        
        // 显示成功提示
        Vue.nextTick(() => {
          alert('数据导入成功！')
        })
      } catch (err) {
        console.error('导入失败:', err)
        error.value = err.message || '导入失败'
        alert('导入失败: ' + err.message)
      } finally {
        loading.value = false
      }
    }

    // 组件挂载时获取数据
    Vue.onMounted(() => {
      fetchProducts()
    })

    // 格式化日期时间
    const formatDateTime = (dateStr) => {
      if (!dateStr) return '永久有效'
      const date = new Date(dateStr)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    return {
      loading,
      error,
      products,
      showConfirmDialog,
      confirmMessage,
      handleDelete,
      confirmDelete,
      formatDateTime,
      fileInput,
      handleImportClick,
      handleFileUpload,
      excelData,
      showExcelData,
      importExcelData
    }
  },
  template: `
    <div class="product-list">
      <!-- Excel数据显示对话框 -->
      <div v-if="showExcelData" class="modal" style="display: block; background: rgba(0,0,0,0.5);">
        <div class="modal-dialog modal-xl">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Excel数据预览</h5>
              <button type="button" class="btn-close" @click="showExcelData = false"></button>
            </div>
            <div class="modal-body" style="max-height: 70vh;">
              <div v-if="excelData" style="overflow-x: auto;">
                <pre style="margin: 0; font-family: monospace; white-space: pre; overflow-y: auto; max-height: calc(70vh - 120px);">{{ excelData }}</pre>
              </div>
              <div v-else class="alert alert-info">
                没有数据可以显示
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="showExcelData = false">关闭</button>
              <button type="button" class="btn btn-primary" @click="importExcelData">导入数据</button>
            </div>
          </div>
        </div>
      </div>

      <div class="d-flex justify-content-between align-items-center mb-4">
        <h1 class="mb-0">产品管理</h1>
        <div>
          <input
            type="file"
            ref="fileInput"
            accept=".xlsx,.xls"
            class="d-none"
            @change="handleFileUpload"
          />
          <button class="btn btn-success me-2" @click="handleImportClick">
            <i class="bi bi-file-earmark-excel me-1"></i>导入产品
          </button>
          <router-link to="/admin/products/add" class="btn btn-primary">
            <i class="bi bi-plus-lg me-1"></i>添加产品
          </router-link>
        </div>
      </div>

      <div v-if="error" class="alert alert-danger">{{ error }}</div>

      <div class="card">
        <div class="card-body">
          <div class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th>产品名称</th>
                  <th>启用状态</th>
                  <th>启用时间</th>
                  <th>失效时间</th>
                  <th>创建时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="loading">
                  <td colspan="6" class="text-center py-4">
                    <div class="spinner-border text-primary">
                      <span class="visually-hidden">加载中...</span>
                    </div>
                  </td>
                </tr>
                <tr v-else-if="products.length === 0">
                  <td colspan="6" class="text-center py-4">暂无产品数据</td>
                </tr>
                <tr v-else v-for="product in products" :key="product.id">
                  <td>{{ product.name }}</td>
                  <td>
                    <span :class="['badge', product.status === 'active' ? 'bg-success' : 'bg-secondary']">
                      {{ product.status === 'active' ? '启用' : '禁用' }}
                    </span>
                  </td>
                  <td>{{ formatDateTime(product.start_date) }}</td>
                  <td>{{ formatDateTime(product.end_date) }}</td>
                  <td>{{ formatDateTime(product.created_at) }}</td>
                  <td>
                    <router-link 
                      :to="'/admin/products/edit/' + product.id"
                      class="btn btn-sm btn-outline-primary me-2"
                      title="编辑"
                    >
                      <i class="bi bi-pencil"></i>
                    </router-link>
                    <button 
                      class="btn btn-sm btn-outline-danger"
                      title="删除"
                      @click="handleDelete(product)"
                      :disabled="loading"
                    >
                      <i class="bi bi-trash"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- 确认删除对话框 -->
      <confirm-dialog
        v-model:show="showConfirmDialog"
        title="确认删除"
        :message="confirmMessage"
        confirmText="确定删除"
        cancelText="取消"
        @confirm="confirmDelete"
      />
    </div>
  `
}

// 导出组件
window.ProductList = ProductList 