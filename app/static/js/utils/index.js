// 工具函数集合
window.utils = {
  // HTTP请求工具
  request: {
    async handleResponse(response) {
      try {
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
          return {
            success: false,
            message: '服务器返回格式错误'
          };
        }
        
        const data = await response.json();
        
        if (!response.ok) {
          return {
            success: false,
            message: data.message || response.statusText || '请求失败'
          };
        }
        
        return {
          success: true,
          data: data.data || data,
          message: data.message
        };
      } catch (error) {
        console.error('Response handling error:', error);
        return {
          success: false,
          message: '解析响应失败'
        };
      }
    },

    buildUrlParams(params) {
      return Object.entries(params)
        .filter(([_, value]) => value !== null && value !== undefined)
        .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
        .join('&');
    },

    async get(url, params = {}) {
      try {
        const queryString = this.buildUrlParams(params);
        const fullUrl = queryString ? `${url}?${queryString}` : url;
        const response = await fetch(fullUrl, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
          },
          credentials: 'same-origin'
        });
        return this.handleResponse(response);
      } catch (error) {
        console.error('Request failed:', error);
        return {
          success: false,
          message: error.message || '网络请求失败'
        };
      }
    },

    async post(url, data = {}) {
      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
          },
          credentials: 'same-origin',
          body: JSON.stringify(data)
        });
        return this.handleResponse(response);
      } catch (error) {
        console.error('Request failed:', error);
        return {
          success: false,
          message: error.message || '网络请求失败'
        };
      }
    }
  },

  // 提示工具
  toast: {
    show(message, type = 'info') {
      const toast = document.createElement('div');
      toast.className = `toast toast-${type}`;
      toast.textContent = message;
      document.body.appendChild(toast);
      
      setTimeout(() => {
        toast.classList.add('show');
      }, 100);

      setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
          document.body.removeChild(toast);
        }, 300);
      }, 3000);
    },

    success(message) {
      this.show(message, 'success');
    },

    error(message) {
      this.show(message, 'error');
    },

    warning(message) {
      this.show(message, 'warning');
    },

    info(message) {
      this.show(message, 'info');
    }
  },

  // 防抖函数
  debounce(func, wait = 300) {
    let timeout;
    return function(...args) {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(this, args), wait);
    };
  },

  // 节流函数
  throttle(func, wait = 300) {
    let timeout;
    let previous = 0;
    return function(...args) {
      const now = Date.now();
      if (!previous) previous = now;
      const remaining = wait - (now - previous);
      if (remaining <= 0 || remaining > wait) {
        if (timeout) {
          clearTimeout(timeout);
          timeout = null;
        }
        previous = now;
        func.apply(this, args);
      } else if (!timeout) {
        timeout = setTimeout(() => {
          previous = Date.now();
          timeout = null;
          func.apply(this, args);
        }, remaining);
      }
    };
  },

  // 深拷贝
  deepClone(obj) {
    if (obj === null || typeof obj !== 'object') return obj;
    if (obj instanceof Date) return new Date(obj);
    if (obj instanceof RegExp) return new RegExp(obj);
    if (obj instanceof Map) return new Map(Array.from(obj, ([key, val]) => [key, this.deepClone(val)]));
    if (obj instanceof Set) return new Set(Array.from(obj, val => this.deepClone(val)));
    const clone = Array.isArray(obj) ? [] : {};
    for (const key in obj) {
      if (Object.prototype.hasOwnProperty.call(obj, key)) {
        clone[key] = this.deepClone(obj[key]);
      }
    }
    return clone;
  },

  // 生成唯一ID
  generateId(prefix = '') {
    return prefix + Math.random().toString(36).substr(2, 9);
  },

  // 判断是否为空
  isEmpty(value) {
    if (value === null || value === undefined) return true;
    if (typeof value === 'string') return value.trim() === '';
    if (Array.isArray(value)) return value.length === 0;
    if (typeof value === 'object') return Object.keys(value).length === 0;
    return false;
  },

  // 获取URL参数
  getUrlParams(url = window.location.href) {
    const params = {};
    const searchParams = new URL(url).searchParams;
    for (const [key, value] of searchParams) {
      params[key] = value;
    }
    return params;
  },

  // 下载文件
  downloadFile(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  },

  // 复制文本到剪贴板
  async copyToClipboard(text) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (error) {
      console.error('复制失败:', error);
      return false;
    }
  },

  // 检查设备类型
  getDeviceType() {
    const ua = navigator.userAgent;
    if (/(tablet|ipad|playbook|silk)|(android(?!.*mobi))/i.test(ua)) {
      return 'tablet';
    }
    if (/Mobile|Android|iP(hone|od)|IEMobile|BlackBerry|Kindle|Silk-Accelerated|(hpw|web)OS|Opera M(obi|ini)/.test(ua)) {
      return 'mobile';
    }
    return 'desktop';
  },

  // 检查浏览器类型
  getBrowserType() {
    const ua = navigator.userAgent;
    if (ua.includes('Chrome')) return 'chrome';
    if (ua.includes('Firefox')) return 'firefox';
    if (ua.includes('Safari')) return 'safari';
    if (ua.includes('Edge')) return 'edge';
    if (ua.includes('MSIE') || ua.includes('Trident/')) return 'ie';
    return 'unknown';
  },

  // 格式化文件大小
  formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  },

  // 检查文件类型
  checkFileType(file, acceptTypes) {
    if (!acceptTypes) return true;
    const types = acceptTypes.split(',').map(type => type.trim());
    const fileType = file.type || '';
    const fileExtension = '.' + file.name.split('.').pop();
    
    return types.some(type => {
      if (type.startsWith('.')) {
        return type.toLowerCase() === fileExtension.toLowerCase();
      }
      if (type.endsWith('/*')) {
        return fileType.startsWith(type.slice(0, -1));
      }
      return type === fileType;
    });
  },

  // 检查文件大小
  checkFileSize(file, maxSize) {
    return file.size <= maxSize;
  },

  // 读取文件内容
  readFile(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  },

  // 解析Excel文件
  async parseExcel(file) {
    const XLSX = window.XLSX;
    if (!XLSX) throw new Error('请先引入XLSX库');

    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const data = new Uint8Array(e.target.result);
          const workbook = XLSX.read(data, { type: 'array' });
          const result = {};
          workbook.SheetNames.forEach(sheetName => {
            result[sheetName] = XLSX.utils.sheet_to_json(workbook.Sheets[sheetName]);
          });
          resolve(result);
        } catch (error) {
          reject(error);
        }
      };
      reader.onerror = reject;
      reader.readAsArrayBuffer(file);
    });
  },

  // 导出Excel文件
  exportExcel(data, filename = 'export.xlsx') {
    const XLSX = window.XLSX;
    if (!XLSX) throw new Error('请先引入XLSX库');

    const wb = XLSX.utils.book_new();
    Object.entries(data).forEach(([sheetName, sheetData]) => {
      const ws = XLSX.utils.json_to_sheet(sheetData);
      XLSX.utils.book_append_sheet(wb, ws, sheetName);
    });
    XLSX.writeFile(wb, filename);
  }
} 