// 格式化工具函数
window.formatUtils = {
  // 格式化日期时间
  formatDateTime(date) {
    if (!date) return '';
    const d = new Date(date);
    return d.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  },

  // 格式化日期
  formatDate(date) {
    if (!date) return '';
    const d = new Date(date);
    return d.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    });
  },

  // 格式化时间
  formatTime(date) {
    if (!date) return '';
    const d = new Date(date);
    return d.toLocaleString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  },

  // 格式化金额
  formatMoney(amount, currency = '¥') {
    if (typeof amount !== 'number') return '';
    return `${currency}${amount.toFixed(2)}`;
  },

  // 格式化文件大小
  formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  },

  // 格式化百分比
  formatPercent(value, decimals = 2) {
    if (typeof value !== 'number') return '';
    return value.toFixed(decimals) + '%';
  },

  // 格式化手机号
  formatPhone(phone) {
    if (!phone) return '';
    return phone.replace(/(\d{3})(\d{4})(\d{4})/, '$1-$2-$3');
  },

  // 格式化身份证号
  formatIdCard(idCard) {
    if (!idCard) return '';
    return idCard.replace(/(\d{6})(\d{4})(\d{4})(\d{4})/, '$1-$2-$3-$4');
  },

  // 格式化银行卡号
  formatBankCard(cardNo) {
    if (!cardNo) return '';
    return cardNo.replace(/(\d{4})(?=\d)/g, '$1 ');
  },

  // 格式化数字（添加千分位）
  formatNumber(num) {
    if (typeof num !== 'number') return '';
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  }
} 