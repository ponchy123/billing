import { createRouter, createWebHistory } from 'vue-router'
import ProductList from '../views/admin/ProductList.vue'

const routes = [
  {
    path: '/admin/products',
    name: 'AdminProducts',
    component: ProductList
  },
  // Redirect root to admin products
  {
    path: '/',
    redirect: '/admin/products'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
