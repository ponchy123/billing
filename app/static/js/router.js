// 获取Vue Router组件和方法
const { RouterView } = VueRouter

// 创建路由实例并立即导出到全局
window.router = VueRouter.createRouter({
  history: VueRouter.createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/admin'
    },
    {
      path: '/login',
      name: 'login',
      component: window.LoginView
    },
    {
      path: '/admin',
      component: window.AdminLayout,
      children: [
        {
          path: '',
          name: 'dashboard',
          component: window.DashboardView
        },
        {
          path: 'users',
          name: 'users',
          component: window.UsersView
        },
        {
          path: 'users/add',
          name: 'user-create',
          component: window.UserEdit
        },
        {
          path: 'users/:id/edit',
          name: 'user-edit',
          component: window.UserEdit
        },
        {
          path: 'products',
          name: 'products',
          component: window.ProductList
        },
        {
          path: 'products/add',
          name: 'product-add',
          component: window.ProductEdit
        },
        {
          path: 'products/edit/:id',
          name: 'product-edit',
          component: window.ProductEdit
        },
        {
          path: 'postal-zones',
          name: 'postal-zones',
          component: window.PostalZonesView
        },
        {
          path: 'fuel-rates',
          name: 'fuel-rates',
          component: window.FuelRatesView
        },
        {
          path: 'calculator',
          name: 'calculator',
          component: window.CalculatorView
        }
      ]
    }
  ]
}) 