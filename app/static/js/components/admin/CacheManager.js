// 缓存管理组件
window.CacheManager = {
  template: `
    <div class="cache-manager">
      <div class="card">
        <div class="card-body">
          <h5 class="card-title">缓存管理</h5>
          
          <!-- 页面缓存配置 -->
          <div class="mb-4">
            <h6>页面缓存</h6>
            <div class="form-check form-switch mb-2">
              <input class="form-check-input" type="checkbox" 
                     v-model="pageCacheEnabled"
                     @change="togglePageCache">
              <label class="form-check-label">启用页面缓存</label>
            </div>
            <div v-if="pageCacheEnabled">
              <div class="small text-muted mb-2">已缓存的页面：</div>
              <div class="d-flex flex-wrap gap-2">
                <span v-for="page in cachedPages" :key="page" 
                      class="badge bg-primary">
                  {{ page }}
                  <button type="button" class="btn-close btn-close-white ms-2"
                          @click="removeCachedPage(page)">
                  </button>
                </span>
              </div>
            </div>
          </div>

          <!-- 数据缓存配置 -->
          <div class="mb-4">
            <h6>数据缓存</h6>
            <div class="form-check form-switch mb-2">
              <input class="form-check-input" type="checkbox" 
                     v-model="dataCacheEnabled"
                     @change="toggleDataCache">
              <label class="form-check-label">启用数据缓存</label>
            </div>
            <div v-if="dataCacheEnabled" class="mb-3">
              <label class="form-label">缓存时间（分钟）</label>
              <input type="number" class="form-control" 
                     v-model.number="cacheExpireMinutes"
                     @change="updateCacheExpire"
                     min="1">
            </div>
            <div class="d-flex gap-2">
              <button class="btn btn-warning" @click="clearExpiredCache">
                清理过期缓存
              </button>
              <button class="btn btn-danger" @click="confirmClearAllCache">
                清理所有缓存
              </button>
            </div>
          </div>

          <!-- 缓存统计 -->
          <div>
            <h6>缓存统计</h6>
            <div class="small text-muted">
              <div>缓存大小：{{ formatSize(cacheSize) }}</div>
              <div>缓存项数：{{ cacheKeys.length }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 确认对话框 -->
      <confirm-dialog
        ref="confirmDialog"
        title="确认清理"
        content="确定要清理所有缓存吗？此操作不可恢复。"
        @confirm="clearAllCache"
      />
    </div>
  `,

  data() {
    return {
      pageCacheEnabled: this.$store.getters['cache/isPageCacheEnabled'],
      dataCacheEnabled: this.$store.getters['cache/isDataCacheEnabled'],
      cacheExpireMinutes: this.$store.getters['cache/dataCacheExpire'] / 60000,
      cacheSize: 0,
      cacheKeys: []
    }
  },

  computed: {
    cachedPages() {
      return this.$store.state.cache.pageCache.include
    }
  },

  methods: {
    togglePageCache(event) {
      this.$store.dispatch('cache/togglePageCache', event.target.checked)
    },

    toggleDataCache(event) {
      this.$store.dispatch('cache/toggleDataCache', event.target.checked)
    },

    updateCacheExpire() {
      const expire = this.cacheExpireMinutes * 60000
      this.$store.dispatch('cache/setDataCacheExpire', expire)
    },

    removeCachedPage(page) {
      this.$store.commit('cache/REMOVE_CACHED_PAGE', page)
    },

    clearExpiredCache() {
      this.$store.dispatch('cache/clearExpiredCache')
      this.updateCacheStats()
      this.$store.dispatch('app/showSuccess', '过期缓存已清理')
    },

    confirmClearAllCache() {
      this.$refs.confirmDialog.show()
    },

    clearAllCache() {
      this.$store.dispatch('cache/clearAllCache')
      this.updateCacheStats()
      this.$store.dispatch('app/showSuccess', '所有缓存已清理')
    },

    formatSize(bytes) {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    },

    updateCacheStats() {
      this.cacheSize = window.cache.size()
      this.cacheKeys = window.cache.keys()
    }
  },

  mounted() {
    this.updateCacheStats()
  }
} 