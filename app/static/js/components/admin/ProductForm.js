// 产品表单组件
window.ProductForm = {
  template: `
    <form @submit.prevent="handleSubmit">
      <div class="mb-3">
        <label for="name" class="form-label">产品名称</label>
        <input type="text" class="form-control" id="name" v-model="form.name" required>
      </div>
      
      <div class="mb-3">
        <label for="carrier" class="form-label">服务商</label>
        <input type="text" class="form-control" id="carrier" v-model="form.carrier" required>
      </div>

      <div class="mb-3">
        <label for="service_type" class="form-label">服务类型</label>
        <input type="text" class="form-control" id="service_type" v-model="form.service_type">
      </div>

      <div class="row">
        <div class="col-md-6 mb-3">
          <label for="currency" class="form-label">货币单位</label>
          <input type="text" class="form-control" id="currency" v-model="form.currency" required>
        </div>
        <div class="col-md-6 mb-3">
          <label for="unit" class="form-label">重量单位</label>
          <input type="text" class="form-control" id="unit" v-model="form.unit" required>
        </div>
      </div>

      <div class="mb-3">
        <label for="dim" class="form-label">体积重系数</label>
        <input type="number" class="form-control" id="dim" v-model="form.dim" step="0.01" min="0">
      </div>

      <div class="mb-3">
        <label class="form-label">启用状态</label>
        <div class="form-check">
          <input type="checkbox" class="form-check-input" id="is_active" v-model="form.is_active">
          <label class="form-check-label" for="is_active">启用</label>
        </div>
      </div>

      <div class="mb-3">
        <label for="start_date" class="form-label">启用时间</label>
        <input type="datetime-local" class="form-control" id="start_date" v-model="form.start_date" required>
      </div>

      <div class="mb-3">
        <label for="end_date" class="form-label">失效时间</label>
        <input type="datetime-local" class="form-control" id="end_date" v-model="form.end_date">
      </div>

      <div class="mb-3">
        <label class="form-label">区域费率</label>
        <div class="table-responsive">
          <table class="table table-bordered">
            <thead>
              <tr>
                <th>重量</th>
                <th v-for="zone in ['Zone1', 'Zone2', 'Zone3', 'Zone4', 'Zone5', 'Zone6', 'Zone7', 'Zone8']" :key="zone">
                  {{zone}}
                </th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(rate, index) in zoneRates" :key="index">
                <td>
                  <input type="number" class="form-control form-control-sm" v-model="rate.weight" step="0.01" min="0">
                </td>
                <td v-for="zone in ['Zone1', 'Zone2', 'Zone3', 'Zone4', 'Zone5', 'Zone6', 'Zone7', 'Zone8']" :key="zone">
                  <input type="number" class="form-control form-control-sm" v-model="rate[zone]" step="0.0001" min="0">
                </td>
                <td>
                  <button type="button" class="btn btn-danger btn-sm" @click="removeZoneRate(index)">删除</button>
                </td>
              </tr>
            </tbody>
          </table>
          <button type="button" class="btn btn-secondary" @click="addZoneRate">添加行</button>
        </div>
      </div>

      <div class="mb-3">
        <label class="form-label">附加费用</label>
        <div class="table-responsive">
          <table class="table table-bordered">
            <thead>
              <tr>
                <th>费用名称</th>
                <th>费用金额</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(surcharge, index) in surcharges" :key="index">
                <td>
                  <input type="text" class="form-control form-control-sm" v-model="surcharge.name">
                </td>
                <td>
                  <input type="number" class="form-control form-control-sm" v-model="surcharge.amount" step="0.01" min="0">
                </td>
                <td>
                  <button type="button" class="btn btn-danger btn-sm" @click="removeSurcharge(index)">删除</button>
                </td>
              </tr>
            </tbody>
          </table>
          <button type="button" class="btn btn-secondary" @click="addSurcharge">添加附加费用</button>
        </div>
      </div>

      <div class="mb-3">
        <label for="notes" class="form-label">备注说明</label>
        <textarea class="form-control" id="notes" v-model="form.notes" rows="3"></textarea>
      </div>

      <div class="d-flex justify-content-end gap-2">
        <button type="button" class="btn btn-secondary" @click="$emit('cancel')">取消</button>
        <button type="submit" class="btn btn-primary">保存</button>
      </div>
    </form>
  `,
  props: {
    initialData: {
      type: Object,
      default: () => ({
        name: '',
        carrier: '',
        service_type: '',
        currency: 'USD',
        unit: 'KG',
        dim: 0,
        is_active: true,
        start_date: new Date().toISOString().slice(0, 16),
        end_date: '',
        zone_rates: '[]',
        surcharges: '{}',
        notes: ''
      })
    }
  },
  data() {
    return {
      form: {
        ...this.initialData,
        zone_rates: this.initialData.zone_rates ? JSON.parse(this.initialData.zone_rates) : [],
        surcharges: this.initialData.surcharges ? JSON.parse(this.initialData.surcharges) : {}
      },
      zoneRates: [],
      surcharges: []
    }
  },
  methods: {
    addZoneRate() {
      this.zoneRates.push({
        weight: 0,
        Zone1: 0,
        Zone2: 0,
        Zone3: 0,
        Zone4: 0,
        Zone5: 0,
        Zone6: 0,
        Zone7: 0,
        Zone8: 0
      })
    },
    removeZoneRate(index) {
      this.zoneRates.splice(index, 1)
    },
    addSurcharge() {
      this.surcharges.push({
        name: '',
        amount: 0
      })
    },
    removeSurcharge(index) {
      this.surcharges.splice(index, 1)
    },
    handleSubmit() {
      // 准备提交的数据
      const formData = {
        ...this.form,
        zone_rates: JSON.stringify(this.zoneRates),
        surcharges: JSON.stringify(this.surcharges.reduce((acc, curr) => {
          acc[curr.name] = curr.amount
          return acc
        }, {}))
      }
      this.$emit('submit', formData)
    }
  },
  mounted() {
    // 初始化区域费率数据
    if (this.form.zone_rates && Array.isArray(this.form.zone_rates)) {
      this.zoneRates = this.form.zone_rates
    }
    
    // 初始化附加费用数据
    if (this.form.surcharges) {
      this.surcharges = Object.entries(this.form.surcharges).map(([name, amount]) => ({
        name,
        amount
      }))
    }
  }
} 