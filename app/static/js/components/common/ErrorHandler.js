// ErrorHandler组件
const ErrorHandler = {
  name: 'ErrorHandler',
  template: `
    <div class="error-handler">
      <!-- 错误提示框 -->
      <div
        v-if="error"
        class="alert alert-danger alert-dismissible fade show position-fixed top-0 end-0 m-3"
        role="alert"
        style="z-index: 9999;"
      >
        <div class="d-flex align-items-center">
          <i class="bi bi-exclamation-triangle-fill me-2"></i>
          <div>
            <h6 class="alert-heading mb-1">错误</h6>
            <div class="error-message">{{ error.message }}</div>
            <div v-if="error.details" class="error-details small mt-2">
              {{ error.details }}
            </div>
          </div>
        </div>
        <button
          type="button"
          class="btn-close"
          @click="clearError"
          aria-label="关闭"
        ></button>
      </div>

      <!-- 成功提示框 -->
      <div
        v-if="success"
        class="alert alert-success alert-dismissible fade show position-fixed top-0 end-0 m-3"
        role="alert"
        style="z-index: 9999;"
      >
        <div class="d-flex align-items-center">
          <i class="bi bi-check-circle-fill me-2"></i>
          <div>{{ success }}</div>
        </div>
        <button
          type="button"
          class="btn-close"
          @click="clearSuccess"
          aria-label="关闭"
        ></button>
      </div>

      <!-- 加载中提示框 -->
      <div
        v-if="loading"
        class="loading-overlay position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center"
        style="background: rgba(255, 255, 255, 0.8); z-index: 9999;"
      >
        <div class="text-center">
          <div class="spinner-border text-primary mb-2" role="status">
            <span class="visually-hidden">加载中...</span>
          </div>
          <div>{{ loading }}</div>
        </div>
      </div>
    </div>
  `,
  data() {
    return {
      error: null,
      success: null,
      loading: null,
      errorTimeout: null,
      successTimeout: null
    }
  },
  methods: {
    showError(error) {
      this.error = error
      if (this.errorTimeout) {
        clearTimeout(this.errorTimeout)
      }
      this.errorTimeout = setTimeout(() => {
        this.clearError()
      }, 5000)
    },
    clearError() {
      this.error = null
      if (this.errorTimeout) {
        clearTimeout(this.errorTimeout)
        this.errorTimeout = null
      }
    },
    showSuccess(message) {
      this.success = message
      if (this.successTimeout) {
        clearTimeout(this.successTimeout)
      }
      this.successTimeout = setTimeout(() => {
        this.clearSuccess()
      }, 3000)
    },
    clearSuccess() {
      this.success = null
      if (this.successTimeout) {
        clearTimeout(this.successTimeout)
        this.successTimeout = null
      }
    },
    showLoading(text = '加载中...') {
      this.loading = text
    },
    hideLoading() {
      this.loading = null
    }
  },
  mounted() {
    // 注册全局事件处理器
    window.emitter.on('show-error', this.showError)
    window.emitter.on('show-success', this.showSuccess)
    window.emitter.on('show-loading', this.showLoading)
    window.emitter.on('hide-loading', this.hideLoading)
  },
  beforeUnmount() {
    // 移除全局事件处理器
    window.emitter.off('show-error', this.showError)
    window.emitter.off('show-success', this.showSuccess)
    window.emitter.off('show-loading', this.showLoading)
    window.emitter.off('hide-loading', this.hideLoading)
  }
}

// 导出组件
window.ErrorHandler = ErrorHandler 