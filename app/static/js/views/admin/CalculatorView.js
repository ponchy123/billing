const { ref, computed, onMounted } = Vue;

const CalculatorView = {
  name: 'calculator-view',
  template: `
    <div class="calculator-view">
      <div class="card">
        <div class="card-header">
          <h3>运费计算</h3>
        </div>
        <div class="card-body">
          <div v-if="error" class="alert alert-danger mb-3">{{ error }}</div>
          
          <form @submit.prevent="handleCalculate">
            <div class="row mb-3">
              <div class="col-md-6">
                <label class="form-label">起始邮编</label>
                <input type="text" class="form-control" v-model="form.fromPostalCode" placeholder="请输入5位邮编">
              </div>
              <div class="col-md-6">
                <label class="form-label">目的邮编</label>
                <input type="text" class="form-control" v-model="form.toPostalCode" placeholder="请输入5位邮编（可选）">
              </div>
            </div>

            <div class="row mb-3">
              <div class="col-md-12">
                <label class="form-label">产品</label>
                <select class="form-select" v-model="form.product_id">
                  <option value="">请选择产品</option>
                  <option v-for="product in products" :key="product.id" :value="product.id">{{ product.name }}</option>
                </select>
              </div>
            </div>

            <div class="row mb-3">
              <div class="col-md-3">
                <label class="form-label">重量(kg)</label>
                <input type="number" class="form-control" v-model="form.weight" step="0.01" min="0">
              </div>
              <div class="col-md-3">
                <label class="form-label">长度(cm)</label>
                <input type="number" class="form-control" v-model="form.length" step="0.01" min="0">
              </div>
              <div class="col-md-3">
                <label class="form-label">宽度(cm)</label>
                <input type="number" class="form-control" v-model="form.width" step="0.01" min="0">
              </div>
              <div class="col-md-3">
                <label class="form-label">高度(cm)</label>
                <input type="number" class="form-control" v-model="form.height" step="0.01" min="0">
              </div>
            </div>

            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? '计算中...' : '计算运费' }}
            </button>
          </form>

          <div v-if="resultRows.length > 0" class="mt-4">
            <template v-for="row in resultRows" :key="row.zone">
              <div class="card mb-3">
                <div class="card-header">
                  <h5 class="mb-0">Zone {{ row.zone }}</h5>
                </div>
                <div class="card-body">
                  <!-- 不可发包裹信息 -->
                  <div v-if="row.isUnauthorized" class="alert alert-danger">
                    <h5>不可发包裹</h5>
                    <p class="mb-3">{{ row.reason }}</p>
                    
                    <div class="package-info mb-3">
                      <h6>包裹信息:</h6>
                      <div class="row">
                        <div class="col-md-4">
                          <div>实际重量: {{ row.packageInfo.weight.actualWeight }}</div>
                          <div>体积重量: {{ row.packageInfo.weight.volumeWeight }}</div>
                          <div>计费重量: {{ row.packageInfo.weight.chargeableWeight }}</div>
                        </div>
                        <div class="col-md-8">
                          <div>尺寸: {{ row.packageInfo.dimensions.length }} × {{ row.packageInfo.dimensions.width }} × {{ row.packageInfo.dimensions.height }}</div>
                          <div>周长: {{ row.packageInfo.dimensions.girth }}</div>
                          <div>总长度+周长: {{ row.packageInfo.dimensions.totalLengthGirth }}</div>
                        </div>
                      </div>
                    </div>
                    
                    <div class="fee-info">
                      <h6>费用信息:</h6>
                      <div class="row">
                        <div class="col-md-6">基础费用: {{ formatAmount(row.details.base_fee) }}</div>
                        <div class="col-md-6">PSS费用: {{ formatAmount(row.details.pss_fee) }}</div>
                      </div>
                      <div class="total-fee mt-2">
                        <strong>总费用: {{ row.formattedTotalAmount }}</strong>
                      </div>
                    </div>
                  </div>

                  <!-- 正常包裹信息 -->
                  <div v-else>
                    <div class="package-info mb-3">
                      <h6>包裹信息:</h6>
                      <div class="row">
                        <div class="col-md-4">
                          <div>实际重量: {{ row.packageInfo.weight.actualWeight }}</div>
                          <div>体积重量: {{ row.packageInfo.weight.volumeWeight }}</div>
                          <div>计费重量: {{ row.packageInfo.weight.chargeableWeight }}</div>
                        </div>
                        <div class="col-md-8">
                          <div>尺寸: {{ row.packageInfo.dimensions.length }} × {{ row.packageInfo.dimensions.width }} × {{ row.packageInfo.dimensions.height }}</div>
                          <div>周长: {{ row.packageInfo.dimensions.girth }}</div>
                          <div>总长度+周长: {{ row.packageInfo.dimensions.totalLengthGirth }}</div>
                        </div>
                      </div>
                    </div>

                    <div class="fee-details">
                      <h6>费用明细:</h6>
                      <table class="table table-bordered">
                        <tbody>
                          <tr>
                            <th>基础运费</th>
                            <td>{{ row.formattedBaseRate }}</td>
                          </tr>
                          <tr v-if="row.surchargeDetails?.handlingFee?.amount > 0">
                            <th>额外处理费</th>
                            <td>
                              <div>基础费用: {{ formatAmount(row.surchargeDetails.handlingFee.details.baseFee) }}</div>
                              <div>PSS费用: {{ formatAmount(row.surchargeDetails.handlingFee.details.pssFee) }}</div>
                              <div class="text-primary">总费用: {{ formatAmount(row.surchargeDetails.handlingFee.amount) }}</div>
                            </td>
                          </tr>
                          <tr v-if="row.surchargeDetails?.oversizeFeeCommercial?.amount > 0">
                            <th>超大超尺寸费(商业)</th>
                            <td>{{ row.formattedOversizeFeeComm }}</td>
                          </tr>
                          <tr v-if="row.surchargeDetails?.oversizeFeeResidential?.amount > 0">
                            <th>超大超尺寸费(住宅)</th>
                            <td>
                              <div>基础费用: {{ formatAmount(row.surchargeDetails.oversizeFeeResidential.details.baseFee) }}</div>
                              <div>PSS费用: {{ formatAmount(row.surchargeDetails.oversizeFeeResidential.details.pssFee) }}</div>
                              <div class="text-primary">总费用: {{ formatAmount(row.surchargeDetails.oversizeFeeResidential.amount) }}</div>
                            </td>
                          </tr>
                          <tr v-if="row.surchargeDetails?.residentialFee?.amount > 0">
                            <th>住宅地址附加费</th>
                            <td>
                              <div>基础费用: {{ formatAmount(row.surchargeDetails.residentialFee.details.baseFee) }}</div>
                              <div>PSS费用: {{ formatAmount(row.surchargeDetails.residentialFee.details.pssFee) }}</div>
                              <div class="text-primary">总费用: {{ formatAmount(row.surchargeDetails.residentialFee.amount) }}</div>
                            </td>
                          </tr>
                          <tr v-if="row.surchargeDetails?.remoteFee?.amount > 0">
                            <th>偏远地区附加费</th>
                            <td>
                              <div>基础费用: {{ formatAmount(row.surchargeDetails.remoteFee.details.baseFee) }}</div>
                              <div>PSS费用: {{ formatAmount(row.surchargeDetails.remoteFee.details.pssFee) }}</div>
                              <div class="text-primary">总费用: {{ formatAmount(row.surchargeDetails.remoteFee.amount) }}</div>
                              <div class="text-muted">{{ row.surchargeDetails.remoteFee.details.reason }}</div>
                            </td>
                          </tr>
                          <tr>
                            <th>燃油费</th>
                            <td>
                              <div>费率: {{ row.fuelSurcharge.rate }}</div>
                              <div>计算基数: {{ formatAmount(row.fuelSurcharge.basis) }}</div>
                              <div class="text-primary">总费用: {{ formatAmount(row.fuelSurcharge.amount) }}</div>
                            </td>
                          </tr>
                          <tr class="table-primary">
                            <th>总费用</th>
                            <td><strong>{{ row.formattedTotalAmount }}</strong></td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: `
    .calculator-result {
      margin-top: 20px;
      border: 1px solid #e0e0e0;
      border-radius: 4px;
      padding: 15px;
    }
    
    .result-section {
      margin-bottom: 20px;
    }
    
    .section-title {
      font-size: 16px;
      font-weight: bold;
      color: #333;
      margin-bottom: 10px;
      padding-bottom: 5px;
      border-bottom: 1px solid #eee;
    }
    
    .section-content {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 10px;
    }
    
    .result-item {
      padding: 5px;
      display: flex;
      flex-direction: column;
    }
    
    .item-label {
      color: #666;
      font-size: 14px;
    }
    
    .item-value {
      font-size: 16px;
      font-weight: 500;
      color: #333;
    }
    
    .item-details {
      font-size: 12px;
      color: #666;
      margin-top: 4px;
    }
  `,
  setup() {
    // 初始化样式
    const styleElement = document.createElement('style');
    styleElement.textContent = CalculatorView.styles;
    document.head.appendChild(styleElement);

    const loading = ref(false);
    const products = ref([]);
    const form = ref({
      fromPostalCode: '',
      toPostalCode: '',
      product_id: '',
      weight: null,
      length: null,
      width: null,
      height: null
    });
    const result = ref(null);
    const error = ref('');

    const formatAmount = (amount) => {
      return amount ? `$${Number(amount).toFixed(2)}` : '$0.00';
    };

    const resultRows = computed(() => {
      if (!result.value) return [];
      
      const rows = result.value.allZones ? result.value.results : [result.value];
      console.log('处理的数据:', rows);
      
      return rows.map(row => {
        if (row.isUnauthorized) {
          console.log('不可发包裹数据:', row);
          return {
            zone: row.zone,
            isUnauthorized: true,
            reason: row.reason,
            packageInfo: row.packageInfo,
            fee: row.fee,
            details: row.details,
            formattedTotalAmount: formatAmount(row.fee)
          };
        }
        
        console.log('正常包裹数据:', row);
        return {
          ...row,
          formattedBaseRate: formatAmount(row.baseRate?.amount),
          formattedHandlingFee: {
            amount: formatAmount(row.surchargeDetails?.handlingFee?.amount),
            baseFee: formatAmount(row.surchargeDetails?.handlingFee?.details?.baseFee),
            pssFee: formatAmount(row.surchargeDetails?.handlingFee?.details?.pssFee),
            reason: row.surchargeDetails?.handlingFee?.details?.reason
          },
          formattedOversizeFeeComm: {
            amount: formatAmount(row.surchargeDetails?.oversizeFeeCommercial?.amount),
            baseFee: formatAmount(row.surchargeDetails?.oversizeFeeCommercial?.details?.baseFee),
            pssFee: formatAmount(row.surchargeDetails?.oversizeFeeCommercial?.details?.pssFee),
            reason: row.surchargeDetails?.oversizeFeeCommercial?.details?.reason
          },
          formattedOversizeFeeResi: {
            amount: formatAmount(row.surchargeDetails?.oversizeFeeResidential?.amount),
            baseFee: formatAmount(row.surchargeDetails?.oversizeFeeResidential?.details?.baseFee),
            pssFee: formatAmount(row.surchargeDetails?.oversizeFeeResidential?.details?.pssFee),
            reason: row.surchargeDetails?.oversizeFeeResidential?.details?.reason
          },
          formattedResidentialFee: {
            amount: formatAmount(row.surchargeDetails?.residentialFee?.amount),
            baseFee: formatAmount(row.surchargeDetails?.residentialFee?.details?.baseFee),
            pssFee: formatAmount(row.surchargeDetails?.residentialFee?.details?.pssFee),
            reason: row.surchargeDetails?.residentialFee?.details?.reason
          },
          formattedRemoteFee: {
            amount: formatAmount(row.surchargeDetails?.remoteFee?.amount),
            baseFee: formatAmount(row.surchargeDetails?.remoteFee?.details?.baseFee),
            pssFee: formatAmount(row.surchargeDetails?.remoteFee?.details?.pssFee),
            reason: row.surchargeDetails?.remoteFee?.details?.reason
          },
          fuelSurcharge: {
            amount: row.fuelSurcharge?.amount,
            rate: row.fuelSurcharge?.rate,
            basis: row.fuelSurcharge?.basis
          },
          formattedTotalAmount: formatAmount(row.totalAmount)
        };
      });
    });

    const showError = (message) => {
      error.value = message;
      console.error(message);
    };

    const validatePostalCode = (code) => {
      return /^\d{5}$/.test(code);
    };

    // 添加单位转换函数
    const convertKgToLbs = (kg) => {
      return Math.ceil(kg * 2.20462);
    };

    const convertCmToInch = (cm) => {
      return Math.ceil(cm * 0.393701);
    };

    const validateForm = () => {
      if (!validatePostalCode(form.value.fromPostalCode)) {
        showError('起始邮编格式错误，请输入5位数字');
        return false;
      }
      
      if (form.value.toPostalCode && !validatePostalCode(form.value.toPostalCode)) {
        showError('目的邮编格式错误，请输入5位数字');
        return false;
      }
      
      if (!form.value.weight || form.value.weight <= 0) {
        showError('请输入有效的重量');
        return false;
      }
      
      if (!form.value.length || form.value.length <= 0 ||
          !form.value.width || form.value.width <= 0 ||
          !form.value.height || form.value.height <= 0) {
        showError('请输入有效的包裹尺寸');
        return false;
      }
      
      if (!form.value.product_id) {
        showError('请选择产品');
        return false;
      }
      
      return true;
    };

    const handleCalculate = async () => {
      try {
        if (!validateForm()) return;
        
        loading.value = true;
        result.value = null;
        error.value = '';
        
        const requestData = {
          fromPostalCode: form.value.fromPostalCode,
          toPostalCode: form.value.toPostalCode,
          product_id: form.value.product_id,
          weight: Number(form.value.weight),
          length: Number(form.value.length),
          width: Number(form.value.width),
          height: Number(form.value.height)
        };
        
        console.log('发送请求数据:', requestData);
        
        const response = await window.api.calculator.calculate(requestData);
        console.log('接收响应数据:', response);
        
        if (response && response.success) {
          result.value = response.data;
          console.log('设置结果数据:', result.value);
        } else {
          showError(response?.message || '计算失败');
        }
      } catch (error) {
        console.error('计算出错:', error);
        showError(error.message || '系统错误，请稍后重试');
      } finally {
        loading.value = false;
      }
    };

    const loadProducts = async () => {
      try {
        loading.value = true;
        const response = await window.api.products.list();
        console.log('获取产品列表响应:', response);
        
        if (response && response.success && Array.isArray(response.data)) {
          // 只保留启用状态的产品
          products.value = response.data.filter(product => product.status === 'active');
        } else {
          showError(response?.message || '获取产品列表失败');
        }
      } catch (error) {
        console.error('获取产品列表出错:', error);
        showError(error.message || '获取产品列表失败，请刷新页面重试');
      } finally {
        loading.value = false;
      }
    };

    onMounted(() => {
      loadProducts();
    });

    return {
      loading,
      products,
      form,
      result,
      resultRows,
      error,
      handleCalculate,
      formatAmount
    };
  }
};

window.CalculatorView = CalculatorView; 