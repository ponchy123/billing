// 等待 DOM 加载完成后初始化应用
window.addEventListener('DOMContentLoaded', () => {
  // 创建Vue应用实例
  const app = Vue.createApp({
    render() {
      return Vue.h(VueRouter.RouterView)
    }
  })

  // 注册全局组件
  app.component('loading-spinner', window.LoadingSpinner)
  app.component('confirm-dialog', window.ConfirmDialog)
  app.component('error-handler', window.ErrorHandler)

  // 使用Vue Router
  app.use(window.router)

  // 挂载应用
  app.mount('#app')
})