const App = {
  name: 'App',
  setup() {
    const loading = Vue.ref(false)
    const error = Vue.ref('')

    // 检查登录状态
    Vue.onMounted(async () => {
      if (window.stores.auth.state.token) {
        try {
          loading.value = true
          await window.stores.auth.actions.fetchCurrentUser()
        } catch (error) {
          console.error('获取用户信息失败:', error)
          window.stores.auth.actions.logout()
          window.router.push('/login')
        } finally {
          loading.value = false
        }
      }
    })

    return {
      loading,
      error,
      auth: window.stores.auth
    }
  },
  template: `
    <div>
      <router-view v-if="!loading"></router-view>
      <div v-else class="loading-container">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">加载中...</span>
        </div>
      </div>
    </div>
  `
}

// 导出组件
window.App = App 