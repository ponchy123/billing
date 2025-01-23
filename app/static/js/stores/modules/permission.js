// 权限管理模块
const usePermissionStore = window.defineStore('permission', {
  state: () => ({
    permissions: [],
    roles: [],
    userPermissions: []
  }),
  actions: {
    setPermissions(permissions) {
      this.permissions = permissions
    },
    setRoles(roles) {
      this.roles = roles
    },
    setUserPermissions(permissions) {
      this.userPermissions = permissions
    },
    async fetchPermissions() {
      try {
        const permissions = await window.api.permission.list()
        this.setPermissions(permissions)
      } catch (error) {
        throw error
      }
    },
    async fetchRoles() {
      try {
        const roles = await window.api.role.list()
        this.setRoles(roles)
      } catch (error) {
        throw error
      }
    },
    async fetchUserPermissions(userId) {
      try {
        const permissions = await window.api.permission.getUserPermissions(userId)
        this.setUserPermissions(permissions)
      } catch (error) {
        throw error
      }
    }
  },
  getters: {
    hasPermission: (state) => (permissionName) => {
      // 如果用户是管理员，拥有所有权限
      if (state.userPermissions.includes('admin')) {
        return true
      }
      // 检查用户是否拥有特定权限
      return state.userPermissions.includes(permissionName)
    },
    allPermissions: state => state.permissions,
    allRoles: state => state.roles,
    userPermissions: state => state.userPermissions
  }
})

// 导出 store
window.usePermissionStore = usePermissionStore 