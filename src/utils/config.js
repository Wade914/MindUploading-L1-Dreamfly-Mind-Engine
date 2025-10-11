/**
 * 环境配置管理（Vite 兼容静态替换版）
 * @Created on: 2025/01/15 10:00
 * @Author: DreamFly Team
 */

// ✅ 使用静态表达式，确保 Vite 的 define 能正确替换
const ENVIRONMENT = process.env.VUE_APP_ENVIRONMENT || 'development';
const IS_PRODUCTION = ENVIRONMENT === 'production';
const DEBUG = (process.env.VUE_APP_DEBUG || 'false') === 'true';

export const config = {
  ENVIRONMENT,
  DEBUG,
  isDevelopment: !IS_PRODUCTION,
  isProduction: IS_PRODUCTION,

  // API 基础地址（关键：静态条件表达式）
  API_BASE_URL: IS_PRODUCTION
    ? (process.env.VUE_APP_PROD_API_BASE_URL || 'http://8.129.25.16:8000')
    : (process.env.VUE_APP_DEV_API_BASE_URL || 'http://localhost:8000'),

  FRONTEND_URL: IS_PRODUCTION
    ? (process.env.VUE_APP_PROD_FRONTEND_URL || 'http://8.129.25.16')
    : (process.env.VUE_APP_DEV_FRONTEND_URL || 'http://localhost:5173'),

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
 */
export function buildApiUrl(endpoint) {
  if (endpoint.startsWith('http://') || endpoint.startsWith('https://')) {
    return endpoint
  }
  if (!endpoint.startsWith('/')) {
    endpoint = '/' + endpoint
  }
  return config.API_BASE_URL + endpoint
}

/**
 * 获取API端点URL
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

export default config