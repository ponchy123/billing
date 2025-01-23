const NotFoundView = {
  name: 'NotFoundView',
  template: `
    <div class="not-found-page">
      <div class="text-center">
        <h1 class="display-1">404</h1>
        <h2 class="mb-4">页面未找到</h2>
        <p class="mb-4">抱歉，您访问的页面不存在。</p>
        <router-link to="/" class="btn btn-primary">
          <i class="bi bi-house-door me-1"></i>返回首页
        </router-link>
      </div>
    </div>
  `
} 