const ProductEdit = {
  name: 'ProductEdit',
  template: `
    <div v-if="isDataReady" class="container-fluid py-3">
      <div class="card">
        <div class="card-body">
          <form @submit.prevent="handleSubmit">
            <div v-if="error" class="alert alert-danger">{{ error }}</div>
            
            <!-- 基本信息 -->
            <div class="row mb-3">
              <div class="col-md-6">
                <div class="mb-3">
                  <label class="form-label">产品名称</label>
                  <input type="text" class="form-control" v-model="formData.product">
                </div>
                <div class="mb-3">
                  <label class="form-label">承运商</label>
                  <input type="text" class="form-control" v-model="formData.carrier">
                </div>
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="form-label">重量单位</label>
                    <input type="text" class="form-control" v-model="formData.unit">
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">体积重量因子(DIM)</label>
                    <input type="number" class="form-control" v-model="formData.dim">
                  </div>
                </div>
              </div>
              <div class="col-md-6">
                <div class="mb-3">
                  <div class="form-check">
                    <input type="checkbox" class="form-check-input" v-model="isActive">
                    <label class="form-check-label">启用</label>
                  </div>
                </div>
                <div class="mb-3">
                  <label class="form-label">开始时间</label>
                  <input type="date" class="form-control" v-model="formData.start_date" 
                         :required="formData.status === 'active'">
                </div>
                <div class="mb-3">
                  <label class="form-label">结束时间</label>
                  <input type="date" class="form-control" v-model="formData.end_date">
                </div>
              </div>
            </div>

            <!-- 区域费率表 -->
            <div class="card mb-3">
              <div class="card-header">
                <h5 class="mb-0">区域费率</h5>
              </div>
              <div class="card-body">
                <div class="table-responsive">
                  <table class="table table-bordered table-hover">
                    <thead>
                      <tr>
                        <th>重量(磅)</th>
                        <th v-for="zone in formData.zones" :key="zone">
                          Zone{{ zone }}
                          <button v-if="formData.zones.length > 1" type="button" class="btn btn-sm btn-danger ms-2" @click="removeZone(zone)">
                            <i class="bi bi-x"></i>
                          </button>
                        </th>
                        <th>操作</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(rate, index) in zoneRates" :key="index">
                        <td>
                          <input type="number" class="form-control form-control-sm" v-model="rate.weight">
                        </td>
                        <td v-for="zone in formData.zones" :key="zone">
                          <div class="input-group input-group-sm">
                            <span class="input-group-text">$</span>
                            <input type="number" class="form-control form-control-sm" 
                                   v-model="rate['Zone' + zone]"
                                   step="0.01" min="0">
                          </div>
                        </td>
                        <td>
                          <button type="button" class="btn btn-sm btn-danger" @click="removeRate(index)">删除</button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                  <div class="mt-2">
                    <button type="button" class="btn btn-sm btn-primary me-2" @click="addRate">添加费率</button>
                    <button type="button" class="btn btn-sm btn-primary" @click="addZone">添加Zone</button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 附加费用 -->
            <div v-if="surchargeCategories && surchargeCategories.length" class="card mb-3">
              <div class="card-header">
                <h5 class="mb-0">附加费用</h5>
              </div>
              <div class="card-body">
                <div v-for="(category, categoryIndex) in surchargeCategories" :key="categoryIndex" class="mb-4">
                  <div class="d-flex justify-content-between align-items-center mb-2">
                    <h6 class="mb-0">{{category.title}}</h6>
                    <div class="form-check" v-if="category.not_applicable !== undefined">
                      <input type="checkbox" class="form-check-input" v-model="category.not_applicable">
                      <label class="form-check-label">不叠加收费</label>
                    </div>
                  </div>

                  <!-- 类别级别的 PSS 时间段 -->
                  <div v-if="category.pss_periods && category.pss_periods.length > 0" class="mb-3">
                    <h6 class="small mb-2">PSS时间段</h6>
                    <table class="table table-bordered table-sm">
                      <thead>
                        <tr>
                          <th>开始日期</th>
                          <th>结束日期</th>
                          <th>金额</th>
                          <th>操作</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(period, periodIndex) in category.pss_periods" :key="periodIndex">
                          <td>
                            <input type="date" class="form-control form-control-sm" v-model="period.start_date">
                          </td>
                          <td>
                            <input type="date" class="form-control form-control-sm" v-model="period.end_date">
                          </td>
                          <td>
                            <div class="input-group input-group-sm">
                              <span class="input-group-text">$</span>
                              <input type="number" class="form-control form-control-sm" v-model="period.amount" step="0.01" min="0">
                            </div>
                          </td>
                          <td>
                            <button type="button" class="btn btn-danger btn-sm" @click="removePssPeriod(categoryIndex, periodIndex)">删除</button>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                    <button type="button" class="btn btn-primary btn-sm mt-2" @click="addPssPeriod(categoryIndex)">添加PSS时间段</button>
                  </div>

                  <!-- 费用项表格 -->
                  <div class="table-responsive">
                    <table class="table table-bordered">
                      <thead>
                        <tr>
                          <th>费用项</th>
                          <th v-for="header in getTableHeaders(category)" :key="header">{{header}}</th>
                        </tr>
                      </thead>
                      <tbody>
                        <template v-for="(item, itemIndex) in category.items" :key="itemIndex">
                          <!-- 主项目 -->
                          <tr>
                            <td>
                              <div>{{item.name}}</div>
                              <div v-if="item.description" class="small text-muted">{{item.description}}</div>
                              
                              <!-- 项目级别的 PSS 时间段 -->
                              <div v-if="item.pss_periods && item.pss_periods.length > 0" class="mt-2">
                                <h6 class="small mb-2">PSS时间段</h6>
                                <table class="table table-bordered table-sm">
                                  <thead>
                                    <tr>
                                      <th>开始日期</th>
                                      <th>结束日期</th>
                                      <th>金额</th>
                                      <th>操作</th>
                                    </tr>
                                  </thead>
                                  <tbody>
                                    <tr v-for="(period, periodIndex) in item.pss_periods" :key="periodIndex">
                                      <td>
                                        <input type="date" class="form-control form-control-sm" v-model="period.start_date">
                                      </td>
                                      <td>
                                        <input type="date" class="form-control form-control-sm" v-model="period.end_date">
                                      </td>
                                      <td>
                                        <div class="input-group input-group-sm">
                                          <span class="input-group-text">$</span>
                                          <input type="number" class="form-control form-control-sm" v-model="period.amount" step="0.01" min="0">
                                        </div>
                                      </td>
                                      <td>
                                        <button type="button" class="btn btn-danger btn-sm" @click="removePssPeriod(categoryIndex, periodIndex, itemIndex)">删除</button>
                                      </td>
                                    </tr>
                                  </tbody>
                                </table>
                                <button type="button" class="btn btn-primary btn-sm mt-2" @click="addPssPeriod(categoryIndex, itemIndex)">添加PSS时间段</button>
                              </div>
                            </td>
                            <template v-if="isSingleFeeCategory(category)">
                              <td>
                                <div class="input-group input-group-sm">
                                  <span class="input-group-text">$</span>
                                  <input type="number" class="form-control form-control-sm" 
                                         v-model="item.fees[2]" 
                                         @input="ensureFees(item)"
                                         step="0.01" min="0">
                                </div>
                              </td>
                            </template>
                            <template v-else>
                              <td v-for="zone in formData.zones" :key="zone">
                                <div class="input-group input-group-sm">
                                  <span class="input-group-text">$</span>
                                  <input type="number" class="form-control form-control-sm" 
                                         v-model="item.fees[zone]"
                                         @input="ensureFees(item, zone)"
                                         step="0.01" min="0">
                                </div>
                              </td>
                            </template>
                          </tr>

                          <!-- 子项目 -->
                          <template v-if="item.items">
                            <tr v-for="(subItem, subIndex) in item.items" :key="subIndex" class="table-light">
                              <td class="ps-4">
                                <div>{{subItem.name}}</div>
                                <div v-if="subItem.description" class="small text-muted">{{subItem.description}}</div>
                                
                                <!-- 子项目的 PSS 时间段 -->
                                <div v-if="subItem.pss_periods && subItem.pss_periods.length > 0" class="mt-2">
                                  <h6 class="small mb-2">PSS时间段</h6>
                                  <table class="table table-bordered table-sm">
                                    <thead>
                                      <tr>
                                        <th>开始日期</th>
                                        <th>结束日期</th>
                                        <th>金额</th>
                                        <th>操作</th>
                                      </tr>
                                    </thead>
                                    <tbody>
                                      <tr v-for="(period, periodIndex) in subItem.pss_periods" :key="periodIndex">
                                        <td>
                                          <input type="date" class="form-control form-control-sm" v-model="period.start_date">
                                        </td>
                                        <td>
                                          <input type="date" class="form-control form-control-sm" v-model="period.end_date">
                                        </td>
                                        <td>
                                          <div class="input-group input-group-sm">
                                            <span class="input-group-text">$</span>
                                            <input type="number" class="form-control form-control-sm" v-model="period.amount" step="0.01" min="0">
                                          </div>
                                        </td>
                                        <td>
                                          <button type="button" class="btn btn-danger btn-sm" @click="removePssPeriod(categoryIndex, periodIndex, itemIndex, subIndex)">删除</button>
                                        </td>
                                      </tr>
                                    </tbody>
                                  </table>
                                  <button type="button" class="btn btn-primary btn-sm mt-2" @click="addPssPeriod(categoryIndex, itemIndex, subIndex)">添加PSS时间段</button>
                                </div>
                              </td>
                              <template v-if="isSingleFeeCategory(category)">
                                <td>
                                  <div class="input-group input-group-sm">
                                    <span class="input-group-text">$</span>
                                    <input type="number" class="form-control form-control-sm" 
                                           v-model="subItem.fees[2]" 
                                           @input="ensureFees(subItem)"
                                           step="0.01" min="0">
                                  </div>
                                </td>
                              </template>
                              <template v-else>
                                <td v-for="zone in formData.zones" :key="zone">
                                  <div class="input-group input-group-sm">
                                    <span class="input-group-text">$</span>
                                    <input type="number" class="form-control form-control-sm" 
                                           v-model="subItem.fees[zone]"
                                           @input="ensureFees(subItem, zone)"
                                           step="0.01" min="0">
                                  </div>
                                </td>
                              </template>
                            </tr>
                          </template>
                        </template>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>

            <!-- 按钮组 -->
            <div class="d-flex justify-content-end">
              <button type="submit" class="btn btn-primary" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-1"></span>
                保存
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    <div v-else-if="loading" class="d-flex justify-content-center py-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">加载中...</span>
      </div>
    </div>
  `,
  setup() {
    const route = VueRouter.useRoute();
    const router = VueRouter.useRouter();
    const loading = Vue.ref(true);
    const error = Vue.ref(null);
    const zoneRates = Vue.ref([]);
    const surchargeCategories = Vue.ref([]);
    const formData = Vue.ref({
      carrier: '',
      product: '',
      currency: '',
      unit: '',
      dim: '',
      status: 'active',
      start_date: '',
      end_date: '',
      zones: [1,2,3,4,5,6,7,8]
    });

    const isDataReady = Vue.ref(false);
    const { watch, onMounted, onBeforeUnmount } = Vue;

    // 在组件卸载前清理状态
    onBeforeUnmount(() => {
      console.log('Component unmounting, cleaning up...');
      // 停止所有的 watch
      if (stopWatchZoneRates) stopWatchZoneRates();
      if (stopWatchSurcharges) stopWatchSurcharges();
      if (stopWatchStatus) stopWatchStatus();
      
      // 清理响应式引用
      loading.value = false;
      error.value = null;
      zoneRates.value = [];
      surchargeCategories.value = [];
      formData.value = {
        carrier: '',
        product: '',
        currency: '',
        unit: '',
        dim: '',
        status: 'active',
        start_date: '',
        end_date: '',
        zones: [1,2,3,4,5,6,7,8]
      };
      isDataReady.value = false;
    });

    // 监听区域费率变化
    const stopWatchZoneRates = watch(zoneRates, (newRates) => {
      if (!newRates) return;
      newRates.forEach(rate => {
        if (!rate) return;
        Object.keys(rate).forEach(zone => {
          if (rate[zone] && zone !== 'weight') {
            rate[zone] = formatNumber(rate[zone]);
          }
        });
      });
    }, { deep: true });

    // 监听附加费用变化
    const stopWatchSurcharges = watch(surchargeCategories, (newCategories) => {
      if (!newCategories) return;
      newCategories.forEach(category => {
        if (!category) return;
        if (category.items) {
          category.items.forEach(item => {
            if (!item) return;
            if (item.fees) {
              Object.keys(item.fees).forEach(zone => {
                item.fees[zone] = formatNumber(item.fees[zone]);
              });
            }
          });
        }
      });
    }, { deep: true });

    // 监听状态变化
    const stopWatchStatus = watch(() => formData.value?.status, (newStatus) => {
      if (newStatus !== undefined) {
        console.log('Status changed:', newStatus);
      }
    });

    // 组件挂载时加载数据
    onMounted(() => {
      console.log('Component mounted');
      if (route.params.id) {
        loadProduct();
      }
    });

    // 初始化附加费用数据
    const defaultSurcharges = [
      {
        title: '1. 额外处理费(Additional Handling Surcharge)',
        not_applicable: true,
        pss_periods: [
          {
            start_date: '2024-11-25',
            end_date: '2024-12-29',
            amount: 5.88
          },
          {
            start_date: '2024-12-30',
            end_date: '2025-01-19',
            amount: 4.68
          }
        ],
        items: [
          {
            name: 'a)额外处理费A-weight: 50磅＜实际重量＜150磅',
            fees: {2: 2.00, 3: 8.49, 4: 8.49, 5: 8.96, 6: 8.96, 7: 9.66, 8: 9.66}
          },
          {
            name: 'b)额外处理费B-length: 48英寸＜最长边 ≤96英寸',
            fees: {2: 5.42, 3: 5.88, 4: 5.88, 5: 6.35, 6: 6.35, 7: 6.99, 8: 6.99}
          },
          {
            name: 'c)额外处理费C-length+girth: 105英寸＜长+周长[2*(宽+高)]≤130英寸',
            fees: {2: 5.42, 3: 5.88, 4: 5.88, 5: 6.35, 6: 6.35, 7: 6.99, 8: 6.99}
          },
          {
            name: 'd)额外处理费D-width: 第二长边＞30英寸',
            fees: {2: 5.42, 3: 5.88, 4: 5.88, 5: 6.35, 6: 6.35, 7: 6.99, 8: 6.99}
          },
          {
            name: 'e)其它额外处理费-packaging: 包裹未进行任何包装或者包装材质为缠绕膜、金属、木材、布料、皮革、充气袋等',
            fees: {2: 4.94, 3: 5.57, 4: 5.57, 5: 5.80, 6: 5.80, 7: 5.97, 8: 5.97}
          }
        ]
      },
      {
        title: '2. 超大超尺寸费(Oversize-商业地址)',
        not_applicable: true,
        pss_periods: [
          {
            start_date: '2024-11-25',
            end_date: '2024-12-29',
            amount: 54.82
          },
          {
            start_date: '2024-12-30',
            end_date: '2025-01-19',
            amount: 46.48
          }
        ],
        items: [
          {
            name: 'a)实际重量＜150磅，且130英寸＜长+[2*(宽+高)]≤165英寸',
            fees: {2: 37.29, 3: 40.43, 4: 40.43, 5: 42.80, 6: 42.80, 7: 45.96, 8: 45.96},
            start_date: '2024-11-25',
            end_date: '2024-12-29',
            pss: 54.82
          },
          {
            name: 'b)实际重量＜150磅，且96英寸＜最长边≤108英寸',
            fees: {2: 37.29, 3: 40.43, 4: 40.43, 5: 42.80, 6: 42.80, 7: 45.96, 8: 45.96},
            start_date: '2024-12-30',
            end_date: '2025-01-19',
            pss: 46.48
          },
          {
            name: 'c)尺寸符合oversize条款的计费重量时，不足90磅按90磅计',
            fees: {2: 37.29, 3: 40.43, 4: 40.43, 5: 42.80, 6: 42.80, 7: 45.96, 8: 45.96}
          }
        ]
      },
      {
        title: '3. 超大超尺寸费(Oversize-住宅地址)',
        not_applicable: true,
        pss_periods: [
          {
            start_date: '2024-11-25',
            end_date: '2024-12-29',
            amount: 54.82
          },
          {
            start_date: '2024-12-30',
            end_date: '2025-01-19',
            amount: 46.48
          }
        ],
        items: [
          {
            name: 'a)实际重量＜150磅，且130英寸＜长+[2*(宽+高)]≤165英寸',
            fees: {2: 42.80, 3: 45.96, 4: 45.96, 5: 50.68, 6: 50.68, 7: 53.04, 8: 53.04},
            start_date: '2024-11-25',
            end_date: '2024-12-29',
            pss: 54.82
          },
          {
            name: 'b)实际重量＜150磅，且96英寸＜最长边≤108英寸',
            fees: {2: 42.80, 3: 45.96, 4: 45.96, 5: 50.68, 6: 50.68, 7: 53.04, 8: 53.04},
            start_date: '2024-12-30',
            end_date: '2025-01-19',
            pss: 46.48
          },
          {
            name: 'c)尺寸符合oversize条款的计费重量时，不足90磅按90磅计',
            fees: {2: 42.80, 3: 45.96, 4: 45.96, 5: 50.68, 6: 50.68, 7: 53.04, 8: 53.04}
          }
        ]
      },
      {
        title: '4. 住宅地址附加费(Residential Surcharge)',
        not_applicable: false,
        pss_periods: [
          {
            start_date: '2024-11-25',
            end_date: '2024-12-29',
            amount: 1.90
          },
          {
            start_date: '2024-12-30',
            end_date: '2025-01-19',
            amount: 1.75
          }
        ],
        items: [
          {
            name: 'FedEx Home Delivery',
            fees: {2: 2.87}
          },
          {
            name: 'FedEx Commercial Ground',
            fees: {2: 6.45},
            description: '如果产品超过70磅，将由Ground服务派送至住宅地址，而非Home服务'
          }
        ]
      },
      {
        title: '5. 偏远地区附加费(Delivery Area Surcharge)',
        not_applicable: true,
        pss_periods: [
          {
            start_date: '2024-11-25',
            end_date: '2024-12-29',
            amount: 2.12
          },
          {
            start_date: '2024-12-30',
            end_date: '2025-01-19',
            amount: 2.52
          }
        ],
        items: [
          {
            name: 'Commercial(FedEx Ground)',
            fees: {2: 2.12}
          },
          {
            name: 'Extended Commercial(FedEx Ground)',
            fees: {2: 2.52}
          },
          {
            name: 'Residential (FedEx Ground)',
            fees: {2: 6.70}
          },
          {
            name: 'Extended Residential (FedEx Ground)',
            fees: {2: 8.80}
          },
          {
            name: 'Residential (FedEx Home Delivery)',
            fees: {2: 2.88}
          },
          {
            name: 'Extended Residential (FedEx Home Delivery)',
            fees: {2: 3.70}
          },
          {
            name: '远端地带-DAS Remote Comm(FedEx Ground)',
            fees: {2: 6.47}
          },
          {
            name: '远端地带-DAS Remote Resi (FedEx Ground)',
            fees: {2: 16.00}
          },
          {
            name: '远端地带-DAS Remote Resi (FedEx Home Delivery)',
            fees: {2: 6.47}
          }
        ]
      },
      {
        title: '增值服务费项目',
        not_applicable: true,
        items: [
          {
            name: '1. 地址校验更改费',
            items: [
              {
                name: 'a)FedEx主动修改地址(Address Correction)',
                fees: {2: 27.00},
                description: '地址填写错误，FedEx修改地址，以账单为准'
              },
              {
                name: 'b)收件人/发件人主动修改(Delivery intercept)',
                fees: {2: 29.90},
                description: '收件人/发件人修改，包含修改地址、派送时间等'
              }
            ]
          },
          {
            name: '2. 签名签收',
            items: [
              {
                name: 'Indirect Signature Required',
                fees: {2: 0.00}
              },
              {
                name: 'Direct Signature Required',
                fees: {2: 8.80}
              },
              {
                name: 'Adult Signature Required',
                fees: {2: 9.90}
              }
            ]
          },
          {
            name: '3. 运费复合费(Shipping Charge Correction)',
            fees: {2: 1.00}
          },
          {
            name: '4. 原件退回',
            fees: {2: 1.00},
            description: '预报重量与尺寸与实际不符时，按USD 1.00每件或该件运费的6%, 两者的最大值收取'
          },
          {
            name: '5. 不可发包裹(Unauthorized)',
            description: '同一包裹符合任一条件，此类包裹不可发；若向Fedex交付符合不可发条件的包裹，附加费为每件收費，且可能被拒收',
            items: [
              {
                name: 'a)实重＞150磅',
                fees: {2: 1325.00}
              },
              {
                name: 'b)最长边＞108英寸',
                fees: {2: 1325.00}
              },
              {
                name: 'c)最长边+周长＞165英寸',
                fees: {2: 1325.00}
              }
            ],
            pss_periods: [
              {
                start_date: '2024-11-25',
                end_date: '2024-12-29',
                amount: 525.00
              },
              {
                start_date: '2024-12-30',
                end_date: '2025-01-19',
                amount: 475.00
              }
            ]
          }
        ]
      }
    ];

    // 生成费用对象
    function generateFeesObject(zones, defaultValue = 0) {
      const fees = {};
      for (let i = 0; i < zones.length; i++) {
        fees[zones[i]] = defaultValue;
      }
      return fees;
    }

    // 添加区域费率行
    const addZoneRate = () => {
      const newRate = {
        weight: zoneRates.value.length + 1
      };
      formData.value.zones.forEach(zone => {
        newRate[`Zone${zone}`] = 0;  // 默认值为0
      });
      zoneRates.value.push(newRate);
    };

    // 删除区域费率行
    const removeZoneRate = (index) => {
      if (index >= 0 && index < zoneRates.value.length) {
        zoneRates.value.splice(index, 1);
        // 重新计算权重
        zoneRates.value.forEach((rate, idx) => {
          rate.weight = idx + 1;
        });
      }
    };

    // 添加费用项
    const addSurchargeItem = (categoryIndex, parentItemIndex = null) => {
      if (categoryIndex >= 0 && categoryIndex < surchargeCategories.value.length) {
        const category = surchargeCategories.value[categoryIndex];
        let newItem = {
          name: '',
          fees: { 2: 0 }
        };
        
        // 如果不是单费用类别，添加其他区域的费用
        if (!isSingleFeeCategory(category)) {
          newItem.fees = {
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
            7: 0,
            8: 0
          };
        }

        // 如果是添加子项目
        if (parentItemIndex !== null && category.items[parentItemIndex]) {
          if (!category.items[parentItemIndex].items) {
            category.items[parentItemIndex].items = [];
          }
          category.items[parentItemIndex].items.push(newItem);
        } else {
          // 添加主项目
          if (!category.items) {
            category.items = [];
          }
          category.items.push(newItem);
        }
      }
    };

    // 删除费用项
    const removeSurchargeItem = (categoryIndex, itemIndex, parentItemIndex = null) => {
      if (categoryIndex >= 0 && categoryIndex < surchargeCategories.value.length) {
        const category = surchargeCategories.value[categoryIndex];
        if (parentItemIndex !== null && category.items[parentItemIndex]) {
          // 删除子项目
          if (category.items[parentItemIndex].items) {
            category.items[parentItemIndex].items.splice(itemIndex, 1);
          }
        } else {
          // 删除主项目
          category.items.splice(itemIndex, 1);
        }
      }
    };

    // 日期格式转换方法
    const formatDate = (date) => {
      if (!date) return '';
      // 处理带有时间的日期格式
      if (date.includes('T')) {
        date = date.split('T')[0];
      }
      if (date.includes('-')) {
        const [year, month, day] = date.split('-');
        return `${year}/${month}/${day}`;
      }
      return date;
    };

    const parseDate = (date) => {
      if (!date) return '';
      // 处理带有时间的日期格式
      if (date.includes('T')) {
        date = date.split('T')[0];
      }
      if (date.includes('/')) {
        const [year, month, day] = date.split('/');
        const formattedMonth = month.padStart(2, '0');
        const formattedDay = day.padStart(2, '0');
        return `${year}-${formattedMonth}-${formattedDay}`;
      }
      return date;
    };

    // 确保费用对象存在
    const ensureFees = (item, zone) => {
      if (!item.fees) {
        item.fees = {};
      }
      if (zone) {
        if (!item.fees[zone]) {
          item.fees[zone] = 0;
        }
      } else {
        if (!item.fees[2]) {
          item.fees[2] = 0;
        }
      }
    };

    // 初始化费用对象
    const initializeFees = (item) => {
      if (!item.fees) {
        item.fees = {};
      }
      // 如果是单费用项，只初始化 zone 2
      if (Object.keys(item.fees).length === 1) {
        item.fees[2] = item.fees[2] || 0;
      } else {
        // 否则初始化所有区域
        formData.value.zones.forEach(zone => {
          if (!item.fees[zone]) {
            item.fees[zone] = 0;
          }
        });
      }
    };

    // 加载产品数据
    const loadProduct = async () => {
      try {
        console.log('Loading product data...');
        loading.value = true;
        error.value = null;
        
        const response = await fetch(`/api/products/${route.params.id}`);
        console.log('API response:', response);
        
        if (!response.ok) {
          throw new Error('加载产品数据失败');
        }

        const data = await response.json();
        console.log('Product data from API:', data);
        
        // 设置基本信息
        formData.value = {
          product: data.name || '',
          carrier: data.carrier || '',
          currency: data.currency ?? '',
          unit: data.unit ?? '',
          dim: data.volume_weight_factor || '250',
          status: data.status || 'inactive',  // 使用原始状态值
          start_date: parseDate(data.start_date) ?? '',
          end_date: parseDate(data.end_date) ?? '',
          zones: data.zones ?? [2,3,4,5,6,7,8]
        };

        // 确保状态正确设置
        console.log('Raw status from API:', data.status);
        console.log('Processed status:', formData.value.status);
        console.log('isActive computed value:', isActive.value);

        // 初始化区域费率数据
        if (data.zone_rates) {
          console.log('Setting zone rates from data:', data.zone_rates);
          try {
            const parsedRates = typeof data.zone_rates === 'string' 
              ? JSON.parse(data.zone_rates) 
              : data.zone_rates;
            
            if (Array.isArray(parsedRates)) {
              zoneRates.value = parsedRates.map((rate, index) => {
                const fees = {};
                formData.value.zones.forEach(zone => {
                  fees[`Zone${zone}`] = rate[`Zone${zone}`] || rate[zone] || 0;
                });
                return {
                  weight: rate.weight || (index + 1),  // 确保重量从1开始
                  ...fees
                };
              });
              console.log('Zone rates initialized successfully:', zoneRates.value);
            } else {
              console.error('Invalid zone rates format:', parsedRates);
              throw new Error('费率数据格式不正确');
            }
          } catch (err) {
            console.error('Error parsing zone rates:', err);
            initializeDefaultRates();
          }
        } else {
          console.log('No zone rates data found, initializing empty rates');
          initializeDefaultRates();
        }
        console.log('Zone rates initialization completed:', zoneRates.value.length);

        // 初始化附加费用数据
        surchargeCategories.value = JSON.parse(JSON.stringify(defaultSurcharges));
        if (data.surcharges) {
          try {
            const parsedSurcharges = typeof data.surcharges === 'string' 
              ? JSON.parse(data.surcharges) 
              : data.surcharges;

            if (parsedSurcharges && Array.isArray(parsedSurcharges) && parsedSurcharges.length > 0) {
              // 确保每个类别都有正确的费用结构
              parsedSurcharges.forEach(category => {
                if (category.items) {
                  category.items = category.items.map(item => {
                    if (!item.fees) {
                      item.fees = isSingleFeeCategory(category) ? { 2: 0 } : 
                        formData.value.zones.reduce((acc, zone) => {
                          acc[zone] = 0;
                          return acc;
                        }, {});
                    }
                    return item;
                  });
                }
              });
              surchargeCategories.value = parsedSurcharges;
            }
          } catch (e) {
            console.error('解析附加费用数据失败:', e);
            // 如果解析失败，使用默认值
            surchargeCategories.value = JSON.parse(JSON.stringify(defaultSurcharges));
          }
        }
        
        // 确保所有费用项都有正确的费用结构
        surchargeCategories.value.forEach(category => {
          if (category.items) {
            category.items.forEach(item => {
              if (!item.fees) {
                item.fees = isSingleFeeCategory(category) ? { 2: 0 } : 
                  formData.value.zones.reduce((acc, zone) => {
                    acc[zone] = 0;
                    return acc;
                  }, {});
              }
            });
          }
        });

        isDataReady.value = true;
        console.log('Data ready set to true');
      } catch (err) {
        error.value = err.message;
        console.error('Loading failed:', err);
        // 如果加载失败，也初始化默认值
        initializeDefaultRates();
      } finally {
        loading.value = false;
        console.log('Loading completed');
      }
    };

    // 初始化默认费率
    const initializeDefaultRates = () => {
      zoneRates.value = [];
      for(let i = 1; i <= 38; i++) {  // 从1开始
        const rate = {
          weight: i
        };
        formData.value.zones.forEach(zone => {
          rate[`Zone${zone}`] = 0;  // 默认值为0
        });
        zoneRates.value.push(rate);
      }
    };

    // 提交表单
    const handleSubmit = async () => {
      try {
        loading.value = true;
        error.value = null;
        
        // 根据 isActive 设置状态
        formData.value.status = isActive.value ? 'active' : 'inactive';
        console.log('Submitting status:', formData.value.status);

        if (formData.value.status === 'active' && !formData.value.start_date) {
          throw new Error('启用状态下必须设置开始有效期');
        }

        // 验证区域费率数据
        const validZoneRates = zoneRates.value.filter(rate => rate.weight != null);
        if (validZoneRates.length === 0) {
          throw new Error('请至少添加一条区域费率数据');
        }

        // 确保 dim 字段有有效值
        if (!formData.value.dim) {
          formData.value.dim = '250';
        }

        // 转换区域费率数据格式
        const formattedZoneRates = validZoneRates.map(rate => {
          const formattedRate = { weight: parseFloat(rate.weight) };
          formData.value.zones.forEach(zone => {
            const zoneValue = parseFloat(rate[`Zone${zone}`] || 0);
            // 同时保存三种可能的键名格式
            formattedRate[`Zone${zone}`] = zoneValue;
            formattedRate[zone] = zoneValue;
            formattedRate[zone.toString()] = zoneValue;
          });
          console.log('Formatted rate:', formattedRate);
          return formattedRate;
        });

        const submitData = {
          name: formData.value.product,
          carrier: formData.value.carrier,
          unit: formData.value.unit,
          volume_weight_factor: formData.value.dim,
          status: isActive.value ? 'active' : 'inactive',
          start_date: formatDate(formData.value.start_date),
          end_date: formatDate(formData.value.end_date),
          zone_rates: formattedZoneRates,
          surcharges: surchargeCategories.value
        };

        console.log('Submitting zone rates:', JSON.stringify(formattedZoneRates));

        const response = await fetch(`/api/products/${route.params.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(submitData)
        });

        if (!response.ok) {
          const responseData = await response.json();
          throw new Error(responseData.message || '保存失败');
        }

        // 保存成功后直接跳转
        router.push('/admin/products');
      } catch (err) {
        error.value = err.message;
        console.error('保存失败:', err);
        alert('保存失败: ' + err.message);
      } finally {
        loading.value = false;
      }
    };

    // 添加数字格式化方法
    const formatNumber = (value) => {
      if (value) {
        const num = parseFloat(value);
        return !isNaN(num) ? num.toFixed(2) : '0.00';
      }
      return '0.00';
    };

    // 添加PSS相关方法
    const addPssPeriod = (categoryIndex, itemIndex = null) => {
      if (categoryIndex >= 0 && categoryIndex < surchargeCategories.value.length) {
        const category = surchargeCategories.value[categoryIndex];
        const newPeriod = {
          start_date: '',
          end_date: '',
          amount: 0
        };

        if (itemIndex !== null) {
          // 添加到特定项目
          if (category.items && category.items[itemIndex]) {
            if (!category.items[itemIndex].pss_periods) {
              category.items[itemIndex].pss_periods = [];
            }
            category.items[itemIndex].pss_periods.push(newPeriod);
          }
        } else {
          // 添加到类别
          if (!category.pss_periods) {
            category.pss_periods = [];
          }
          category.pss_periods.push(newPeriod);
        }
      }
    };

    const removePssPeriod = (categoryIndex, periodIndex, itemIndex = null) => {
      if (categoryIndex >= 0 && categoryIndex < surchargeCategories.value.length) {
        const category = surchargeCategories.value[categoryIndex];
        
        if (itemIndex !== null) {
          // 从特定项目中删除
          if (category.items && 
              category.items[itemIndex] && 
              category.items[itemIndex].pss_periods && 
              periodIndex >= 0 && 
              periodIndex < category.items[itemIndex].pss_periods.length) {
            category.items[itemIndex].pss_periods.splice(periodIndex, 1);
          }
        } else {
          // 从类别中删除
          if (category.pss_periods && 
              periodIndex >= 0 && 
              periodIndex < category.pss_periods.length) {
            category.pss_periods.splice(periodIndex, 1);
          }
        }
      }
    };

    // 判断是否显示PSS时间段
    const shouldShowPssPeriods = (category, item = null) => {
      if (item) {
        return item.pss_periods && item.pss_periods.length > 0;
      }
      return category && category.pss_periods && category.pss_periods.length > 0;
    };

    // 判断是否是单费用类别
    function isSingleFeeCategory(category) {
      return category && (
        category.title.includes('住宅地址附加费') || 
        category.title.includes('偏远地区附加费') ||
        category.title.includes('增值服务费项目')
      );
    }

    // 获取表头
    const getTableHeaders = (category) => {
      if (isSingleFeeCategory(category)) {
        return ['费用'];
      }
      return formData.value.zones.map(zone => `Zone${zone}`);
    };

    const isActive = Vue.computed({
      get: () => {
        const status = formData.value.status;
        console.log('Getting isActive, current status:', status);
        return status === 'active';
      },
      set: (val) => {
        console.log('Setting isActive to:', val);
        formData.value.status = val ? 'active' : 'inactive';
        console.log('New status:', formData.value.status);
      }
    });

    // 添加区域（Zone）
    const addZone = () => {
      const nextZone = Math.max(...formData.value.zones) + 1;
      formData.value.zones.push(nextZone);
      // 为所有现有费率添加新的zone
      zoneRates.value.forEach(rate => {
        rate[`Zone${nextZone}`] = 0;  // 新zone的默认值为0
      });
    };

    // 删除区域（Zone）
    const removeZone = (zone) => {
      const index = formData.value.zones.indexOf(zone);
      if (index > -1) {
        formData.value.zones.splice(index, 1);
        // 从所有费率中删除该zone
        zoneRates.value.forEach(rate => {
          delete rate[`Zone${zone}`];
        });
      }
    };

    return {
      loading,
      error,
      formData,
      zoneRates,
      surchargeCategories,
      isDataReady,
      handleSubmit,
      addRate: addZoneRate,
      removeRate: removeZoneRate,
      addZone,
      removeZone,
      isActive,
      getTableHeaders,
      isSingleFeeCategory,
      addPssPeriod,
      removePssPeriod,
      ensureFees,
      initializeFees,
      shouldShowPssPeriods
    };
  }
};

// 导出组件
window.ProductEdit = ProductEdit;
