/**
 * 统一的API请求工具
 * @Created on: 2025/01/15 10:00
 * @Author: DreamFly Team
 */

import authManager from './auth.js'

/**
 * 统一的API请求方法
 * @param {Object} options - 请求配置
 * @returns {Promise} 请求结果
 */
export function apiRequest(options) {
  return new Promise((resolve, reject) => {
    // 默认配置
    const defaultOptions = {
      method: 'GET',
      header: {
        'Content-Type': 'application/json'
      },
      timeout: 10000
    }

    // 合并配置
    const finalOptions = { ...defaultOptions, ...options }

    // 添加基础URL
    if (finalOptions.url && !finalOptions.url.startsWith('http')) {
      finalOptions.url = `http://localhost:8000${finalOptions.url}`
    }

    // 添加JWT token到请求头
    const token = authManager.getToken()
    if (token) {
      finalOptions.header['Authorization'] = `Bearer ${token}`
    }

    // 发起请求
    uni.request({
      ...finalOptions,
      success: (response) => {
        // 检查HTTP状态码
        if (response.statusCode === 401) {
          // token无效或过期
          console.log('Token无效，清除登录状态')
          authManager.clearUserInfo()
          authManager.requireLogin()
          reject(new Error('登录已过期'))
          return
        }

        if (response.statusCode === 403) {
          // 权限不足
          uni.showToast({
            title: '权限不足',
            icon: 'none'
          })
          reject(new Error('权限不足'))
          return
        }

        if (response.statusCode >= 200 && response.statusCode < 300) {
          // 请求成功
          resolve(response)
        } else {
          // 其他HTTP错误
          console.error('HTTP错误:', response.statusCode, response.data)
          reject(new Error(`HTTP错误: ${response.statusCode}`))
        }
      },
      fail: (error) => {
        console.error('API请求失败:', finalOptions.url, error)
        reject(error)
      }
    })
  })
}

/**
 * GET请求
 * @param {string} url - 请求URL
 * @param {Object} params - 查询参数
 * @param {Object} options - 其他配置
 * @returns {Promise} 请求结果
 */
export function get(url, params = {}, options = {}) {
  // 构建查询字符串
  const queryString = Object.keys(params)
    .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
    .join('&')
  
  const finalUrl = queryString ? `${url}?${queryString}` : url

  return apiRequest({
    url: finalUrl,
    method: 'GET',
    ...options
  })
}

/**
 * POST请求
 * @param {string} url - 请求URL
 * @param {Object} data - 请求数据
 * @param {Object} options - 其他配置
 * @returns {Promise} 请求结果
 */
export function post(url, data = {}, options = {}) {
  return apiRequest({
    url,
    method: 'POST',
    data,
    ...options
  })
}

/**
 * PUT请求
 * @param {string} url - 请求URL
 * @param {Object} data - 请求数据
 * @param {Object} options - 其他配置
 * @returns {Promise} 请求结果
 */
export function put(url, data = {}, options = {}) {
  return apiRequest({
    url,
    method: 'PUT',
    data,
    ...options
  })
}

/**
 * DELETE请求
 * @param {string} url - 请求URL
 * @param {Object} options - 其他配置
 * @returns {Promise} 请求结果
 */
export function del(url, options = {}) {
  return apiRequest({
    url,
    method: 'DELETE',
    ...options
  })
}
