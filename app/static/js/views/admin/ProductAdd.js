const ProductAdd = {
  name: 'ProductAdd',
  setup() {
    const router = VueRouter.useRouter()
    const loading = Vue.ref(false)
    const error = Vue.ref('')
    const form = Vue.reactive({
      name: '',
      is_active: true,
      start_date: '',
      end_date: ''
    })

    const handleSubmit = async () => {
      try {
        loading.value = true
        error.value = ''

        // 验证表单
        if (!form.name) {
          error.value = '请输入产品名称'
          return
        }
        if (!form.start_date) {
          error.value = '请选择启用时间'
          return
        }

        // 准备提交的数据
        const data = {
          name: form.name,
          is_active: form.is_active,
          start_date: form.start_date,
          end_date: form.end_date || null
        }

        // 发送请求
        await window.api.product.create(data)
        
        // 跳转回列表页
        router.push('/admin/products')
      } catch (err) {
        console.error('创建产品失败:', err)
        error.value = err.response?.data?.message || '创建产品失败'
      } finally {
        loading.value = false
      }
    }

    const handleCancel = () => {
      router.push('/admin/products')
    }

    return {
      loading,
      error,
      form,
      handleSubmit,
      handleCancel
    }
  },
  template: `
    <div class="product-add">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h1 class="mb-0">添加产品</h1>
      </div>

      <div class="card">
        <div class="card-body">
          <form @submit.prevent="handleSubmit">
            <div v-if="error" class="alert alert-danger">{{ error }}</div>

            <div class="mb-3">
              <label for="name" class="form-label">产品名称</label>
              <input
                type="text"
                class="form-control"
                id="name"
                v-model="form.name"
                :disabled="loading"
                required
              >
            </div>

            <div class="mb-3">
              <div class="form-check">
                <input
                  type="checkbox"
                  class="form-check-input"
                  id="is_active"
                  v-model="form.is_active"
                  :disabled="loading"
                >
                <label class="form-check-label" for="is_active">启用状态</label>
              </div>
            </div>

            <div class="mb-3">
              <label for="start_date" class="form-label">启用时间</label>
              <input
                type="datetime-local"
                class="form-control"
                id="start_date"
                v-model="form.start_date"
                :disabled="loading"
                required
              >
            </div>

            <div class="mb-3">
              <label for="end_date" class="form-label">失效时间</label>
              <input
                type="datetime-local"
                class="form-control"
                id="end_date"
                v-model="form.end_date"
                :disabled="loading"
                :min="form.start_date"
              >
              <div class="form-text">如果不设置失效时间，则永久有效</div>
            </div>

            <div class="d-flex justify-content-end gap-2">
              <button
                type="button"
                class="btn btn-secondary"
                @click="handleCancel"
                :disabled="loading"
              >
                取消
              </button>
              <button
                type="submit"
                class="btn btn-primary"
                :disabled="loading"
              >
                <span v-if="loading" class="spinner-border spinner-border-sm me-1"></span>
                保存
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  `
}

// 导出组件
window.ProductAdd = ProductAdd 