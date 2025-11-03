/**
 * 云己项目 - 公共JavaScript工具库
 */

// API配置 - 使用后端 API URL
const ENVIRONMENT = process.env.VUE_APP_ENVIRONMENT || 'development';
const API_BASE_URL = ENVIRONMENT === 'production'
  ? 'https://your-domain.com'  // 生产环境后端 API 地址
  : 'http://localhost:8000';    // 本地开发后端 API 地址

// 工具函数类
class Utils {
    /**
     * 格式化日期
     * @param {string|Date} date 
     * @returns {string}
     */
    static formatDate(date) {
        const d = new Date(date);
        const now = new Date();
        const diff = now - d;
        
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);
        
        if (minutes < 1) return '刚刚';
        if (minutes < 60) return `${minutes}分钟前`;
        if (hours < 24) return `${hours}小时前`;
        if (days < 30) return `${days}天前`;
        
        return d.toLocaleDateString('zh-CN');
    }

    /**
     * 计算生命天数
     * @param {string} birthdate 
     * @returns {number}
     */
    static calculateLifeDays(birthdate) {
        const birth = new Date(birthdate);
        const today = new Date();
        const diffTime = Math.abs(today - birth);
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    }

    /**
     * 计算生命纪年
     * @param {string} birthdate 
     * @param {string} targetDate 
     * @returns {object}
     */
    static calculateLifeYear(birthdate, targetDate = null) {
        const birthDate = new Date(birthdate);
        const target = targetDate ? new Date(targetDate) : new Date();
        const diffTime = target - birthDate;
        const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
        
        const birthYear = birthDate.getFullYear();
        const targetYear = target.getFullYear();
        const lifeYear = targetYear - birthYear;
        
        return {
            day: diffDays + 1,
            year: lifeYear + 1,
            month: target.getMonth() + 1,
            dayOfMonth: target.getDate()
        };
    }

    /**
     * 防抖函数
     * @param {Function} func 
     * @param {number} wait 
     * @returns {Function}
     */
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * 节流函数
     * @param {Function} func 
     * @param {number} limit 
     * @returns {Function}
     */
    static throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    /**
     * 深拷贝对象
     * @param {any} obj 
     * @returns {any}
     */
    static deepClone(obj) {
        if (obj === null || typeof obj !== 'object') return obj;
        if (obj instanceof Date) return new Date(obj.getTime());
        if (obj instanceof Array) return obj.map(item => Utils.deepClone(item));
        if (typeof obj === 'object') {
            const clonedObj = {};
            for (let key in obj) {
                if (obj.hasOwnProperty(key)) {
                    clonedObj[key] = Utils.deepClone(obj[key]);
                }
            }
            return clonedObj;
        }
    }

    /**
     * 生成UUID
     * @returns {string}
     */
    static generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    /**
     * 验证邮箱格式
     * @param {string} email 
     * @returns {boolean}
     */
    static isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    /**
     * 截取文本
     * @param {string} text 
     * @param {number} length 
     * @returns {string}
     */
    static truncateText(text, length = 100) {
        if (!text) return '';
        return text.length > length ? text.substring(0, length) + '...' : text;
    }

    /**
     * 格式化文件大小
     * @param {number} bytes 
     * @returns {string}
     */
    static formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// 本地存储管理类
class Storage {
    /**
     * 设置本地存储
     * @param {string} key 
     * @param {any} value 
     */
    static set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.error('存储失败:', e);
        }
    }

    /**
     * 获取本地存储
     * @param {string} key 
     * @param {any} defaultValue 
     * @returns {any}
     */
    static get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.error('读取存储失败:', e);
            return defaultValue;
        }
    }

    /**
     * 删除本地存储
     * @param {string} key 
     */
    static remove(key) {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.error('删除存储失败:', e);
        }
    }

    /**
     * 清空本地存储
     */
    static clear() {
        try {
            localStorage.clear();
        } catch (e) {
            console.error('清空存储失败:', e);
        }
    }
}

// 提示消息管理类
class Toast {
    /**
     * 显示提示消息
     * @param {string} message 
     * @param {string} type 
     * @param {number} duration 
     */
    static show(message, type = 'info', duration = 3000) {
        // 移除已存在的提示
        const existingToast = document.querySelector('.toast');
        if (existingToast) {
            existingToast.remove();
        }

        // 创建新的提示元素
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;

        // 添加到页面
        document.body.appendChild(toast);

        // 显示动画
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);

        // 自动隐藏
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, duration);
    }

    static success(message, duration) {
        Toast.show(message, 'success', duration);
    }

    static error(message, duration) {
        Toast.show(message, 'error', duration);
    }

    static info(message, duration) {
        Toast.show(message, 'info', duration);
    }

    static warning(message, duration) {
        Toast.show(message, 'warning', duration);
    }
}

