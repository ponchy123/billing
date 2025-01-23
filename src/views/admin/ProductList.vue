<template>
  <div class="product-list">
    <div class="header">
      <h1>产品管理</h1>
      <div class="actions">
        <div class="search">
          <input type="text" v-model="searchQuery" placeholder="搜索产品..." @input="handleSearch">
        </div>
        <button class="add-btn" @click="handleAdd">+ 添加产品</button>
      </div>
    </div>

    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>产品名称</th>
          <th>产品代码</th>
          <th>创建时间</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="product in products" :key="product.id">
          <td>{{ product.id }}</td>
          <td>{{ product.name }}</td>
          <td>{{ product.code }}</td>
          <td>{{ formatDate(product.createTime) }}</td>
          <td>
            <button class="edit-btn" @click="handleEdit(product)">编辑</button>
            <button class="delete-btn" @click="handleDelete(product)">删除</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const products = ref([])
const searchQuery = ref('')

const fetchProducts = async () => {
  try {
    const response = await axios.get('/api/products')
    products.value = response.data.products
  } catch (error) {
    console.error('Failed to fetch products:', error)
  }
}

const handleSearch = () => {
  // Implement search logic
}

const handleAdd = () => {
  // Implement add logic
}

const handleEdit = (product) => {
  // Implement edit logic
}

const handleDelete = async (product) => {
  // Implement delete logic
}

const formatDate = (date) => {
  return new Date(date).toLocaleString()
}

onMounted(() => {
  fetchProducts()
})
</script>

<style scoped>
.product-list {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.actions {
  display: flex;
  gap: 10px;
}

.search input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 200px;
}

button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.add-btn {
  background-color: #4CAF50;
  color: white;
}

table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

th {
  background-color: #f5f5f5;
  font-weight: 600;
}

.edit-btn {
  background-color: #2196F3;
  color: white;
  margin-right: 8px;
}

.delete-btn {
  background-color: #f44336;
  color: white;
}
</style>
