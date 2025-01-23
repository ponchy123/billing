// 创建 axios 实例
const request = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    // 从认证状态获取令牌
    const token = window.stores.auth.state.token
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response) {
      const { status, data } = error.response
      
      // 处理认证错误
      if (status === 401) {
        window.stores.auth.actions.logout()
        window.router.push('/login')
        return Promise.reject(new Error('认证已过期，请重新登录'))
      }
      
      // 处理权限错误
      if (status === 403) {
        window.router.push('/403')
        return Promise.reject(new Error('没有权限访问此资源'))
      }
      
      // 处理业务错误
      if (data && data.message) {
        return Promise.reject(new Error(data.message))
      }
    }
    
    return Promise.reject(error)
  }
)

// 导出请求实例
window.request = request

// API 模块
window.api = {
  // 认证相关
  auth: {
    // 登录
    login: (credentials) => {
      return request.post('/auth/login', credentials)
    },
    // 获取当前用户信息
    getCurrentUser: () => {
      return request.get('/auth/user')
    },
    // 登出
    logout: () => {
      return request.post('/auth/logout')
    }
  },
  
  // 产品管理
  product: {
    // 获取产品列表
    list: () => {
      return request.get('/products')
    },
    // 创建产品
    create: (data) => {
      return request.post('/products', data)
    },
    // 更新产品
    update: (id, data) => {
      return request.put(`/products/${id}`, data)
    },
    // 删除产品
    delete: (id) => {
      return request.delete(`/products/${id}`)
    },
    // 获取产品详情
    get: (id) => {
      return request.get(`/products/${id}`)
    },
    // 导入产品
    import: (formData) => {
      return request({
        method: 'post',
        url: '/products/import',
        data: formData,
        upload: true,
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
    }
  },

  // 邮编区域管理
  postalZones: {
    // 获取列表
    list: () => {
      return request.get('/postal-zones')
    },
    // 获取详情
    get: (id) => {
      return request.get(`/postal-zones/${id}`)
    },
    // 创建
    create: (data) => {
      return request.post('/postal-zones', data)
    },
    // 更新
    update: (id, data) => {
      return request.put(`/postal-zones/${id}`, data)
    },
    // 删除
    delete: (id) => {
      return request.delete(`/postal-zones/${id}`)
    },
    // 获取收件邮编列表
    listReceiver: () => {
      return request.get('/postal-zones/receiver')
    },
    // 创建收件邮编
    createReceiver: (data) => {
      return request.post('/postal-zones/receiver', data)
    },
    // 更新收件邮编
    updateReceiver: (id, data) => {
      return request.put(`/postal-zones/receiver/${id}`, data)
    },
    // 删除收件邮编
    deleteReceiver: (id) => {
      return request.delete(`/postal-zones/receiver/${id}`)
    },
    // 获取偏远邮编列表
    listRemote: () => {
      return request.get('/postal-zones/remote')
    },
    // 创建偏远邮编
    createRemote: (data) => {
      return request.post('/postal-zones/remote', data)
    },
    // 更新偏远邮编
    updateRemote: (id, data) => {
      return request.put(`/postal-zones/remote/${id}`, data)
    },
    // 删除偏远邮编
    deleteRemote: (id) => {
      return request.delete(`/postal-zones/remote/${id}`)
    }
  }
}