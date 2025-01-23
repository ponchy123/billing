// 表单组件
window.Form = {
  name: 'Form',
  props: {
    // 表单配置
    fields: {
      type: Array,
      required: true
    },
    // 表单数据
    modelValue: {
      type: Object,
      required: true
    },
    // 是否显示标签
    showLabel: {
      type: Boolean,
      default: true
    },
    // 标签宽度
    labelWidth: {
      type: String,
      default: '120px'
    },
    // 是否显示必填星号
    showRequiredAsterisk: {
      type: Boolean,
      default: true
    },
    // 是否禁用
    disabled: {
      type: Boolean,
      default: false
    },
    // 是否只读
    readonly: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue', 'submit'],
  setup(props, { emit }) {
    // 表单数据
    const formData = computed({
      get: () => props.modelValue,
      set: (value) => emit('update:modelValue', value)
    })

    // 处理输入
    const handleInput = (field, value) => {
      formData.value = {
        ...formData.value,
        [field.prop]: value
      }
    }

    // 提交表单
    const handleSubmit = (e) => {
      e.preventDefault()
      emit('submit', formData.value)
    }

    return {
      formData,
      handleInput,
      handleSubmit
    }
  },
  template: `
    <form @submit="handleSubmit">
      <div class="row g-3">
        <div v-for="field in fields" :key="field.prop"
          :class="field.colClass || 'col-12'">
          <div class="form-group">
            <label v-if="showLabel" :for="field.prop" class="form-label"
              :style="{ width: labelWidth }">
              {{ field.label }}
              <span v-if="showRequiredAsterisk && field.required" class="text-danger">*</span>
            </label>
            
            <!-- 文本输入框 -->
            <input v-if="field.type === 'text'" type="text"
              :id="field.prop"
              class="form-control"
              :class="{ 'is-invalid': field.error }"
              :value="formData[field.prop]"
              :placeholder="field.placeholder"
              :disabled="disabled || field.disabled"
              :readonly="readonly || field.readonly"
              :required="field.required"
              :minlength="field.minlength"
              :maxlength="field.maxlength"
              :pattern="field.pattern"
              @input="e => handleInput(field, e.target.value)">
            
            <!-- 数字输入框 -->
            <input v-else-if="field.type === 'number'" type="number"
              :id="field.prop"
              class="form-control"
              :class="{ 'is-invalid': field.error }"
              :value="formData[field.prop]"
              :placeholder="field.placeholder"
              :disabled="disabled || field.disabled"
              :readonly="readonly || field.readonly"
              :required="field.required"
              :min="field.min"
              :max="field.max"
              :step="field.step"
              @input="e => handleInput(field, e.target.value)">
            
            <!-- 密码输入框 -->
            <input v-else-if="field.type === 'password'" type="password"
              :id="field.prop"
              class="form-control"
              :class="{ 'is-invalid': field.error }"
              :value="formData[field.prop]"
              :placeholder="field.placeholder"
              :disabled="disabled || field.disabled"
              :readonly="readonly || field.readonly"
              :required="field.required"
              :minlength="field.minlength"
              :maxlength="field.maxlength"
              @input="e => handleInput(field, e.target.value)">
            
            <!-- 文本域 -->
            <textarea v-else-if="field.type === 'textarea'"
              :id="field.prop"
              class="form-control"
              :class="{ 'is-invalid': field.error }"
              :value="formData[field.prop]"
              :placeholder="field.placeholder"
              :disabled="disabled || field.disabled"
              :readonly="readonly || field.readonly"
              :required="field.required"
              :rows="field.rows || 3"
              @input="e => handleInput(field, e.target.value)">
            </textarea>
            
            <!-- 选择框 -->
            <select v-else-if="field.type === 'select'"
              :id="field.prop"
              class="form-select"
              :class="{ 'is-invalid': field.error }"
              :value="formData[field.prop]"
              :disabled="disabled || field.disabled"
              :required="field.required"
              @change="e => handleInput(field, e.target.value)">
              <option value="" disabled selected>{{ field.placeholder }}</option>
              <option v-for="option in field.options" :key="option.value"
                :value="option.value">
                {{ option.label }}
              </option>
            </select>
            
            <!-- 单选框组 -->
            <div v-else-if="field.type === 'radio'" class="d-flex gap-3">
              <div v-for="option in field.options" :key="option.value" class="form-check">
                <input type="radio" class="form-check-input"
                  :id="field.prop + '_' + option.value"
                  :name="field.prop"
                  :value="option.value"
                  :checked="formData[field.prop] === option.value"
                  :disabled="disabled || field.disabled"
                  :required="field.required"
                  @change="e => handleInput(field, option.value)">
                <label class="form-check-label" :for="field.prop + '_' + option.value">
                  {{ option.label }}
                </label>
              </div>
            </div>
            
            <!-- 复选框组 -->
            <div v-else-if="field.type === 'checkbox'" class="d-flex gap-3">
              <div v-for="option in field.options" :key="option.value" class="form-check">
                <input type="checkbox" class="form-check-input"
                  :id="field.prop + '_' + option.value"
                  :value="option.value"
                  :checked="formData[field.prop]?.includes(option.value)"
                  :disabled="disabled || field.disabled"
                  :required="field.required"
                  @change="e => {
                    const values = formData[field.prop] || []
                    const value = option.value
                    const index = values.indexOf(value)
                    if (index === -1) {
                      values.push(value)
                    } else {
                      values.splice(index, 1)
                    }
                    handleInput(field, values)
                  }">
                <label class="form-check-label" :for="field.prop + '_' + option.value">
                  {{ option.label }}
                </label>
              </div>
            </div>
            
            <!-- 开关 -->
            <div v-else-if="field.type === 'switch'" class="form-check form-switch">
              <input type="checkbox" class="form-check-input"
                :id="field.prop"
                :checked="formData[field.prop]"
                :disabled="disabled || field.disabled"
                @change="e => handleInput(field, e.target.checked)">
              <label class="form-check-label" :for="field.prop">
                {{ field.label }}
              </label>
            </div>
            
            <!-- 错误提示 -->
            <div v-if="field.error" class="invalid-feedback">
              {{ field.error }}
            </div>
            
            <!-- 帮助文本 -->
            <div v-if="field.help" class="form-text">
              {{ field.help }}
            </div>
          </div>
        </div>
      </div>
      
      <!-- 表单按钮 -->
      <div class="row mt-4">
        <div class="col-12">
          <slot name="footer">
            <button type="submit" class="btn btn-primary">提交</button>
          </slot>
        </div>
      </div>
    </form>
  `
} 