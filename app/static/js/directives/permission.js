// 权限指令
window.vPermission = {
  mounted(el, binding) {
    const { value } = binding
    const store = window.app.$store
    
    if (value && !store.getters['permission/hasPermission'](value)) {
      el.parentNode?.removeChild(el)
    }
  }
}

// 角色指令
window.vRole = {
  mounted(el, binding) {
    const { value } = binding
    const store = window.app.$store
    const userRoles = store.state.permission.userPermissions
    
    if (value && !userRoles.includes(value)) {
      el.parentNode?.removeChild(el)
    }
  }
} 