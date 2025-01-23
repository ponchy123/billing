// 事件总线
window.eventBus = {
  // 事件处理器映射
  handlers: {},

  // 注册事件处理器
  on(event, handler) {
    if (!this.handlers[event]) {
      this.handlers[event] = [];
    }
    this.handlers[event].push(handler);
  },

  // 移除事件处理器
  off(event, handler) {
    if (!this.handlers[event]) return;
    if (!handler) {
      delete this.handlers[event];
    } else {
      this.handlers[event] = this.handlers[event].filter(h => h !== handler);
    }
  },

  // 触发事件
  emit(event, data) {
    if (!this.handlers[event]) return;
    this.handlers[event].forEach(handler => {
      try {
        handler(data);
      } catch (error) {
        console.error(`事件处理器错误 (${event}):`, error);
      }
    });
  }
}; 