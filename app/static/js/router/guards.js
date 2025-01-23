// 路由守卫
window.setupRouteGuards = (router) => {
  router.beforeEach(async (to, from, next) => {
    try {
      const auth = window.stores.auth
      
      // 如果访问登录页且已登录，重定向到首页
      if (to.path === '/login' && auth.state.isAuthenticated) {
        next({ path: '/admin' })
        return
      }

      // 如果路由需要认证（除了登录页面外的所有页面）
      if (to.path !== '/login') {
        // 如果未登录，重定向到登录页
        if (!auth.state.isAuthenticated) {
          next({
            path: '/login',
            query: { redirect: to.fullPath }
          })
          return
        }

        // 如果没有用户信息，获取用户信息
        if (!auth.state.user) {
          try {
            await auth.actions.fetchCurrentUser()
          } catch (error) {
            console.error('获取用户信息失败:', error)
            next({
              path: '/login',
              query: { redirect: to.fullPath }
            })
            return
          }
        }

        // 检查管理员路由权限
        const adminRoutes = ['/admin/users', '/admin/products', '/admin/postal-zones', '/admin/fuel-rates']
        if (adminRoutes.some(route => to.path.startsWith(route)) && auth.state.user?.role !== 'admin') {
          console.error('没有访问权限')
          next('/admin/calculator')
          return
        }
      }

      next()
    } catch (error) {
      console.error('路由守卫错误:', error)
      next(false)
    }
  })
} 