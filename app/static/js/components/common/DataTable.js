// 数据表格组件
window.DataTable = {
  name: 'DataTable',
  props: {
    // 表格列配置
    columns: {
      type: Array,
      required: true
    },
    // 表格数据
    data: {
      type: Array,
      required: true
    },
    // 是否显示序号列
    showIndex: {
      type: Boolean,
      default: false
    },
    // 是否显示选择框
    selectable: {
      type: Boolean,
      default: false
    },
    // 选中的行
    selected: {
      type: Array,
      default: () => []
    },
    // 是否显示操作列
    showActions: {
      type: Boolean,
      default: false
    },
    // 是否显示边框
    bordered: {
      type: Boolean,
      default: true
    },
    // 是否显示斑马纹
    striped: {
      type: Boolean,
      default: true
    },
    // 是否显示加载状态
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:selected', 'edit', 'delete'],
  setup(props, { emit }) {
    // 是否全选
    const isAllSelected = computed(() => {
      return props.data.length > 0 && props.selected.length === props.data.length
    })

    // 是否部分选中
    const isIndeterminate = computed(() => {
      return props.selected.length > 0 && props.selected.length < props.data.length
    })

    // 切换全选
    const toggleSelectAll = () => {
      if (isAllSelected.value) {
        emit('update:selected', [])
      } else {
        emit('update:selected', props.data.map(item => item.id))
      }
    }

    // 切换单选
    const toggleSelect = (id) => {
      const selected = [...props.selected]
      const index = selected.indexOf(id)
      if (index === -1) {
        selected.push(id)
      } else {
        selected.splice(index, 1)
      }
      emit('update:selected', selected)
    }

    // 编辑行
    const handleEdit = (row) => {
      emit('edit', row)
    }

    // 删除行
    const handleDelete = (row) => {
      emit('delete', row)
    }

    return {
      isAllSelected,
      isIndeterminate,
      toggleSelectAll,
      toggleSelect,
      handleEdit,
      handleDelete
    }
  },
  template: `
    <div class="table-responsive">
      <table class="table" :class="{
        'table-bordered': bordered,
        'table-striped': striped
      }">
        <thead>
          <tr>
            <th v-if="showIndex" width="80">#</th>
            <th v-if="selectable" width="50">
              <div class="form-check">
                <input type="checkbox" class="form-check-input"
                  :checked="isAllSelected"
                  :indeterminate="isIndeterminate"
                  @change="toggleSelectAll">
              </div>
            </th>
            <th v-for="col in columns" :key="col.prop" :width="col.width">
              {{ col.label }}
            </th>
            <th v-if="showActions" width="150">操作</th>
          </tr>
        </thead>
        <tbody v-if="!loading">
          <tr v-for="(row, index) in data" :key="row.id">
            <td v-if="showIndex">{{ index + 1 }}</td>
            <td v-if="selectable">
              <div class="form-check">
                <input type="checkbox" class="form-check-input"
                  :checked="selected.includes(row.id)"
                  @change="toggleSelect(row.id)">
              </div>
            </td>
            <td v-for="col in columns" :key="col.prop">
              <template v-if="col.formatter">
                {{ col.formatter(row[col.prop], row) }}
              </template>
              <template v-else>
                {{ row[col.prop] }}
              </template>
            </td>
            <td v-if="showActions">
              <button type="button" class="btn btn-sm btn-primary me-2"
                @click="handleEdit(row)">
                编辑
              </button>
              <button type="button" class="btn btn-sm btn-danger"
                @click="handleDelete(row)">
                删除
              </button>
            </td>
          </tr>
        </tbody>
        <tbody v-else>
          <tr>
            <td :colspan="columns.length + (showIndex ? 1 : 0) + (selectable ? 1 : 0) + (showActions ? 1 : 0)"
              class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">加载中...</span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  `
} 