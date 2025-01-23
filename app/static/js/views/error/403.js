// 403权限错误页面
window.ForbiddenView = {
  template: `
    <div class="forbidden-view">
      <div class="container">
        <div class="row justify-content-center">
          <div class="col-md-6 text-center">
            <div class="error-template">
              <h1>403</h1>
              <h2>访问被拒绝</h2>
              <div class="error-details mb-4">
                抱歉，您没有权限访问此页面！
              </div>
              <div class="error-actions">
                <router-link to="/" class="btn btn-primary">
                  <i class="bi bi-house-door"></i> 返回首页
                </router-link>
                <button class="btn btn-secondary ms-2" @click="goBack">
                  <i class="bi bi-arrow-left"></i> 返回上一页
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  methods: {
    goBack() {
      window.history.back()
    }
  }
} 