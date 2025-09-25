/**
 * 文件相关工具函数
 */

/**
 * 根据文件类型获取对应的图标
 * @param {string} type - 文件类型
 * @returns {string} 文件图标
 */
export function getFileIcon(type) {
  const icons = {
    pdf: '📕',
    doc: '📘',
    docx: '📘',
    txt: '📗'
  }
  return icons[type] || '📄'
}

/**
 * 格式化文件大小
 * @param {number} size - 文件大小（字节）
 * @returns {string} 格式化后的文件大小
 */
export function formatFileSize(size) {
  if (size < 1024) return size + ' B'
  if (size < 1024 * 1024) return (size / 1024).toFixed(1) + ' KB'
  return (size / (1024 * 1024)).toFixed(1) + ' MB'
}
