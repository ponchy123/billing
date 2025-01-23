// 缓存状态管理模块
const useCacheStore = window.defineStore('cache', {
  state: () => ({
    // 页面缓存配置
    pageCache: {
      // 是否启用页面缓存
      enabled: true,
      // 缓存的页面组件
      include: ['DashboardView', 'ProductList', 'PostalZonesView'],
      // 不缓存的页面组件
      exclude: ['LoginView', 'ProductAdd']
    },
    // 数据缓存配置
    dataCache: {
      // 是否启用数据缓存
      enabled: true,
      // 缓存时间（毫秒）
      expire: 30 * 60 * 1000 // 30分钟
    }
  }),
  actions: {
    setPageCacheEnabled(enabled) {
      this.pageCache.enabled = enabled
    },
    setDataCacheEnabled(enabled) {
      this.dataCache.enabled = enabled
    },
    setDataCacheExpire(expire) {
      this.dataCache.expire = expire
    },
    addCachedPage(componentName) {
      if (!this.pageCache.include.includes(componentName)) {
        this.pageCache.include.push(componentName)
      }
    },
    removeCachedPage(componentName) {
      const index = this.pageCache.include.indexOf(componentName)
      if (index > -1) {
        this.pageCache.include.splice(index, 1)
      }
    },
    // 缓存数据
    cacheData({ key, value, expire }) {
      if (!this.dataCache.enabled) return false
      return window.cache.set(key, value, expire || this.dataCache.expire)
    },
    // 获取缓存数据
    getCachedData(key) {
      if (!this.dataCache.enabled) return null
      return window.cache.get(key)
    },
    // 删除缓存数据
    removeCachedData(key) {
      window.cache.remove(key)
    },
    // 清理所有缓存数据
    clearAllCache() {
      window.cache.clear()
    },
    // 清理过期缓存
    clearExpiredCache() {
      window.cache.clearExpired()
    },
    // 启用/禁用页面缓存
    togglePageCache(enabled) {
      this.setPageCacheEnabled(enabled)
    },
    // 启用/禁用数据缓存
    toggleDataCache(enabled) {
      this.setDataCacheEnabled(enabled)
    },
    // 设置数据缓存时间
    setDataCacheExpire(expire) {
      this.setDataCacheExpire(expire)
    }
  }
})

// 导出 store
window.useCacheStore = useCacheStore 