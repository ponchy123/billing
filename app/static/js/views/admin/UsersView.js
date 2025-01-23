const UsersView = {
  name: 'UsersView',
  setup() {
    const users = Vue.ref([])
    const loading = Vue.ref(false)
    const error = Vue.ref('')
    const router = VueRouter.useRouter()

    const fetchUsers = async () => {
      try {
        loading.value = true
        error.value = ''
        const response = await axios.get('/api/admin/users')
        if (response.data.success) {
          users.value = response.data.data || []
        } else {
          error.value = response.data.message || '获取用户列表失败'
          users.value = []
        }
      } catch (err) {
        error.value = err.response?.data?.message || '获取用户列表失败'
        console.error('获取用户列表失败:', err)
        users.value = []
      } finally {
        loading.value = false
      }
    }

    const handleEdit = (user) => {
      router.push(`/admin/users/${user.id}/edit`)
    }

    const handleDelete = async (user) => {
      if (!confirm(`确定要删除用户 "${user.username}" 吗？`)) {
        return
      }
      
      try {
        loading.value = true
        const response = await axios.delete(`/api/admin/users/${user.id}`)
        if (response.data.success) {
          await fetchUsers()
        } else {
          error.value = response.data.message || '删除用户失败'
        }
      } catch (err) {
        error.value = err.response?.data?.message || '删除用户失败'
        console.error('删除用户失败:', err)
      } finally {
        loading.value = false
      }
    }

    const handleAdd = () => {
      router.push('/admin/users/add')
    }

    Vue.onMounted(() => {
      fetchUsers()
    })

    return {
      users,
      loading,
      error,
      handleEdit,
      handleDelete,
      handleAdd
    }
  },
  template: `
    <div class="users-view">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h1 class="mb-0">用户管理</h1>
        <button class="btn btn-primary" @click="handleAdd">
          <i class="bi bi-plus-lg me-1"></i>添加用户
        </button>
      </div>
      
      <div v-if="error" class="alert alert-danger">{{ error }}</div>
      
      <div class="card">
        <div class="card-body">
          <div class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>用户名</th>
                  <th>邮箱</th>
                  <th>角色</th>
                  <th>状态</th>
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
                <tr v-else-if="users.length === 0">
                  <td colspan="6" class="text-center py-4">暂无用户数据</td>
                </tr>
                <tr v-else v-for="user in users" :key="user.id">
                  <td>{{ user.id }}</td>
                  <td>{{ user.username }}</td>
                  <td>{{ user.email }}</td>
                  <td>{{ user.role }}</td>
                  <td>
                    <span :class="['badge', user.active ? 'bg-success' : 'bg-danger']">
                      {{ user.active ? '活跃' : '禁用' }}
                    </span>
                  </td>
                  <td>
                    <button 
                      class="btn btn-sm btn-outline-primary me-2" 
                      title="编辑"
                      @click="handleEdit(user)"
                      :disabled="loading"
                    >
                      <i class="bi bi-pencil"></i>
                    </button>
                    <button 
                      class="btn btn-sm btn-outline-danger" 
                      title="删除"
                      @click="handleDelete(user)"
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
    </div>
  `
}

// 导出组件
window.UsersView = UsersView 