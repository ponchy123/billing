const NotFoundView = {
  name: 'NotFoundView',
  template: `
    <div class="not-found-view d-flex align-items-center justify-content-center" style="min-height: 100vh;">
      <div class="text-center">
        <h1 class="display-1 fw-bold text-primary mb-4">404</h1>
        <h2 class="mb-4">页面未找到</h2>
        <p class="mb-4 text-muted">抱歉，您访问的页面不存在或已被移除。</p>
        <router-link to="/" class="btn btn-primary">
          <i class="bi bi-house-door me-2"></i>返回首页
        </router-link>
      </div>
    </div>
  `
}

// 导出组件
window.NotFoundView = NotFoundView 