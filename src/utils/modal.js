/**
 * 全局弹窗工具
 * 提供统一的暗色主题弹窗样式
 */

let modalInstance = null

// 设置全局弹窗实例
export function setModalInstance(instance) {
  modalInstance = instance
}

// 显示自定义弹窗
export function showModal(options) {
  if (modalInstance && modalInstance.showModal) {
    return modalInstance.showModal(options)
  }
  
  // 如果没有自定义弹窗实例，回退到系统弹窗
  return new Promise((resolve) => {
    uni.showModal({
      title: options.title || '提示',
      content: options.content || '',
      showCancel: options.showCancel !== false,
      cancelText: options.cancelText || '取消',
      confirmText: options.confirmText || '确定',
      success: (res) => {
        if (res.confirm) {
          if (options.onConfirm) options.onConfirm()
          resolve(true)
        } else {
          if (options.onCancel) options.onCancel()
          resolve(false)
        }
      }
    })
  })
}

// 显示确认弹窗
export function showConfirm(title, content, options = {}) {
  return showModal({
    title,
    content,
    showCancel: true,
    ...options
  })
}

// 显示警告弹窗
export function showAlert(title, content, options = {}) {
  return showModal({
    title,
    content,
    showCancel: false,
    ...options
  })
}

// 显示危险操作确认弹窗
export function showDangerConfirm(title, content, options = {}) {
  return showModal({
    title,
    content,
    type: 'danger',
    confirmText: '确认删除',
    ...options
  })
}
