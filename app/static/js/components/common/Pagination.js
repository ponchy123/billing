// 分页组件
window.Pagination = {
  name: 'Pagination',
  props: {
    total: {
      type: Number,
      required: true
    },
    pageSize: {
      type: Number,
      default: 10
    },
    currentPage: {
      type: Number,
      default: 1
    },
    showTotal: {
      type: Boolean,
      default: true
    }
  },
  emits: ['update:currentPage', 'change'],
  setup(props, { emit }) {
    const totalPages = computed(() => Math.ceil(props.total / props.pageSize))
    
    const pageList = computed(() => {
      const pages = []
      const current = props.currentPage
      const total = totalPages.value
      
      // 总是显示第一页
      pages.push(1)
      
      if (current > 3) {
        pages.push('...')
      }
      
      // 显示当前页前后两页
      for (let i = Math.max(2, current - 2); i <= Math.min(total - 1, current + 2); i++) {
        pages.push(i)
      }
      
      if (current < total - 2) {
        pages.push('...')
      }
      
      // 总是显示最后一页
      if (total > 1) {
        pages.push(total)
      }
      
      return pages
    })
    
    const handlePageChange = (page) => {
      if (page === '...') return
      if (page === props.currentPage) return
      emit('update:currentPage', page)
      emit('change', page)
    }
    
    const prev = () => {
      if (props.currentPage > 1) {
        handlePageChange(props.currentPage - 1)
      }
    }
    
    const next = () => {
      if (props.currentPage < totalPages.value) {
        handlePageChange(props.currentPage + 1)
      }
    }
    
    return {
      totalPages,
      pageList,
      handlePageChange,
      prev,
      next
    }
  },
  template: `
    <nav aria-label="分页导航" class="mt-3">
      <ul class="pagination justify-content-center mb-0">
        <li v-if="showTotal" class="page-item disabled me-3">
          <span class="page-link bg-transparent border-0">
            共 {{ total }} 条记录
          </span>
        </li>
        
        <li class="page-item" :class="{ disabled: currentPage === 1 }">
          <a class="page-link" href="#" @click.prevent="prev">上一页</a>
        </li>
        
        <li v-for="page in pageList" :key="page" 
            class="page-item" :class="{ active: page === currentPage, disabled: page === '...' }">
          <a class="page-link" href="#" @click.prevent="handlePageChange(page)">{{ page }}</a>
        </li>
        
        <li class="page-item" :class="{ disabled: currentPage === totalPages }">
          <a class="page-link" href="#" @click.prevent="next">下一页</a>
        </li>
      </ul>
    </nav>
  `
} 