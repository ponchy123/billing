// LoadingSpinner组件
const LoadingSpinner = {
  template: `
    <div class="loading-spinner" v-if="visible">
      <div class="spinner-backdrop"></div>
      <div class="spinner-content">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">加载中...</span>
        </div>
        <div class="spinner-text mt-2" v-if="text">{{ text }}</div>
      </div>
    </div>
  `,

  data() {
    return {
      visible: false,
      text: ''
    }
  },

  mounted() {
    // 监听显示加载事件
    window.eventBus.on('show-loading', text => {
      this.text = text || ''
      this.visible = true
    })

    // 监听隐藏加载事件
    window.eventBus.on('hide-loading', () => {
      this.visible = false
      this.text = ''
    })
  },

  beforeUnmount() {
    // 移除事件监听
    window.eventBus.off('show-loading')
    window.eventBus.off('hide-loading')
  }
}

// 注册为全局组件
window.LoadingSpinner = LoadingSpinner 