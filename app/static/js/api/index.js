// API接口集合
window.api = {
  // 认证相关接口
  auth: {
    // 登录
    login: (credentials) => {
      return window.request.post('/auth/login', credentials)
    },
    // 登出
    logout: () => {
      return window.request.post('/auth/logout')
    },
    // 获取当前用户信息
    getCurrentUser: () => {
      return window.request.get('/auth/user')
    }
  },

  // 用户相关接口
  users: {
    // 获取用户列表
    list: (params) => {
      return window.request.get('/users', { params })
    },
    // 获取用户详情
    get: (id) => {
      return window.request.get(`/users/${id}`)
    },
    // 创建用户
    create: (data) => {
      return window.request.post('/users', data)
    },
    // 更新用户
    update: (id, data) => {
      return window.request.put(`/users/${id}`, data)
    },
    // 删除用户
    delete: (id) => {
      return window.request.delete(`/users/${id}`)
    }
  },

  // 产品相关接口
  products: {
    // 获取产品列表
    list: (params) => {
      return window.request.get('/products', { params })
    },
    // 获取产品详情
    get: (id) => {
      return window.request.get(`/products/${id}`)
    },
    // 创建产品
    create: (data) => {
      return window.request.post('/products', data)
    },
    // 更新产品
    update: (id, data) => {
      return window.request.put(`/products/${id}`, data)
    },
    // 删除产品
    delete: (id) => {
      return window.request.delete(`/products/${id}`)
    },
    // 导入产品
    import: (file, onProgress) => {
      return window.request.upload('/products/import', file, onProgress)
    }
  },

  // 邮政区域相关接口
  postalZones: {
    // 获取区域列表
    list: (params) => {
      return window.request.get('/postal-zones', { params })
    },
    // 获取区域详情
    get: (id) => {
      return window.request.get(`/postal-zones/${id}`)
    },
    // 创建区域
    create: (data) => {
      return window.request.post('/postal-zones', data)
    },
    // 更新区域
    update: (id, data) => {
      return window.request.put(`/postal-zones/${id}`, data)
    },
    // 删除区域
    delete: (id) => {
      return window.request.delete(`/postal-zones/${id}`)
    },
    // 获取起始邮编列表
    startList: () => {
      return window.request.get('/postal-zones/start')
    },
    // 创建起始邮编
    createStart: (data) => {
      return window.request.post('/postal-zones/start', data)
    },
    // 更新起始邮编
    updateStart: (id, data) => {
      return window.request.put(`/postal-zones/start/${id}`, data)
    },
    // 删除起始邮编
    deleteStart: (id) => {
      return window.request.delete(`/postal-zones/start/${id}`)
    },
    // 导入起始邮编
    importStart: (file, onProgress) => {
      return window.request.upload('/postal-zones/start/import', file, onProgress)
    },
    // 获取目的邮编列表
    receiverList: () => {
      return window.request.get('/postal-zones/receiver')
    },
    // 创建目的邮编
    createReceiver: (data) => {
      return window.request.post('/postal-zones/receiver', data)
    },
    // 更新目的邮编
    updateReceiver: (id, data) => {
      return window.request.put(`/postal-zones/receiver/${id}`, data)
    },
    // 删除目的邮编
    deleteReceiver: (id) => {
      return window.request.delete(`/postal-zones/receiver/${id}`)
    },
    // 导入目的邮编
    importReceiver: (file, onProgress) => {
      return window.request.upload('/postal-zones/receiver/import', file, onProgress)
    }
  },

  // 燃油费率相关接口
  fuelRates: {
    // 获取费率列表
    list: (params) => {
      return window.request.get('/fuel-rates', { params })
    },
    // 获取费率详情
    get: (id) => {
      return window.request.get(`/fuel-rates/${id}`)
    },
    // 创建费率
    create: (data) => {
      return window.request.post('/fuel-rates', data)
    },
    // 更新费率
    update: (id, data) => {
      return window.request.put(`/fuel-rates/${id}`, data)
    },
    // 删除费率
    delete: (id) => {
      return window.request.delete(`/fuel-rates/${id}`)
    }
  },

  // 运费计算器相关接口
  calculator: {
    // 计算运费
    calculate: (data) => {
      return window.request.post('/calculator/calculate', data)
    }
  }
}

// 获取收件邮编详情
window.getReceiverPostalDetails = (id) => {
  return window.request.get(`/postal-zones/receiver/${id}/details`)
} 