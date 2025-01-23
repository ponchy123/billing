// 定义组件
const UserEdit = {
  name: 'UserEdit',
  setup() {
    const router = VueRouter.useRouter()
    const route = VueRouter.useRoute()
    const loading = Vue.ref(false)
    const error = Vue.ref('')
    const user = Vue.ref({
      username: '',
      email: '',
      password: '',
      is_active: true,
      role: 'user'
    })

    const isEdit = Vue.computed(() => route.name === 'user-edit')
    const title = Vue.computed(() => isEdit.value ? '编辑用户' : '添加用户')

    const fetchUser = async (id) => {
      try {
        loading.value = true
        error.value = ''
        const response = await axios.get(`/api/admin/users/${id}`)
        user.value = {
          ...response.data,
          password: '' // 清空密码字段
        }
      } catch (err) {
        error.value = err.response?.data?.message || '获取用户信息失败'
        console.error('获取用户信息失败:', err)
        router.push('/admin/users')
      } finally {
        loading.value = false
      }
    }

    const handleSubmit = async () => {
      try {
        // 表单验证
        if (!user.value.username || !user.value.email || (!isEdit.value && !user.value.password)) {
          error.value = '请填写必填字段'
          return
        }

        loading.value = true
        error.value = ''
        
        // 构造提交的数据
        const submitData = {
          ...user.value
        }
        
        // 如果是编辑模式且密码为空，则不提交密码字段
        if (isEdit.value && !submitData.password) {
          delete submitData.password
        }
        
        if (isEdit.value) {
          await axios.put(`/api/admin/users/${route.params.id}`, submitData)
        } else {
          await axios.post('/api/admin/users', submitData)
        }
        
        router.push('/admin/users')
      } catch (err) {
        error.value = err.response?.data?.message || '保存用户失败'
        console.error('保存用户失败:', err)
      } finally {
        loading.value = false
      }
    }

    const handleBack = () => {
      router.push('/admin/users')
    }

    // 组件挂载时获取数据
    Vue.onMounted(() => {
      if (route.params.id) {
        fetchUser(route.params.id)
      }
    })

    return {
      user,
      loading,
      error,
      isEdit,
      title,
      handleSubmit,
      handleBack
    }
  },
  template: `
    <div class="container-fluid py-3">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="mb-0">{{ title }}</h2>
        <button class="btn btn-secondary" @click="handleBack">
          <i class="bi bi-arrow-left me-1"></i>返回
        </button>
      </div>
      
      <div class="card">
        <div class="card-body">
          <div v-if="error" class="alert alert-danger">
            {{ error }}
          </div>
          
          <form @submit.prevent="handleSubmit" class="needs-validation" novalidate>
            <div class="mb-3">
              <label for="username" class="form-label required">用户名</label>
              <input 
                type="text" 
                class="form-control" 
                id="username" 
                v-model="user.username"
                required
                :disabled="loading"
                placeholder="请输入用户名"
              >
            </div>
            
            <div class="mb-3">
              <label for="email" class="form-label required">邮箱</label>
              <input 
                type="email" 
                class="form-control" 
                id="email" 
                v-model="user.email"
                required
                :disabled="loading"
                placeholder="请输入邮箱地址"
              >
            </div>
            
            <div class="mb-3">
              <label for="password" class="form-label" :class="{ required: !isEdit }">
                密码
                <span v-if="isEdit" class="text-muted">(留空表示不修改)</span>
              </label>
              <input 
                type="password" 
                class="form-control" 
                id="password" 
                v-model="user.password"
                :required="!isEdit"
                :disabled="loading"
                placeholder="请输入密码"
              >
            </div>
            
            <div class="mb-3">
              <label for="role" class="form-label">角色</label>
              <select 
                class="form-select" 
                id="role" 
                v-model="user.role"
                :disabled="loading"
              >
                <option value="user">普通用户</option>
                <option value="admin">管理员</option>
              </select>
            </div>
            
            <div class="mb-4">
              <div class="form-check">
                <input 
                  type="checkbox" 
                  class="form-check-input" 
                  id="is_active" 
                  v-model="user.is_active"
                  :disabled="loading"
                >
                <label class="form-check-label" for="is_active">启用账号</label>
              </div>
            </div>
            
            <div class="d-flex gap-2">
              <button type="submit" class="btn btn-primary" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-1"></span>
                {{ isEdit ? '保存修改' : '创建用户' }}
              </button>
              <button type="button" class="btn btn-secondary" @click="handleBack" :disabled="loading">取消</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  `
}

// 导出组件
if (window.Vue) {
  window.UserEdit = UserEdit
} else {
  console.error('Vue is not loaded')
} 