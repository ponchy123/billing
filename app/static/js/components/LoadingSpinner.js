const LoadingSpinner = {
  name: 'LoadingSpinner',
  template: `
    <div class="loading-spinner">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">加载中...</span>
      </div>
    </div>
  `
}

// 导出组件
window.LoadingSpinner = LoadingSpinner 