// 缓存工具
window.cache = {
  // 默认缓存时间（30分钟）
  DEFAULT_CACHE_TIME: 30 * 60 * 1000,

  // 获取缓存
  get(key) {
    const item = localStorage.getItem(key)
    if (!item) return null

    try {
      const data = JSON.parse(item)
      const { value, expire } = data
      
      // 如果没有过期时间，直接返回
      if (!expire) return value
      
      // 如果已过期，删除缓存
      if (expire < Date.now()) {
        this.remove(key)
        return null
      }
      
      return value
    } catch (error) {
      console.error('读取缓存失败:', error)
      return null
    }
  },

  // 设置缓存
  set(key, value, expire = this.DEFAULT_CACHE_TIME) {
    try {
      const data = {
        value,
        expire: expire ? Date.now() + expire : null
      }
      localStorage.setItem(key, JSON.stringify(data))
      return true
    } catch (error) {
      console.error('设置缓存失败:', error)
      return false
    }
  },

  // 删除缓存
  remove(key) {
    localStorage.removeItem(key)
  },

  // 清除所有缓存
  clear() {
    localStorage.clear()
  },

  // 获取所有缓存键
  keys() {
    return Object.keys(localStorage)
  },

  // 获取缓存大小
  size() {
    let size = 0
    for (const key of this.keys()) {
      size += localStorage.getItem(key).length
    }
    return size
  },

  // 检查是否超出存储限制
  checkStorageLimit() {
    try {
      const test = 'test'
      localStorage.setItem(test, test)
      localStorage.removeItem(test)
      return true
    } catch (error) {
      console.error('存储空间不足')
      return false
    }
  },

  // 清理过期缓存
  clearExpired() {
    for (const key of this.keys()) {
      this.get(key) // 获取时会自动清理过期缓存
    }
  }
} 