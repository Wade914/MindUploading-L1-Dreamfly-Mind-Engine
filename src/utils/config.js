/**
 * 环境配置管理
 * @Created on: 2025/01/15 10:00
 * @Author: DreamFly Team
 */

/**
 * 获取环境变量
 * @param {string} key - 环境变量键名
 * @param {string} defaultValue - 默认值
 * @returns {string} 环境变量值
 */
function getEnvVar(key, defaultValue = '') {
  // 在uni-app中，环境变量通过process.env访问
  // 注意：只有以VUE_APP_开头的变量才会被暴露到客户端
  return process.env[key] || defaultValue
}

/**
 * 获取当前环境
 */
const ENVIRONMENT = getEnvVar('VUE_APP_ENVIRONMENT', 'development')
const IS_DEVELOPMENT = ENVIRONMENT === 'development'
const IS_PRODUCTION = ENVIRONMENT === 'production'

/**
 * 根据环境获取配置值
 * @param {string} devKey - 开发环境键名
 * @param {string} prodKey - 生产环境键名
 * @param {string} defaultValue - 默认值
 * @returns {string} 配置值
 */
function getEnvConfig(devKey, prodKey, defaultValue = '') {
  if (IS_PRODUCTION) {
    return getEnvVar(prodKey, defaultValue)
  }
  return getEnvVar(devKey, defaultValue)
}

/**
 * 应用配置
 */
export const config = {
  // 环境配置
  ENVIRONMENT,
  DEBUG: getEnvVar('VUE_APP_DEBUG', 'true') === 'true',
  isDevelopment: IS_DEVELOPMENT,
  isProduction: IS_PRODUCTION,

  // API配置 - 根据环境自动选择
  API_BASE_URL: getEnvConfig(
    'VUE_APP_DEV_API_BASE_URL',
    'VUE_APP_PROD_API_BASE_URL',
    'http://localhost:8000'
  ),

  FRONTEND_URL: getEnvConfig(
    'VUE_APP_DEV_FRONTEND_URL',
    'VUE_APP_PROD_FRONTEND_URL',
    'http://localhost:5173'
  ),
  
  // API端点配置
  API_ENDPOINTS: {
    // 认证相关
    LOGIN: '/api/login',
    REGISTER: '/api/register',
    
    // 意识体管理
    MINDS: '/api/minds',
    MIND_LIST: '/api/mind-list',
    MIND_DETAIL: '/api/mind',
    
    // 用户资产
    USER_ASSETS: '/api/user/consciousness-assets',
    DASHBOARD_STATS: '/api/user/dashboard-stats',
    
    // 记忆片段
    MEMORY_FRAGMENTS: '/api/user/memory-fragments',
    
    // 文档管理
    DOCUMENTS: '/api/user/documents',
    DOCUMENTS_UPLOAD: '/api/user/documents/upload',
    
    // 笔记管理
    NOTES: '/api/user/notes',
    NOTE_FOLDERS: '/api/user/note-folders',
    
    // 社交网络
    SOCIAL_USERS: '/api/social/users',
    SOCIAL_STATS: '/api/social/stats',
    SOCIAL_SEARCH: '/api/social/search',
    
    // AI服务
    AI_MODELS: '/api/ai/models',
    AI_CHAT: '/api/ai/chat',
    AI_SPEECH: '/api/audio/speech',
    
    // 交互管理
    INTERACTIONS: '/api/interactions'
  }
}

/**
 * 构建完整的API URL
 * @param {string} endpoint - API端点
 * @returns {string} 完整的API URL
 */
export function buildApiUrl(endpoint) {
  // 如果endpoint已经是完整URL，直接返回
  if (endpoint.startsWith('http://') || endpoint.startsWith('https://')) {
    return endpoint
  }
  
  // 确保endpoint以/开头
  if (!endpoint.startsWith('/')) {
    endpoint = '/' + endpoint
  }
  
  return config.API_BASE_URL + endpoint
}

/**
 * 获取API端点URL
 * @param {string} endpointKey - 端点键名
 * @returns {string} 完整的API URL
 */
export function getApiUrl(endpointKey) {
  const endpoint = config.API_ENDPOINTS[endpointKey]
  if (!endpoint) {
    console.warn(`API端点 ${endpointKey} 不存在`)
    return ''
  }
  return buildApiUrl(endpoint)
}

/**
 * 日志工具
 */
export const logger = {
  debug: (...args) => {
    if (config.DEBUG) {
      console.log('[DEBUG]', ...args)
    }
  },
  info: (...args) => {
    console.log('[INFO]', ...args)
  },
  warn: (...args) => {
    console.warn('[WARN]', ...args)
  },
  error: (...args) => {
    console.error('[ERROR]', ...args)
  }
}

// 默认导出配置对象
export default config
