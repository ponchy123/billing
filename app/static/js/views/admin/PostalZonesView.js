// PostalZonesView组件
const PostalZonesView = {
  name: 'PostalZonesView',
  setup() {
    // 基础配置
    const baseURL = 'http://127.0.0.1:5000'
    
    // 响应式数据
    const loading = Vue.ref(false)
    const error = Vue.ref('')
    const receiverPostals = Vue.ref([])
    const remotePostals = Vue.ref([])
    const confirmMessage = Vue.ref('')
    const selectedPostal = Vue.ref(null)
    const deleteType = Vue.ref('')
    const showConfirmDialog = Vue.ref(false)
    const editingPostalDetails = Vue.ref({
      type: 'receiver',
      data: []
    })
    const importForm = Vue.reactive({
      start_code: '',
      file: null
    })
    const remoteImportForm = Vue.reactive({
      start_code: '',
      file: null
    })

    // 创建 axios 实例
    const http = axios.create({
      baseURL,
      timeout: 10000,
      headers: {
        'Accept': 'application/json'
      }
    })

    // 添加请求拦截器
    http.interceptors.request.use(config => {
      console.log('发送请求:', {
        url: config.url,
        method: config.method,
        headers: config.headers
      })
      return config
    })

    // 添加响应拦截器
    http.interceptors.response.use(
      response => {
        console.log('收到响应:', {
          url: response.config.url,
          status: response.status,
          data: response.data
        })
        return response
      },
      error => {
        console.error('请求错误:', {
          url: error.config?.url,
          message: error.message,
          response: error.response?.data,
          status: error.response?.status
        })
        return Promise.reject(error)
      }
    )

    const fetchPostals = async () => {
      try {
        loading.value = true
        console.log('开始获取邮编数据...')
        
        // 获取收件邮编数据
        try {
          console.log('请求收件邮编数据...')
          const receiverResponse = await http.get('/api/postal-zones/receiver')
          console.log('收件邮编原始响应:', receiverResponse)
          
          if (receiverResponse?.data?.success) {
            receiverPostals.value = receiverResponse.data.data || []
            console.log('设置收件邮编数据:', receiverPostals.value)
          } else {
            console.warn('收件邮编响应异常:', receiverResponse?.data)
            receiverPostals.value = []
          }
        } catch (err) {
          console.error('获取收件邮编失败:', err)
          receiverPostals.value = []
        }

        // 获取偏远邮编数据
        try {
          console.log('请求偏远邮编数据...')
          const remoteResponse = await http.get('/api/postal-zones/remote')
          console.log('偏远邮编原始响应:', remoteResponse)
          
          if (remoteResponse?.data?.success) {
            remotePostals.value = remoteResponse.data.data || []
            console.log('设置偏远邮编数据:', remotePostals.value)
          } else {
            console.warn('偏远邮编响应异常:', remoteResponse?.data)
            remotePostals.value = []
          }
        } catch (err) {
          console.error('获取偏远邮编失败:', err)
          remotePostals.value = []
        }

      } catch (err) {
        console.error('获取数据失败:', err)
        error.value = '获取数据失败，请检查网络连接'
      } finally {
        loading.value = false
        console.log('数据获取完成，状态:', {
          receiverPostals: receiverPostals.value,
          remotePostals: remotePostals.value,
          error: error.value
        })
      }
    }

    const handleFileSelect = (event) => {
      const file = event.target.files[0]
      if (file) {
        console.log('选择文件:', file.name)
        importForm.file = file
      }
    }

    const resetImportForm = () => {
      importForm.start_code = ''
      importForm.file = null
    }

    const handleImport = async () => {
      try {
        // 检查表单
        if (!importForm.start_code || !importForm.file) {
          alert('请填写起始邮编并选择文件')
          return
        }

        // 验证起始邮编格式
        if (!/^\d{5}$/.test(importForm.start_code)) {
          alert('起始邮编必须是5位数字')
          return
        }

        // 验证文件格式
        if (!importForm.file.name.match(/\.(xlsx|xls)$/i)) {
          alert('请选择正确的Excel文件格式(.xlsx或.xls)')
          return
        }

        loading.value = true

        // 构建表单数据
        const formData = new FormData()
        formData.append('file', importForm.file)
        formData.append('start_code', importForm.start_code)

        // 发送请求
        await http.post('/api/postal-zones/receiver/import', formData)
        
        // 导入成功
        alert('导入成功')
        
        // 关闭模态框
        const modalElement = document.getElementById('importModal')
        const modal = bootstrap.Modal.getInstance(modalElement)
        modal?.hide()
        
        // 重置表单
        resetImportForm()
        
        // 刷新数据
        await fetchPostals()
        
      } catch (error) {
        console.error('导入错误:', error)
        alert('导入失败，请检查文件格式')
      } finally {
        loading.value = false
      }
    }

    const editPostal = async (postal, type = 'receiver') => {
      try {
        console.log('开始获取详情:', { postal, type })
        const endpoint = type === 'receiver' ? 'receiver' : 'remote'
        const url = `/api/postal-zones/${endpoint}/${postal.id}/details`
        console.log('请求URL:', url)
        
        const response = await http.get(url)
        console.log('获取详情响应:', response)
        
        if (response.data && response.data.success) {
          console.log('设置详情数据:', response.data.data)
          editingPostalDetails.value = {
            type,
            data: response.data.data || []
          }
          const modalElement = document.getElementById('editModal')
          if (modalElement) {
            const modal = new bootstrap.Modal(modalElement)
            modal.show()
          }
        } else {
          console.warn('响应数据异常:', response.data)
          throw new Error(response.data?.message || '获取详情失败')
        }
      } catch (error) {
        console.error('获取邮编详情失败:', error)
        console.error('错误详情:', {
          message: error.message,
          response: error.response?.data,
          status: error.response?.status
        })
        alert(error.response?.data?.message || error.message || '获取邮编详情失败')
      }
    }

    const confirmDelete = (postal, type) => {
      selectedPostal.value = postal
      deleteType.value = type
      confirmMessage.value = `确定要删除${type === 'receiver' ? '收件' : '偏远'}邮编 "${postal.start_code}" 吗？此操作不可恢复。`
      showConfirmDialog.value = true
    }

    const showImportModal = () => {
      const modalElement = document.getElementById('importModal')
      if (modalElement) {
        const modal = new bootstrap.Modal(modalElement)
        modal.show()
      }
    }

    const handleRemoteFileSelect = (event) => {
      const file = event.target.files[0]
      if (file) {
        console.log('选择偏远邮编文件:', file.name)
        remoteImportForm.file = file
      }
    }

    const resetRemoteImportForm = () => {
      remoteImportForm.start_code = ''
      remoteImportForm.file = null
    }

    const handleRemoteImport = async () => {
      try {
        // 检查表单
        if (!remoteImportForm.start_code || !remoteImportForm.file) {
          alert('请填写起始邮编并选择文件')
          return
        }

        // 验证起始邮编格式
        if (!/^\d{5}$/.test(remoteImportForm.start_code)) {
          alert('起始邮编必须是5位数字')
          return
        }

        // 验证文件格式
        if (!remoteImportForm.file.name.match(/\.(xlsx|xls)$/i)) {
          alert('请选择正确的Excel文件格式(.xlsx或.xls)')
          return
        }

        loading.value = true

        // 构建表单数据
        const formData = new FormData()
        formData.append('file', remoteImportForm.file)
        formData.append('start_code', remoteImportForm.start_code)

        // 发送请求
        await http.post('/api/postal-zones/remote/import', formData)
        
        // 导入成功
        alert('导入成功')
        
        // 关闭模态框
        const modalElement = document.getElementById('remoteImportModal')
        const modal = bootstrap.Modal.getInstance(modalElement)
        modal?.hide()
        
        // 重置表单
        resetRemoteImportForm()
        
        // 刷新数据
        await fetchPostals()
        
      } catch (error) {
        console.error('导入错误:', error)
        alert('导入失败，请检查文件格式')
      } finally {
        loading.value = false
      }
    }

    const showRemoteImportModal = () => {
      const modalElement = document.getElementById('remoteImportModal')
      if (modalElement) {
        const modal = new bootstrap.Modal(modalElement)
        modal.show()
      }
    }

    // 在组件挂载时获取数据
    Vue.onMounted(() => {
      console.log('组件挂载，开始获取数据...')
      fetchPostals()
    })

    return {
      loading,
      error,
      receiverPostals,
      remotePostals,
      confirmMessage,
      selectedPostal,
      deleteType,
      showConfirmDialog,
      editingPostalDetails,
      importForm,
      handleFileSelect,
      handleImport,
      resetImportForm,
      editPostal,
      confirmDelete,
      handleDelete: async () => {
        if (!selectedPostal.value || !deleteType.value) return
        
        try {
          loading.value = true
          await http.delete(`/api/postal-zones/${deleteType.value}/${selectedPostal.value.id}`)
          await fetchPostals()
          showConfirmDialog.value = false
        } catch (err) {
          console.error('删除失败:', err)
          error.value = err.response?.data?.message || err.message || '删除失败'
        } finally {
          loading.value = false
          selectedPostal.value = null
          deleteType.value = ''
        }
      },
      showImportModal,
      remoteImportForm,
      handleRemoteFileSelect,
      handleRemoteImport,
      resetRemoteImportForm,
      showRemoteImportModal
    }
  },
  template: `
    <div class="postal-zones-view">
      <div class="container-fluid">
        <div class="row">
          <!-- 收件邮编表 -->
          <div class="col-12 col-lg-6 mb-4">
            <div class="card">
              <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">收件邮编表</h5>
                <div class="d-flex gap-2">
                  <button class="btn btn-success btn-sm" @click="showImportModal">
                    <i class="bi bi-file-earmark-excel"></i> 导入收件邮编分区表
                  </button>
                </div>
              </div>
              <div class="card-body">
                <div v-if="error" class="alert alert-danger">{{ error }}</div>
                <div class="table-responsive">
                  <table class="table table-striped">
                    <thead>
                      <tr>
                        <th>起始邮编</th>
                        <th>区域名称</th>
                        <th>文件名</th>
                        <th>操作</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-if="loading">
                        <td colspan="4" class="text-center">
                          <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">加载中...</span>
                          </div>
                        </td>
                      </tr>
                      <template v-else>
                        <tr v-for="postal in receiverPostals" :key="postal.id || postal.start_code">
                          <td>{{ postal.start_code }}</td>
                          <td>{{ postal.zone_name || '-' }}</td>
                          <td>{{ postal.file_name || '-' }}</td>
                          <td>
                            <button class="btn btn-sm btn-info me-2" @click="editPostal(postal)">
                              <i class="bi bi-pencil"></i> 编辑
                            </button>
                            <button class="btn btn-sm btn-danger" @click="confirmDelete(postal, 'receiver')">
                              <i class="bi bi-trash"></i> 删除
                            </button>
                          </td>
                        </tr>
                        <tr v-if="!receiverPostals.length">
                          <td colspan="4" class="text-center">暂无数据</td>
                        </tr>
                      </template>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>

          <!-- 偏远邮编表 -->
          <div class="col-12 col-lg-6 mb-4">
            <div class="card">
              <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">偏远邮编表</h5>
                <div class="d-flex gap-2">
                  <button class="btn btn-success btn-sm" @click="showRemoteImportModal">
                    <i class="bi bi-file-earmark-excel"></i> 导入偏远邮编分区表
                  </button>
                </div>
              </div>
              <div class="card-body">
                <div class="table-responsive">
                  <table class="table table-striped">
                    <thead>
                      <tr>
                        <th>起始邮编</th>
                        <th>区域名称</th>
                        <th>文件名</th>
                        <th>操作</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-if="loading">
                        <td colspan="4" class="text-center">
                          <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">加载中...</span>
                          </div>
                        </td>
                      </tr>
                      <template v-else>
                        <tr v-for="postal in remotePostals" :key="postal.id || postal.start_code">
                          <td>{{ postal.start_code }}</td>
                          <td>{{ postal.zone_name || '-' }}</td>
                          <td>{{ postal.file_name || '-' }}</td>
                          <td>
                            <button class="btn btn-sm btn-info me-2" @click="editPostal(postal, 'remote')">
                              <i class="bi bi-pencil"></i> 编辑
                            </button>
                            <button class="btn btn-sm btn-danger" @click="confirmDelete(postal, 'remote')">
                              <i class="bi bi-trash"></i> 删除
                            </button>
                          </td>
                        </tr>
                        <tr v-if="!remotePostals.length">
                          <td colspan="4" class="text-center">暂无数据</td>
                        </tr>
                      </template>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 导入对话框 -->
      <div class="modal fade" id="importModal" tabindex="-1" aria-labelledby="importModalLabel" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="importModalLabel">导入收件邮编分区表</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <form @submit.prevent="handleImport">
                <div class="mb-3">
                  <label class="form-label">起始邮编</label>
                  <input type="text" 
                         class="form-control" 
                         v-model="importForm.start_code" 
                         maxlength="5" 
                         pattern="\\d{5}"
                         required
                         placeholder="请输入5位数字邮编">
                </div>
                <div class="mb-3">
                  <label class="form-label">Excel文件</label>
                  <input type="file" 
                         class="form-control" 
                         accept=".xlsx,.xls" 
                         @change="handleFileSelect"
                         required>
                </div>
              </form>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
              <button type="button" 
                      class="btn btn-primary" 
                      @click="handleImport" 
                      :disabled="loading || !importForm.start_code || !importForm.file">
                {{ loading ? '导入中...' : '导入' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 确认删除对话框 -->
      <div class="modal" :class="{ show: showConfirmDialog }" tabindex="-1" :style="{ display: showConfirmDialog ? 'block' : 'none' }">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">确认删除</h5>
              <button type="button" class="btn-close" @click="showConfirmDialog = false"></button>
            </div>
            <div class="modal-body">
              {{ confirmMessage }}
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="showConfirmDialog = false">取消</button>
              <button type="button" class="btn btn-danger" @click="handleDelete" :disabled="loading">
                {{ loading ? '删除中...' : '删除' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 编辑详情对话框 -->
      <div class="modal" id="editModal" tabindex="-1" aria-labelledby="editModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="editModalLabel">邮编详情</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <div class="table-responsive">
                <table class="table table-striped">
                  <thead>
                    <tr v-if="editingPostalDetails.type === 'receiver'">
                      <th>序号</th>
                      <th>Destination ZIP</th>
                      <th>Zone</th>
                    </tr>
                    <tr v-else>
                      <th>序号</th>
                      <th>Destination ZIP Codes</th>
                      <th>Destination ZIP Codes</th>
                      <th>Destination ZIP Codes</th>
                      <th>Destination ZIP Codes</th>
                      <th>Destination ZIP codes</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="loading">
                      <td :colspan="editingPostalDetails.type === 'receiver' ? 3 : 6" class="text-center">
                        <div class="spinner-border text-primary" role="status">
                          <span class="visually-hidden">加载中...</span>
                        </div>
                      </td>
                    </tr>
                    <template v-else>
                      <template v-if="editingPostalDetails.type === 'receiver'">
                        <tr v-for="(item, index) in editingPostalDetails.data" :key="index">
                          <td>{{ index + 1 }}</td>
                          <td>{{ item['Destination ZIP'] }}</td>
                          <td>{{ item['Zone'] }}</td>
                        </tr>
                        <tr v-if="!editingPostalDetails.data.length">
                          <td colspan="3" class="text-center">暂无数据</td>
                        </tr>
                      </template>
                      <template v-else>
                        <tr v-for="(item, index) in editingPostalDetails.data" :key="index">
                          <td>{{ index + 1 }}</td>
                          <td>{{ item['DAS'] }}</td>
                          <td>{{ item['DAS_EXT'] }}</td>
                          <td>{{ item['DAS_Remote'] }}</td>
                          <td>{{ item['DAS_Alaska'] }}</td>
                          <td>{{ item['DAS_Hawaii'] }}</td>
                        </tr>
                        <tr v-if="!editingPostalDetails.data.length">
                          <td colspan="6" class="text-center">暂无数据</td>
                        </tr>
                      </template>
                    </template>
                  </tbody>
                </table>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 偏远邮编导入对话框 -->
      <div class="modal fade" id="remoteImportModal" tabindex="-1" aria-labelledby="remoteImportModalLabel" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="remoteImportModalLabel">导入偏远邮编分区表</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <form @submit.prevent="handleRemoteImport">
                <div class="mb-3">
                  <label class="form-label">起始邮编</label>
                  <input type="text" 
                         class="form-control" 
                         v-model="remoteImportForm.start_code" 
                         maxlength="5" 
                         pattern="\\d{5}"
                         required
                         placeholder="请输入5位数字邮编">
                </div>
                <div class="mb-3">
                  <label class="form-label">Excel文件</label>
                  <input type="file" 
                         class="form-control" 
                         accept=".xlsx,.xls" 
                         @change="handleRemoteFileSelect"
                         required>
                  <div class="form-text">
                    请上传包含 DAS、DAS_EXT、DAS_Remote、DAS_Alaska、DAS_Hawaii 列的 Excel 文件
                  </div>
                </div>
              </form>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
              <button type="button" 
                      class="btn btn-primary" 
                      @click="handleRemoteImport" 
                      :disabled="loading || !remoteImportForm.start_code || !remoteImportForm.file">
                {{ loading ? '导入中...' : '导入' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `
}

// 导出组件
window.PostalZonesView = PostalZonesView