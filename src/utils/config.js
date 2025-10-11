/**
 * 环境配置管理（Vite define 全局常量版）
 * @Created on: 2025/01/15 10:00
 * @Author: DreamFly Team
 */

// ✅ 完全使用 vite.config.js 中 define 注入的全局常量
export const config = {
  ENVIRONMENT: __IS_PRODUCTION__ ? 'production' : 'development',
  DEBUG: __DEBUG__,
  isDevelopment: !__IS_PRODUCTION__,
  isProduction: __IS_PRODUCTION__,

  // ✅ 直接使用注入的字符串，不再重复判断
  API_BASE_URL: __API_BASE_URL__,
  FRONTEND_URL: __FRONTEND_URL__,

  // API端点配置（保持不变）
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