// API请求管理类
class ApiClient {
    /**
     * 发送HTTP请求
     * @param {string} url 
     * @param {object} options 
     * @returns {Promise}
     */
    static async request(url, options = {}) {
        const token = Storage.get('auth_token') || Storage.get('token');
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...(token && { 'Authorization': `Bearer ${token}` })
            }
        };

        const finalOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };

        try {
            const response = await fetch(`${API_BASE_URL}${url}`, finalOptions);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || data.error || '请求失败');
            }

            return data;
        } catch (error) {
            console.error('API请求错误:', error);
            throw error;
        }
    }

    static async get(url, options = {}) {
        return ApiClient.request(url, { ...options, method: 'GET' });
    }

    static async post(url, data, options = {}) {
        return ApiClient.request(url, {
            ...options,
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    static async put(url, data, options = {}) {
        return ApiClient.request(url, {
            ...options,
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    static async delete(url, options = {}) {
        return ApiClient.request(url, { ...options, method: 'DELETE' });
    }

    /**
     * 上传文件
     * @param {string} url 
     * @param {FormData} formData 
     * @returns {Promise}
     */
    static async upload(url, formData) {
        const token = Storage.get('auth_token') || Storage.get('token');
        
        const options = {
            method: 'POST',
            body: formData,
            headers: {
                ...(token && { 'Authorization': `Bearer ${token}` })
            }
        };

        try {
            const response = await fetch(`${API_BASE_URL}${url}`, options);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || data.error || '上传失败');
            }

            return data;
        } catch (error) {
            console.error('文件上传错误:', error);
            throw error;
        }
    }
}

// 加载状态管理类
class Loading {
    static show(element, text = '加载中...') {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        if (!element) return;

        // 创建加载指示器
        const loadingEl = document.createElement('div');
        loadingEl.className = 'loading-overlay';
        loadingEl.innerHTML = `
            <div class="loading-content">
                <div class="loading-spinner"></div>
                <span>${text}</span>
            </div>
        `;

        // 设置样式
        loadingEl.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 255, 255, 0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
        `;

        // 确保父元素有相对定位
        if (getComputedStyle(element).position === 'static') {
            element.style.position = 'relative';
        }

        element.appendChild(loadingEl);
    }

    static hide(element) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        if (!element) return;

        const loadingEl = element.querySelector('.loading-overlay');
        if (loadingEl) {
            loadingEl.remove();
        }
    }
}

// 事件总线
class EventBus {
    constructor() {
        this.events = {};
    }

    on(event, callback) {
        if (!this.events[event]) {
            this.events[event] = [];
        }
        this.events[event].push(callback);
    }

    off(event, callback) {
        if (!this.events[event]) return;
        
        this.events[event] = this.events[event].filter(cb => cb !== callback);
    }

    emit(event, data) {
        if (!this.events[event]) return;
        
        this.events[event].forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                console.error('事件回调执行错误:', error);
            }
        });
    }
}

// 创建全局事件总线实例
const eventBus = new EventBus();

// 用户认证管理 (和 Vue 的 authManager 保持一致)
class Auth {
    constructor() {
        this.currentUser = null;
        this.token = null;
        this.loadTokenFromStorage();
    }

    // 从本地存储加载 token
    loadTokenFromStorage() {
        try {
            const token = localStorage.getItem('auth_token');
            if (token) {
                this.token = token;
                // 从 token 中解析用户信息
                this.parseUserFromToken(token);
            }
        } catch (error) {
            console.error('加载 token 失败:', error);
            this.clearUserInfo();
        }
    }

    // 从 JWT token 中解析用户信息
    parseUserFromToken(token) {
        try {
            // 简单的 JWT 解析 (格式: header.payload.signature)
            const payload = JSON.parse(atob(token.split('.')[1]));
            this.currentUser = {
                user_id: payload.user_id,
                username: payload.username,
                email: payload.email
            };
        } catch (error) {
            console.error('解析 token 失败:', error);
            this.clearUserInfo();
        }
    }

    // 保存 token 到本地存储
    saveTokenToStorage(token) {
        try {
            localStorage.setItem('auth_token', token);
            this.token = token;
            // 从 token 中解析用户信息
            this.parseUserFromToken(token);
            eventBus.emit('user:login', this.currentUser);
        } catch (error) {
            console.error('保存 token 失败:', error);
        }
    }

    // 清除用户信息
    clearUserInfo() {
        this.currentUser = null;
        this.token = null;
        try {
            localStorage.removeItem('auth_token');
        } catch (error) {
            console.error('清除用户信息失败:', error);
        }
    }

    // 获取当前用户信息
    static getCurrentUser() {
        return authInstance.currentUser;
    }

    // 获取当前用户 ID
    static getCurrentUserId() {
        return authInstance.currentUser?.user_id || null;
    }

    // 获取认证 token
    static getToken() {
        return authInstance.token;
    }

    // 检查是否已登录
    static isLoggedIn() {
        return !!(authInstance.currentUser && authInstance.token);
    }

    // 登出
    static logout() {
        authInstance.clearUserInfo();
        eventBus.emit('user:logout');

        // 重定向到登录页
        window.location.href = 'login.html';
    }

    // 要求登录
    static requireAuth() {
        if (!Auth.isLoggedIn()) {
            Toast.warning('请先登录');
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 1000);
            return false;
        }
        return true;
    }
}

// 创建全局实例
const authInstance = new Auth();

// DOM就绪时执行
document.addEventListener('DOMContentLoaded', function() {
    // 检查登录状态
    if (window.location.pathname.includes('login.html')) {
        // 登录页面不需要检查认证状态
        return;
    }
    
    // 其他页面检查认证状态
    if (!Auth.isLoggedIn() && !window.location.pathname.includes('login.html')) {
        console.log('用户未登录，跳转到登录页');
        // 可以选择是否强制跳转登录页
        // window.location.href = 'login.html';
    }
});

// 导出到全局
window.Utils = Utils;
window.Storage = Storage;
window.Toast = Toast;
window.ApiClient = ApiClient;
window.Loading = Loading;
window.eventBus = eventBus;
window.Auth = Auth;