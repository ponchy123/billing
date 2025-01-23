// FuelRatesView组件
const FuelRatesView = {
  name: 'FuelRatesView',
  setup() {
    const loading = Vue.ref(false)
    const error = Vue.ref('')
    const rates = Vue.ref([])
    const showFormDialog = Vue.ref(false)
    const showDeleteDialog = Vue.ref(false)
    const formData = Vue.ref({
      id: null,
      effective_date: '',
      expiry_date: '',
      rate: 0,
      is_active: true
    })
    const selectedRate = Vue.ref(null)
    const deleteMessage = Vue.ref('')

    const formatNumber = (num) => {
      return Number(parseFloat(num).toFixed(2))
    }

    const formatDate = (date) => {
      return new Date(date).toLocaleDateString('zh-CN')
    }

    const isActive = (rate) => {
      return rate.is_active
    }

    const fetchRates = async () => {
      try {
        loading.value = true
        error.value = ''
        const response = await fetch('/api/fuel-rates')
        if (!response.ok) {
          throw new Error(`获取费率列表失败: ${response.status}`)
        }
        const result = await response.json()
        rates.value = result.fuel_rates || []
      } catch (err) {
        console.error('获取费率列表失败:', err)
        error.value = err.message || '获取费率列表失败'
      } finally {
        loading.value = false
      }
    }

    const showAddRateDialog = () => {
      // 设置默认日期为今天
      const today = new Date()
      const year = today.getFullYear()
      const month = String(today.getMonth() + 1).padStart(2, '0')
      const day = String(today.getDate()).padStart(2, '0')
      
      formData.value = {
        id: null,
        effective_date: `${year}-${month}-${day}`,
        expiry_date: '',
        rate: 0,
        is_active: true
      }
      showFormDialog.value = true
    }

    const editRate = (rate) => {
      // 确保日期格式正确
      const effectiveDate = new Date(rate.effective_date)
      const effectiveYear = effectiveDate.getFullYear()
      const effectiveMonth = String(effectiveDate.getMonth() + 1).padStart(2, '0')
      const effectiveDay = String(effectiveDate.getDate()).padStart(2, '0')
      
      // 处理失效日期
      let expiryDateStr = ''
      if (rate.expiry_date) {
        const expiryDate = new Date(rate.expiry_date)
        const expiryYear = expiryDate.getFullYear()
        const expiryMonth = String(expiryDate.getMonth() + 1).padStart(2, '0')
        const expiryDay = String(expiryDate.getDate()).padStart(2, '0')
        expiryDateStr = `${expiryYear}-${expiryMonth}-${expiryDay}`
      }
      
      formData.value = {
        id: rate.id,
        effective_date: `${effectiveYear}-${effectiveMonth}-${effectiveDay}`,
        expiry_date: expiryDateStr,
        rate: rate.rate,
        is_active: rate.is_active
      }
      showFormDialog.value = true
    }

    const handleSubmit = async () => {
      try {
        loading.value = true;
        error.value = '';

        // 验证表单
        if (!formData.value.effective_date) {
          throw new Error('请选择生效日期');
        }
        if (!formData.value.rate || formData.value.rate < 0) {
          throw new Error('请输入有效的费率');
        }

        // 构造请求数据
        const requestData = {
          effective_date: formData.value.effective_date,
          rate: parseFloat(parseFloat(formData.value.rate).toFixed(2)),
          is_active: formData.value.is_active
        };

        // 如果设置了失效日期，添加到请求数据中
        if (formData.value.expiry_date) {
          requestData.expiry_date = formData.value.expiry_date;
        }

        // 发送请求
        const url = formData.value.id ? `/api/fuel-rates/${formData.value.id}` : '/api/fuel-rates';
        const method = formData.value.id ? 'PUT' : 'POST';
        const response = await fetch(url, {
          method,
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestData)
        });

        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.message || '操作失败');
        }

        // 关闭对话框并刷新数据
        showFormDialog.value = false;
        await fetchRates();
        alert('操作成功');

      } catch (err) {
        console.error('提交失败:', err);
        error.value = err.message || '操作失败';
      } finally {
        loading.value = false;
      }
    }

    const confirmDeleteRate = (rate) => {
      selectedRate.value = rate
      deleteMessage.value = `确定要删除 ${formatDate(rate.effective_date)} 的费率吗？`
      showDeleteDialog.value = true
    }

    const handleDeleteRate = async () => {
      if (!selectedRate.value) return

      try {
        loading.value = true
        error.value = ''
        const response = await fetch(`/api/fuel-rates/${selectedRate.value.id}`, {
          method: 'DELETE'
        })

        if (!response.ok) {
          throw new Error(`删除失败: ${response.status}`)
        }

        await fetchRates()
        showDeleteDialog.value = false
        alert('删除成功')
      } catch (err) {
        console.error('删除失败:', err)
        error.value = err.message || '删除失败'
      } finally {
        loading.value = false
        selectedRate.value = null
      }
    }

    // 组件挂载时获取费率列表
    Vue.onMounted(() => {
      fetchRates()
    })

    return {
      loading,
      error,
      rates,
      showFormDialog,
      showDeleteDialog,
      formData,
      selectedRate,
      deleteMessage,
      formatNumber,
      formatDate,
      isActive,
      showAddRateDialog,
      editRate,
      handleSubmit,
      confirmDeleteRate,
      handleDeleteRate
    }
  },
  template: `
    <div class="fuel-rates-view">
      <!-- 工具栏 -->
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h4 class="mb-0">燃油费率管理</h4>
        <button class="btn btn-primary" @click="showAddRateDialog">
          <i class="bi bi-plus-lg me-1"></i>添加费率
        </button>
      </div>

      <!-- 费率列表 -->
      <div class="card">
        <div class="card-body">
          <div class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th>生效日期</th>
                  <th>失效日期</th>
                  <th>费率(%)</th>
                  <th>状态</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="rate in rates" :key="rate.id">
                  <td>{{ formatDate(rate.effective_date) }}</td>
                  <td>{{ rate.expiry_date ? formatDate(rate.expiry_date) : '-' }}</td>
                  <td>{{ formatNumber(rate.rate) }}%</td>
                  <td>
                    <span
                      class="badge"
                      :class="{
                        'bg-success': isActive(rate),
                        'bg-secondary': !isActive(rate)
                      }"
                    >
                      {{ isActive(rate) ? '生效中' : '已禁用' }}
                    </span>
                  </td>
                  <td>
                    <div class="btn-group">
                      <button
                        class="btn btn-sm btn-outline-primary"
                        @click="editRate(rate)"
                      >
                        <i class="bi bi-pencil me-1"></i>编辑
                      </button>
                      <button
                        class="btn btn-sm btn-outline-danger"
                        @click="confirmDeleteRate(rate)"
                      >
                        <i class="bi bi-trash me-1"></i>删除
                      </button>
                    </div>
                  </td>
                </tr>
                <tr v-if="rates.length === 0">
                  <td colspan="5" class="text-center py-4">
                    <div class="text-muted">暂无数据</div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- 添加/编辑费率对话框 -->
      <confirm-dialog
        v-model:show="showFormDialog"
        :title="formData.id ? '编辑费率' : '添加费率'"
        type="primary"
        :confirm-text="formData.id ? '保存' : '添加'"
        @confirm="handleSubmit"
      >
        <form @submit.prevent="handleSubmit">
          <div class="mb-3">
            <label class="form-label">生效日期</label>
            <input
              type="date"
              class="form-control"
              v-model="formData.effective_date"
              required
            >
          </div>
          <div class="mb-3">
            <label class="form-label">失效日期</label>
            <input
              type="date"
              class="form-control"
              v-model="formData.expiry_date"
            >
          </div>
          <div class="mb-3">
            <label class="form-label">费率(%)</label>
            <input
              type="number"
              class="form-control"
              v-model="formData.rate"
              step="0.01"
              min="0"
              required
            >
          </div>
          <div class="mb-3 form-check">
            <input
              type="checkbox"
              class="form-check-input"
              id="is_active"
              v-model="formData.is_active"
            >
            <label class="form-check-label" for="is_active">启用</label>
          </div>
          <div v-if="error" class="alert alert-danger">{{ error }}</div>
        </form>
      </confirm-dialog>

      <!-- 删除确认对话框 -->
      <confirm-dialog
        v-model:show="showDeleteDialog"
        title="删除费率"
        type="danger"
        :message="deleteMessage"
        @confirm="handleDeleteRate"
      ></confirm-dialog>
    </div>
  `
}

// 导出组件
window.FuelRatesView = FuelRatesView 