// 等待所有组件和依赖加载完成
window.addEventListener('DOMContentLoaded', () => {
  // 初始化认证状态
  window.stores.auth.actions.initializeAuth()

  // 创建Vue应用实例
  const app = Vue.createApp(window.App)

  // 注册全局组件
  app.component('confirm-dialog', window.ConfirmDialog)
  app.component('error-handler', window.ErrorHandler)
  app.component('loading-spinner', window.LoadingSpinner)

  // 确保路由已经加载
  if (window.router) {
    // 设置路由守卫
    window.setupRouteGuards(window.router)
    
    // 使用Vue Router
    app.use(window.router)

    // 挂载应用
    app.mount('#app')
  } else {
    console.error('路由未正确加载')
  }
})