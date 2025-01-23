const DashboardView = {
  name: 'DashboardView',
  setup() {
    const loading = Vue.ref(false)
    const error = Vue.ref('')
    const stats = Vue.ref({
      users: 0,
      products: 0,
      zones: 0,
      rates: 0
    })

    const fetchStats = async () => {
      try {
        loading.value = true
        error.value = ''
        
        // 获取统计数据
        const response = await axios.get('/api/admin/stats')
        console.log('统计数据响应:', response)
        
        // 更新统计数据
        if (response && typeof response === 'object') {
          stats.value = {
            users: response.users || 0,
            products: response.products || 0,
            zones: response.zones || 0,
            rates: response.rates || 0
          }
        } else {
          throw new Error('获取统计数据失败：响应格式不正确')
        }
      } catch (err) {
        console.error('获取统计数据失败:', err)
        error.value = err.response?.data?.message || err.message || '获取统计数据失败'
      } finally {
        loading.value = false
      }
    }

    // 组件挂载时获取数据
    Vue.onMounted(() => {
      fetchStats()
    })

    return {
      loading,
      error,
      stats
    }
  },
  template: `
    <div class="dashboard">
      <h1 class="mb-4">仪表盘</h1>

      <div v-if="error" class="alert alert-danger">{{ error }}</div>

      <div class="row g-4">
        <div class="col-md-3">
          <div class="card">
            <div class="card-body">
              <h5 class="card-title">
                <i class="bi bi-people me-2"></i>用户数量
              </h5>
              <p class="card-text display-6">
                <span v-if="loading" class="spinner-border"></span>
                <span v-else>{{ stats.users }}</span>
              </p>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="card">
            <div class="card-body">
              <h5 class="card-title">
                <i class="bi bi-box me-2"></i>产品数量
              </h5>
              <p class="card-text display-6">
                <span v-if="loading" class="spinner-border"></span>
                <span v-else>{{ stats.products }}</span>
              </p>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="card">
            <div class="card-body">
              <h5 class="card-title">
                <i class="bi bi-geo me-2"></i>邮编区域
              </h5>
              <p class="card-text display-6">
                <span v-if="loading" class="spinner-border"></span>
                <span v-else>{{ stats.zones }}</span>
              </p>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="card">
            <div class="card-body">
              <h5 class="card-title">
                <i class="bi bi-fuel-pump me-2"></i>费率数量
              </h5>
              <p class="card-text display-6">
                <span v-if="loading" class="spinner-border"></span>
                <span v-else>{{ stats.rates }}</span>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  `
}

// 导出组件
window.DashboardView = DashboardView 