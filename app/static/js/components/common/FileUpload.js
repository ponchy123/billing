// 文件上传组件
window.FileUpload = {
  name: 'FileUpload',
  props: {
    // 上传地址
    action: {
      type: String,
      required: true
    },
    // 文件类型限制
    accept: {
      type: String,
      default: '*'
    },
    // 是否多选
    multiple: {
      type: Boolean,
      default: false
    },
    // 文件大小限制(MB)
    maxSize: {
      type: Number,
      default: 10
    },
    // 是否自动上传
    autoUpload: {
      type: Boolean,
      default: true
    },
    // 上传时附带的额外参数
    data: {
      type: Object,
      default: () => ({})
    },
    // 上传请求的header
    headers: {
      type: Object,
      default: () => ({})
    },
    // 是否显示文件列表
    showFileList: {
      type: Boolean,
      default: true
    },
    // 是否禁用
    disabled: {
      type: Boolean,
      default: false
    }
  },
  emits: ['success', 'error', 'progress', 'change'],
  setup(props, { emit }) {
    const fileList = ref([])
    const uploading = ref(false)
    const uploadProgress = ref(0)

    // 处理文件选择
    const handleFileSelect = (e) => {
      const files = Array.from(e.target.files)
      if (!files.length) return

      // 验证文件
      const validFiles = files.filter(file => {
        // 验证大小
        if (file.size > props.maxSize * 1024 * 1024) {
          window.alert(`文件 ${file.name} 超过大小限制 ${props.maxSize}MB`)
          return false
        }
        return true
      })

      if (!validFiles.length) return

      // 添加到文件列表
      validFiles.forEach(file => {
        fileList.value.push({
          id: Date.now() + Math.random(),
          name: file.name,
          size: file.size,
          status: 'ready',
          progress: 0,
          file
        })
      })

      emit('change', fileList.value)

      // 自动上传
      if (props.autoUpload) {
        upload()
      }

      // 清空input
      e.target.value = ''
    }

    // 上传文件
    const upload = async () => {
      if (uploading.value) return
      if (!fileList.value.length) return

      uploading.value = true
      uploadProgress.value = 0

      try {
        for (const file of fileList.value) {
          if (file.status === 'success') continue

          const formData = new FormData()
          formData.append('file', file.file)

          // 添加额外参数
          Object.keys(props.data).forEach(key => {
            formData.append(key, props.data[key])
          })

          file.status = 'uploading'
          
          try {
            const response = await window.request.post(props.action, formData, {
              headers: {
                'Content-Type': 'multipart/form-data',
                ...props.headers
              },
              onUploadProgress: (e) => {
                file.progress = Math.round((e.loaded * 100) / e.total)
                emit('progress', file.progress, file)
              }
            })

            file.status = 'success'
            file.url = response.url
            emit('success', response, file)
          } catch (error) {
            file.status = 'error'
            emit('error', error, file)
          }
        }
      } finally {
        uploading.value = false
      }
    }

    // 移除文件
    const removeFile = (file) => {
      const index = fileList.value.indexOf(file)
      if (index > -1) {
        fileList.value.splice(index, 1)
        emit('change', fileList.value)
      }
    }

    // 清空文件列表
    const clearFiles = () => {
      fileList.value = []
      emit('change', fileList.value)
    }

    // 获取文件图标
    const getFileIcon = (file) => {
      const ext = file.name.split('.').pop().toLowerCase()
      const icons = {
        pdf: 'bi-file-pdf',
        doc: 'bi-file-word',
        docx: 'bi-file-word',
        xls: 'bi-file-excel',
        xlsx: 'bi-file-excel',
        ppt: 'bi-file-ppt',
        pptx: 'bi-file-ppt',
        jpg: 'bi-file-image',
        jpeg: 'bi-file-image',
        png: 'bi-file-image',
        gif: 'bi-file-image',
        zip: 'bi-file-zip',
        rar: 'bi-file-zip',
        txt: 'bi-file-text'
      }
      return icons[ext] || 'bi-file'
    }

    // 格式化文件大小
    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    return {
      fileList,
      uploading,
      uploadProgress,
      handleFileSelect,
      upload,
      removeFile,
      clearFiles,
      getFileIcon,
      formatFileSize
    }
  },
  template: `
    <div class="file-upload">
      <!-- 上传按钮 -->
      <div class="upload-btn">
        <input type="file" class="file-input"
          :accept="accept"
          :multiple="multiple"
          :disabled="disabled"
          @change="handleFileSelect"
          style="display: none"
          ref="fileInput">
          
        <button type="button" class="btn btn-primary"
          :disabled="disabled"
          @click="$refs.fileInput.click()">
          <i class="bi bi-upload me-1"></i>选择文件
        </button>
        
        <button v-if="!autoUpload && fileList.length"
          type="button" class="btn btn-success ms-2"
          :disabled="disabled || uploading"
          @click="upload">
          <template v-if="uploading">
            <span class="spinner-border spinner-border-sm me-1"></span>
            上传中...
          </template>
          <template v-else>
            <i class="bi bi-cloud-upload me-1"></i>开始上传
          </template>
        </button>
      </div>

      <!-- 文件列表 -->
      <div v-if="showFileList && fileList.length" class="file-list mt-3">
        <div v-for="file in fileList" :key="file.id"
          class="file-item d-flex align-items-center p-2 border rounded mb-2">
          <!-- 文件图标 -->
          <i :class="getFileIcon(file)" class="bi fs-4 me-2"></i>
          
          <!-- 文件信息 -->
          <div class="flex-grow-1">
            <div class="d-flex justify-content-between">
              <span class="file-name">{{ file.name }}</span>
              <span class="file-size text-muted">{{ formatFileSize(file.size) }}</span>
            </div>
            
            <!-- 上传进度 -->
            <div v-if="file.status === 'uploading'" class="progress mt-1" style="height: 2px">
              <div class="progress-bar" :style="{ width: file.progress + '%' }"></div>
            </div>
          </div>
          
          <!-- 状态图标 -->
          <div class="ms-2">
            <i v-if="file.status === 'success'" class="bi bi-check-circle-fill text-success"></i>
            <i v-else-if="file.status === 'error'" class="bi bi-x-circle-fill text-danger"></i>
            <div v-else-if="file.status === 'uploading'" class="spinner-border spinner-border-sm"></div>
          </div>
          
          <!-- 删除按钮 -->
          <button type="button" class="btn-close ms-2"
            :disabled="file.status === 'uploading'"
            @click="removeFile(file)">
          </button>
        </div>
      </div>
    </div>
  `
} 