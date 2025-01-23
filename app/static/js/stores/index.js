// 创建全局状态管理
window.stores = {
  auth: {
    state: Vue.reactive({
      token: localStorage.getItem('token'),
      user: null,
      isAuthenticated: false
    }),
    getters: {
      currentUser: () => window.stores.auth.state.user,
      userToken: () => window.stores.auth.state.token
    },
    actions: {
      async login(credentials) {
        try {
          const response = await window.api.auth.login(credentials)
          const { token, user } = response
          this.state.token = token
          this.state.user = user
          this.state.isAuthenticated = true
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
          this.state.token = null
          this.state.user = null
          this.state.isAuthenticated = false
          localStorage.removeItem('token')
        }
      },
      async fetchCurrentUser() {
        try {
          const response = await window.api.auth.getCurrentUser()
          this.state.user = response
          this.state.isAuthenticated = true
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
          this.state.token = token
          this.state.isAuthenticated = true
          this.fetchCurrentUser()
        }
      }
    }
  }
} 