// StartPostalTable组件
window.StartPostalTable = {
  template: `
    <div class="start-postal-table">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <div class="d-flex align-items-center gap-3">
          <h3>起始邮编管理</h3>
        </div>
        <div class="d-flex gap-2">
          <button class="btn btn-success" @click="importStartPostal">
            <i class="bi bi-file-earmark-excel"></i> 导入起始邮编
          </button>
          <button class="btn btn-primary" @click="openCreateModal">
            <i class="bi bi-plus"></i> 添加起始邮编
          </button>
        </div>
      </div>

      <div class="d-flex justify-content-end mb-3">
        <button class="btn btn-success" @click="importZoneExcel">
          <i class="bi bi-file-earmark-excel"></i> 导入收件邮编分区表
        </button>
      </div>

      <div class="table-responsive">
        <table class="table table-striped">
          <thead>
            <tr>
              <th>起始邮编</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="postal in startPostals" :key="postal.id">
              <td>{{ postal.start_code }} - {{ postal.end_code }}</td>
              <td>
                <button class="btn btn-sm btn-info me-2" @click="editPostal(postal)">
                  <i class="bi bi-pencil"></i> 编辑
                </button>
                <button class="btn btn-sm btn-danger" @click="deletePostal(postal)">
                  <i class="bi bi-trash"></i> 删除
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 添加/编辑邮编的模态框 -->
      <div class="modal fade" id="startPostalModal" tabindex="-1">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">{{ isEdit ? '编辑起始邮编' : '添加起始邮编' }}</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
              <form @submit.prevent="handleSubmit">
                <div class="mb-3">
                  <label for="start_code" class="form-label">起始邮编</label>
                  <input type="text" class="form-control" id="start_code" v-model="form.start_code" required>
                </div>
                <div class="mb-3">
                  <label for="end_code" class="form-label">结束邮编</label>
                  <input type="text" class="form-control" id="end_code" v-model="form.end_code" required>
                </div>
                <div class="mb-3">
                  <label for="zone_id" class="form-label">所属区域</label>
                  <select class="form-select" id="zone_id" v-model="form.zone_id" required>
                    <option value="">请选择区域</option>
                    <option v-for="zone in zones" :key="zone.id" :value="zone.id">
                      {{ zone.name }}
                    </option>
                  </select>
                </div>
              </form>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
              <button type="button" class="btn btn-primary" @click="handleSubmit">保存</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  data() {
    return {
      startPostals: [],
      zones: [],
      form: {
        start_code: '',
        end_code: '',
        zone_id: ''
      },
      isEdit: false,
      editId: null,
      modal: null
    }
  },
  methods: {
    async fetchStartPostals() {
      try {
        const response = await axios.get('/api/postal-zones/start')
        this.startPostals = response.data
      } catch (error) {
        console.error('获取起始邮编列表失败:', error)
        alert('获取起始邮编列表失败')
      }
    },
    async fetchZones() {
      try {
        const response = await axios.get('/api/postal-zones')
        this.zones = response.data
      } catch (error) {
        console.error('获取区域列表失败:', error)
        alert('获取区域列表失败')
      }
    },
    openCreateModal() {
      this.isEdit = false
      this.editId = null
      this.form = {
        start_code: '',
        end_code: '',
        zone_id: ''
      }
      this.modal.show()
    },
    editPostal(postal) {
      this.isEdit = true
      this.editId = postal.id
      this.form = {
        start_code: postal.start_code,
        end_code: postal.end_code,
        zone_id: postal.zone_id
      }
      this.modal.show()
    },
    async handleSubmit() {
      try {
        if (this.isEdit) {
          await axios.put(`/api/postal-zones/start/${this.editId}`, this.form)
        } else {
          await axios.post('/api/postal-zones/start', this.form)
        }
        this.modal.hide()
        await this.fetchStartPostals()
      } catch (error) {
        console.error('保存失败:', error)
        alert('保存失败')
      }
    },
    async deletePostal(postal) {
      if (confirm(`确定要删除这条邮编记录吗？`)) {
        try {
          await axios.delete(`/api/postal-zones/start/${postal.id}`)
          await this.fetchStartPostals()
          alert('删除成功')
        } catch (error) {
          console.error('删除邮编失败:', error)
          alert('删除邮编失败')
        }
      }
    },
    async importStartPostal() {
      const input = document.createElement('input')
      input.type = 'file'
      input.accept = '.xlsx'
      input.onchange = async (event) => {
        const file = event.target.files[0]
        if (!file) return

        const formData = new FormData()
        formData.append('file', file)

        try {
          await axios.post('/api/postal-zones/start/import', formData, {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          })
          await this.fetchStartPostals()
          alert('导入成功')
        } catch (error) {
          console.error('导入失败:', error)
          alert('导入失败')
        }
      }
      input.click()
    },
    async importZoneExcel() {
      const input = document.createElement('input')
      input.type = 'file'
      input.accept = '.xlsx'
      input.onchange = async (event) => {
        const file = event.target.files[0]
        if (!file) return

        const formData = new FormData()
        formData.append('file', file)

        try {
          await axios.post('/api/postal-zones/import-zone-excel', formData, {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          })
          await this.fetchStartPostals()
          await this.fetchZones()
          alert('导入成功')
        } catch (error) {
          console.error('导入失败:', error)
          alert('导入失败')
        }
      }
      input.click()
    }
  },
  mounted() {
    this.modal = new bootstrap.Modal(document.getElementById('startPostalModal'))
    this.fetchStartPostals()
    this.fetchZones()
  }
} 