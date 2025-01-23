// 定义管理布局组件
const AdminLayout = {
  name: 'AdminLayout',
  setup() {
    const router = VueRouter.useRouter()
    const auth = window.stores.auth
    const user = Vue.computed(() => auth.state.user)
    const isAdmin = Vue.computed(() => user.value?.role === 'admin')

    const menuItems = Vue.computed(() => {
      // 基础菜单项 - 所有用户都可以访问的计算功能
      const baseMenus = [
        {
          title: '费用计算',
          icon: 'bi-calculator',
          path: '/admin/calculator'
        }
      ]

      // 管理员菜单项
      const adminMenus = [
        {
          title: '仪表盘',
          icon: 'bi-speedometer2',
          path: '/admin'
        },
        {
          title: '用户管理',
          icon: 'bi-people',
          path: '/admin/users'
        },
        {
          title: '产品管理',
          icon: 'bi-box',
          path: '/admin/products'
        },
        {
          title: '邮编区域',
          icon: 'bi-geo-alt',
          path: '/admin/postal-zones'
        },
        {
          title: '燃油费率',
          icon: 'bi-fuel-pump',
          path: '/admin/fuel-rates'
        }
      ]

      // 根据用户角色返回对应的菜单项
      return isAdmin.value ? [...adminMenus, ...baseMenus] : baseMenus
    })

    const handleLogout = async () => {
      try {
        await auth.actions.logout()
        router.push('/login')
      } catch (error) {
        console.error('退出登录失败:', error)
      }
    }

    return {
      user,
      menuItems,
      handleLogout
    }
  },
  template: `
    <div class="admin-layout">
      <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container-fluid">
          <router-link class="navbar-brand" to="/admin">运费计算系统</router-link>
          
          <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <span class="navbar-toggler-icon"></span>
          </button>
          
          <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav me-auto">
              <li v-for="item in menuItems" :key="item.path" class="nav-item">
                <router-link :to="item.path" class="nav-link" active-class="active">
                  <i :class="item.icon" class="me-1"></i>
                  {{ item.title }}
                </router-link>
              </li>
            </ul>
            
            <div class="d-flex align-items-center">
              <span class="text-light me-3">
                <i class="bi bi-person-circle me-1"></i>
                {{ user?.username }}
              </span>
              <button class="btn btn-outline-light" @click="handleLogout">
                <i class="bi bi-box-arrow-right me-1"></i>
                退出
              </button>
            </div>
          </div>
        </div>
      </nav>
      
      <div class="container-fluid py-4">
        <router-view></router-view>
      </div>
    </div>
  `
}

// 导出组件
window.AdminLayout = AdminLayout 