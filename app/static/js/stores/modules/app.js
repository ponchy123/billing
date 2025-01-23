// 创建 app store
const useAppStore = window.defineStore('app', {
  state: () => ({
    loading: false,
    error: null
  }),

  actions: {
    setLoading(status) {
      this.loading = status
    },

    setError(error) {
      this.error = error
    },

    clearError() {
      this.error = null
    }
  }
})

// 导出 store
window.useAppStore = useAppStore