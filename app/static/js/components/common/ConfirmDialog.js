// ConfirmDialog组件
const ConfirmDialog = {
  template: `
    <div v-if="show" class="modal fade show" style="display: block">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ title }}</h5>
            <button type="button" class="btn-close" @click="handleCancel"></button>
          </div>
          <div class="modal-body">
            {{ message }}
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="handleCancel">{{ cancelText }}</button>
            <button type="button" class="btn btn-primary" @click="handleConfirm">{{ confirmText }}</button>
          </div>
        </div>
      </div>
      <div class="modal-backdrop fade show"></div>
    </div>
  `,
  props: {
    show: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      default: '确认'
    },
    message: {
      type: String,
      default: ''
    },
    confirmText: {
      type: String,
      default: '确定'
    },
    cancelText: {
      type: String,
      default: '取消'
    }
  },
  emits: ['confirm', 'cancel', 'update:show'],
  setup(props, { emit }) {
    const handleConfirm = () => {
      emit('confirm')
      emit('update:show', false)
    }

    const handleCancel = () => {
      emit('cancel')
      emit('update:show', false)
    }

    return {
      handleConfirm,
      handleCancel
    }
  }
}

// 注册为全局组件
window.ConfirmDialog = ConfirmDialog 