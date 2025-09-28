/**
 * 用户认证工具类
 * @Created on: 2025/09/14
 * @Author: DreamFly Team
 */

import { config, buildApiUrl, logger } from './config.js'

// 用户状态管理
class AuthManager {
  constructor() {
    this.currentUser = null
    this.token = null
    this.loadTokenFromStorage()
  }

  // 从本地存储加载token
  loadTokenFromStorage() {
    try {
      const token = uni.getStorageSync('auth_token')

      if (token) {
        this.token = token
        // 从token中解析用户信息（不存储在本地）
        this.parseUserFromToken(token)
      }
    } catch (error) {
      console.error('加载token失败:', error)
      this.clearUserInfo()
    }
  }

  // 从JWT token中解析用户信息
  parseUserFromToken(token) {
    try {
      // 简单的JWT解析（仅用于获取用户信息，不验证签名）
      const payload = JSON.parse(atob(token.split('.')[1]))
      this.currentUser = {
        user_id: payload.user_id,
        username: payload.username,
        email: payload.email
      }
    } catch (error) {
      console.error('解析token失败:', error)
      this.clearUserInfo()
    }
  }

  // 保存token到本地存储
  saveTokenToStorage(token) {
    try {
      uni.setStorageSync('auth_token', token)
      this.token = token
      // 从token中解析用户信息
      this.parseUserFromToken(token)
    } catch (error) {
      console.error('保存token失败:', error)
    }
  }

  // 清除用户信息
  clearUserInfo() {
    this.currentUser = null
    this.token = null
    try {
      uni.removeStorageSync('auth_token')
    } catch (error) {
      console.error('清除用户信息失败:', error)
    }
  }

  // 获取当前用户ID
  getCurrentUserId() {
    return this.currentUser?.user_id || null
  }

  // 获取当前用户信息
  getCurrentUser() {
    return this.currentUser
  }

  // 获取认证token
  getToken() {
    return this.token
  }

  // 检查是否已登录
  isLoggedIn() {
    return !!(this.currentUser && this.token)
  }

  // 登录
  async login(email, password) {
    return new Promise((resolve) => {
      // 登录请求不需要token，直接使用uni.request
      uni.request({
        url: buildApiUrl('/api/login'),
        method: 'POST',
        header: {
          'Content-Type': 'application/json'
        },
        data: {
          email: email,
          password: password
        },
        success: (response) => {
          console.log('登录响应:', response)
          if (response.data.code === 200) {
            const userData = response.data.data
            const token = userData.token

            if (token) {
              this.saveTokenToStorage(token)
              resolve({
                success: true,
                data: userData
              })
            } else {
              resolve({
                success: false,
                message: '服务器未返回有效token'
              })
            }
          } else {
            resolve({
              success: false,
              message: response.data.message || '登录失败'
            })
          }
        },
        fail: (error) => {
          console.error('登录请求失败:', error)
          resolve({
            success: false,
            message: '网络错误，请稍后重试'
          })
        }
      })
    })
  }

  // 注册
  async register(username, email, password, confirmPassword) {
    if (password !== confirmPassword) {
      return {
        success: false,
        message: '两次输入的密码不一致'
      }
    }

    return new Promise((resolve) => {
      // 注册请求不需要token，直接使用uni.request
      uni.request({
        url: 'http://localhost:8000/api/register',
        method: 'POST',
        header: {
          'Content-Type': 'application/json'
        },
        data: {
          username: username,
          email: email,
          password: password,
          confirm_password: confirmPassword
        },
        success: (response) => {
          console.log('注册响应:', response)
          if (response.data.code === 200) {
            resolve({
              success: true,
              data: response.data.data,
              message: '注册成功，请登录'
            })
          } else {
            resolve({
              success: false,
              message: response.data.message || '注册失败'
            })
          }
        },
        fail: (error) => {
          console.error('注册请求失败:', error)
          resolve({
            success: false,
            message: '网络错误，请稍后重试'
          })
        }
      })
    })
  }

  // 登出
  logout() {
    this.clearUserInfo()
    // 跳转到登录页
    uni.reLaunch({
      url: '/pages/auth/login'
    })
  }

  // 检查登录状态，如果未登录则跳转到登录页
  requireLogin() {
    if (!this.isLoggedIn()) {
      uni.showModal({
        title: '需要登录',
        content: '请先登录后再使用此功能',
        showCancel: false,
        success: () => {
          uni.reLaunch({
            url: '/pages/auth/login'
          })
        }
      })
      return false
    }
    return true
  }
}

// 创建全局实例
const authManager = new AuthManager()

// 导出认证管理器
export default authManager

// 导出便捷方法
export const getCurrentUserId = () => authManager.getCurrentUserId()
export const getCurrentUser = () => authManager.getCurrentUser()
export const isLoggedIn = () => authManager.isLoggedIn()
export const requireLogin = () => authManager.requireLogin()
export const logout = () => authManager.logout()
