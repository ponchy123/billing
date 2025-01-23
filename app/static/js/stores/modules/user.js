// 用户状态管理模块
const useUserStore = window.defineStore('user', {
  state: () => ({
    users: [],
    currentPage: 1,
    totalPages: 1,
    loading: false,
    error: null
  }),
  actions: {
    setUsers(users) {
      this.users = users
    },
    setPagination({ currentPage, totalPages }) {
      this.currentPage = currentPage
      this.totalPages = totalPages
    },
    setLoading(loading) {
      this.loading = loading
    },
    setError(error) {
      this.error = error
    },
    async fetchUsers({ page = 1, query = '' } = {}) {
      this.setLoading(true)
      try {
        const response = await window.api.user.list({ page, query })
        this.setUsers(response.users)
        this.setPagination({
          currentPage: response.currentPage,
          totalPages: response.totalPages
        })
      } catch (error) {
        this.setError(error.message)
        throw error
      } finally {
        this.setLoading(false)
      }
    },
    async createUser(userData) {
      try {
        await window.api.user.create(userData)
        await this.fetchUsers()
      } catch (error) {
        throw error
      }
    },
    async updateUser({ id, data }) {
      try {
        await window.api.user.update(id, data)
        await this.fetchUsers()
      } catch (error) {
        throw error
      }
    },
    async deleteUser(id) {
      try {
        await window.api.user.delete(id)
        await this.fetchUsers()
      } catch (error) {
        throw error
      }
    }
  }
})

// 导出 store
window.useUserStore = useUserStore 