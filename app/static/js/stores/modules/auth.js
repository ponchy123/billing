// 认证状态管理
const useAuthStore = window.defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    isAuthenticated: false
  }),
  getters: {
    currentUser: (state) => state.user,
    userToken: (state) => state.token
  },
  actions: {
    async login(credentials) {
      try {
        const response = await window.api.auth.login(credentials)
        const { token, user } = response
        this.token = token
        this.user = user
        this.isAuthenticated = true
        localStorage.setItem('token', token)
        return response
      } catch (error) {
        console.error('Login failed:', error)
        throw error
      }
    },
    async logout() {
      try {
        await window.api.auth.logout()
      } catch (error) {
        console.error('Logout failed:', error)
      } finally {
        this.token = null
        this.user = null
        this.isAuthenticated = false
        localStorage.removeItem('token')
      }
    },
    async fetchCurrentUser() {
      try {
        const response = await window.api.auth.getCurrentUser()
        this.user = response
        this.isAuthenticated = true
        return response
      } catch (error) {
        console.error('Failed to fetch user:', error)
        this.logout()
        throw error
      }
    },
    initializeAuth() {
      const token = localStorage.getItem('token')
      if (token) {
        this.token = token
        this.isAuthenticated = true
        this.fetchCurrentUser()
      }
    }
  }
})

// 导出 store
window.useAuthStore = useAuthStore