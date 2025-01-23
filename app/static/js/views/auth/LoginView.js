const LoginView = {
  name: 'LoginView',
  setup() {
    const loading = Vue.ref(false)
    const error = Vue.ref('')
    const route = VueRouter.useRoute()
    const router = VueRouter.useRouter()
    const form = Vue.reactive({
      username: '',
      password: ''
    })

    const handleSubmit = async () => {
      try {
        loading.value = true
        error.value = ''

        // 验证表单
        if (!form.username || !form.password) {
          error.value = '请输入用户名和密码'
          return
        }

        // 调用登录接口
        const response = await window.api.auth.login({
          username: form.username,
          password: form.password
        })

        // 获取认证 store
        const authStore = window.stores.auth
        authStore.state.token = response.token
        authStore.state.user = response.user
        authStore.state.isAuthenticated = true

        // 保存令牌
        localStorage.setItem('token', response.token)

        // 登录成功后跳转到原页面或默认页面
        const redirectPath = route.query.redirect || '/admin/calculator'
        router.push(redirectPath)
      } catch (err) {
        console.error('登录失败:', err)
        error.value = err.message || '登录失败，请检查用户名和密码'
      } finally {
        loading.value = false
      }
    }

    return {
      form,
      loading,
      error,
      handleSubmit
    }
  },
  template: `
    <div class="login-page">
      <div class="login-box">
        <div class="login-header">
          <h1>运费计算系统</h1>
        </div>
        <div class="login-body">
          <form @submit.prevent="handleSubmit">
            <div v-if="error" class="alert alert-danger">{{ error }}</div>
            
            <div class="form-group mb-3">
              <label for="username" class="form-label">用户名</label>
              <input
                type="text"
                class="form-control"
                id="username"
                v-model="form.username"
                :disabled="loading"
                required
                autocomplete="username"
              >
            </div>

            <div class="form-group mb-4">
              <label for="password" class="form-label">密码</label>
              <input
                type="password"
                class="form-control"
                id="password"
                v-model="form.password"
                :disabled="loading"
                required
                autocomplete="current-password"
              >
            </div>

            <button
              type="submit"
              class="btn btn-primary w-100"
              :disabled="loading"
            >
              <span v-if="loading" class="spinner-border spinner-border-sm me-1"></span>
              登录
            </button>
          </form>
        </div>
      </div>
    </div>
  `
}

// 导出组件
window.LoginView = LoginView 