/**
 * API工具类 - 统一管理所有API调用
 * @Created on: 2025/09/14
 * @Author: DreamFly Team
 */

import authManager from './auth.js'

// API配置
const API_CONFIG = {
  BASE_URL: 'http://localhost:8000',
  ENDPOINTS: {
    // 用户资产管理
    CONSCIOUSNESS_ASSETS: '/api/user/consciousness-assets',
    DASHBOARD_STATS: '/api/user/dashboard-stats',
    
    // 记忆片段管理
    MEMORY_FRAGMENTS: '/api/user/memory-fragments',
    
    // 测试结果管理
    TEST_RESULTS: '/api/user/test-results',
    
    // 文档管理
    DOCUMENTS: '/api/user/documents',
    DOCUMENTS_UPLOAD: '/api/user/documents/upload',
    DOCUMENTS_DOWNLOAD: '/api/user/documents',
    DOCUMENTS_PREVIEW: '/api/user/documents',

    // 笔记管理
    NOTES: '/api/user/notes',
    NOTE_FOLDERS: '/api/user/note-folders',

    // 社交网络
    SOCIAL_USERS: '/api/social/users',
    SOCIAL_STATS: '/api/social/stats',
    SOCIAL_SEARCH: '/api/social/search',

    // 交易管理
    TRANSACTIONS: '/api/user/transactions',
    MARKET_ITEMS: '/api/user/market/consciousness-items'
  }
}

/**
 * 通用API调用函数
 * @param {string} endpoint - API端点
 * @param {object} options - 请求选项
 * @returns {Promise} API响应数据
 */
async function apiCall(endpoint, options = {}) {
  const url = `${API_CONFIG.BASE_URL}${endpoint}`;

  // 检查是否需要认证
  if (!authManager.isLoggedIn() && !endpoint.includes('/login') && !endpoint.includes('/register')) {
    authManager.requireLogin();
    throw new Error('用户未登录');
  }

  // 添加用户ID到请求参数（如果已登录）
  const userId = authManager.getCurrentUserId();
  let finalUrl = url;

  if (userId && !endpoint.includes('/login') && !endpoint.includes('/register')) {
    // 所有请求都使用Query参数传递user_id
    const separator = url.includes('?') ? '&' : '?';
    finalUrl = `${url}${separator}user_id=${userId}`;
  }

  try {
    const response = await fetch(finalUrl, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': authManager.getToken() ? `Bearer ${authManager.getToken()}` : '',
        ...options.headers
      },
      ...options
    });

    const data = await response.json();

    if (data.code === 200) {
      return data.data;
    } else {
      // 根据错误类型提供友好的错误信息
      let friendlyMessage = data.message || '请求失败';

      if (response.status === 422) {
        friendlyMessage = '输入信息有误，请检查后重试';
      } else if (response.status === 401) {
        friendlyMessage = '登录已过期，请重新登录';
        authManager.logout();
      } else if (response.status === 403) {
        friendlyMessage = '没有权限执行此操作';
      } else if (response.status === 404) {
        friendlyMessage = '请求的资源不存在';
      } else if (response.status >= 500) {
        friendlyMessage = '服务器错误，请稍后重试';
      }

      throw new Error(friendlyMessage);
    }
  } catch (error) {
    console.error(`API调用失败 [${endpoint}]:`, error);

    // 网络错误的友好提示
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error('网络连接失败，请检查网络后重试');
    }

    throw error;
  }
}

/**
 * 用户资产管理API
 */
export const assetsAPI = {
  // 获取用户资产列表
  async getUserAssets() {
    const result = await apiCall(API_CONFIG.ENDPOINTS.CONSCIOUSNESS_ASSETS);
    return result.assets || [];
  },
  
  // 创建新资产
  async createAsset(assetData) {
    const result = await apiCall(API_CONFIG.ENDPOINTS.CONSCIOUSNESS_ASSETS, {
      method: 'POST',
      body: JSON.stringify(assetData)
    });
    return result.asset;
  },
  
  // 获取资产详情
  async getAssetDetail(assetId) {
    const result = await apiCall(`${API_CONFIG.ENDPOINTS.CONSCIOUSNESS_ASSETS}/${assetId}`);
    return result.asset;
  },
  
  // 更新资产
  async updateAsset(assetId, updateData) {
    const result = await apiCall(`${API_CONFIG.ENDPOINTS.CONSCIOUSNESS_ASSETS}/${assetId}`, {
      method: 'PUT',
      body: JSON.stringify(updateData)
    });
    return result.asset;
  },
  
  // 删除资产
  async deleteAsset(assetId) {
    await apiCall(`${API_CONFIG.ENDPOINTS.CONSCIOUSNESS_ASSETS}/${assetId}`, {
      method: 'DELETE'
    });
    return true;
  },
  
  // 获取仪表板统计数据
  async getDashboardStats() {
    const result = await apiCall(API_CONFIG.ENDPOINTS.DASHBOARD_STATS);
    return result.stats || {};
  }
};

/**
 * 记忆片段管理API
 */
export const memoryAPI = {
  // 获取记忆片段列表
  async getMemoryFragments(category = null) {
    const endpoint = category 
      ? `${API_CONFIG.ENDPOINTS.MEMORY_FRAGMENTS}?category=${category}`
      : API_CONFIG.ENDPOINTS.MEMORY_FRAGMENTS;
    const result = await apiCall(endpoint);
    return result.fragments || [];
  },
  
  // 创建记忆片段
  async createMemoryFragment(memoryData) {
    const result = await apiCall(API_CONFIG.ENDPOINTS.MEMORY_FRAGMENTS, {
      method: 'POST',
      body: JSON.stringify(memoryData)
    });
    return result.fragment;
  },
  
  // 获取记忆片段详情
  async getMemoryDetail(fragmentId) {
    const result = await apiCall(`${API_CONFIG.ENDPOINTS.MEMORY_FRAGMENTS}/${fragmentId}`);
    return result.fragment;
  },
  
  // 更新记忆片段
  async updateMemoryFragment(fragmentId, updateData) {
    const result = await apiCall(`${API_CONFIG.ENDPOINTS.MEMORY_FRAGMENTS}/${fragmentId}`, {
      method: 'PUT',
      body: JSON.stringify(updateData)
    });
    return result.fragment;
  },
  
  // 删除记忆片段
  async deleteMemoryFragment(fragmentId) {
    await apiCall(`${API_CONFIG.ENDPOINTS.MEMORY_FRAGMENTS}/${fragmentId}`, {
      method: 'DELETE'
    });
    return true;
  }
};

/**
 * 测试结果管理API
 */
export const testAPI = {
  // 获取测试结果列表
  async getTestResults(testType = null) {
    const userInfo = authManager.getCurrentUser();
    if (!userInfo) {
      throw new Error('用户未登录');
    }

    let endpoint = `${API_CONFIG.ENDPOINTS.TEST_RESULTS}?user_id=${userInfo.user_id}`;
    if (testType) {
      endpoint += `&test_type=${testType}`;
    }
    const result = await apiCall(endpoint);
    return result.test_results || [];
  },

  // 保存测试结果
  async saveTestResult(testData) {
    const userInfo = authManager.getCurrentUser();
    if (!userInfo) {
      throw new Error('用户未登录');
    }

    const endpoint = `${API_CONFIG.ENDPOINTS.TEST_RESULTS}?user_id=${userInfo.user_id}`;
    const result = await apiCall(endpoint, {
      method: 'POST',
      body: JSON.stringify(testData)
    });
    return result.test_result;
  },
  
  // 获取测试结果详情
  async getTestDetail(testId) {
    const userInfo = authManager.getCurrentUser();
    if (!userInfo) {
      throw new Error('用户未登录');
    }

    const endpoint = `${API_CONFIG.ENDPOINTS.TEST_RESULTS}/${testId}?user_id=${userInfo.user_id}`;
    const result = await apiCall(endpoint);
    return result.test_result;
  }
};

/**
 * 文档管理API
 */
export const documentsAPI = {
  // 获取文档列表
  async getDocuments() {
    const result = await apiCall(API_CONFIG.ENDPOINTS.DOCUMENTS);
    return result.documents || [];
  },
  
  // 上传文档
  async uploadDocument(file) {
    const userId = authManager.getCurrentUserId();
    if (!userId) {
      throw new Error('用户未登录');
    }

    const formData = new FormData();
    formData.append('file', file);

    const url = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.DOCUMENTS_UPLOAD}?user_id=${encodeURIComponent(userId)}`;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': authManager.getToken() ? `Bearer ${authManager.getToken()}` : '',
      },
      body: formData
    });

    const data = await response.json();
    if (data.code === 200) {
      return data.data;
    } else {
      throw new Error(data.message || '文档上传失败');
    }
  },
  
  // 获取文档详情
  async getDocumentDetail(docId) {
    const result = await apiCall(`${API_CONFIG.ENDPOINTS.DOCUMENTS}/${docId}`);
    return result.document;
  },
  
  // 更新文档
  async updateDocument(docId, updateData) {
    const result = await apiCall(`${API_CONFIG.ENDPOINTS.DOCUMENTS}/${docId}`, {
      method: 'PUT',
      body: JSON.stringify(updateData)
    });
    return result.document;
  },
  
  // 删除文档
  async deleteDocument(docId) {
    await apiCall(`${API_CONFIG.ENDPOINTS.DOCUMENTS}/${docId}`, {
      method: 'DELETE'
    });
    return true;
  },

  // 获取文档预览URL
  getDocumentPreviewUrl(docId) {
    const userId = authManager.getCurrentUserId();
    if (!userId) {
      throw new Error('用户未登录');
    }
    return `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.DOCUMENTS_PREVIEW}/${docId}/preview?user_id=${encodeURIComponent(userId)}`;
  },

  // 获取文档下载URL
  getDocumentDownloadUrl(docId) {
    const userId = authManager.getCurrentUserId();
    if (!userId) {
      throw new Error('用户未登录');
    }
    return `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.DOCUMENTS_DOWNLOAD}/${docId}/download?user_id=${encodeURIComponent(userId)}`;
  }
};

/**
 * 笔记管理API
 */
export const notesAPI = {
  // 获取笔记列表
  async getNotes(folderId = null) {
    const endpoint = folderId
      ? `${API_CONFIG.ENDPOINTS.NOTES}?folder_id=${folderId}`
      : API_CONFIG.ENDPOINTS.NOTES;
    const result = await apiCall(endpoint);
    return result.notes || [];
  },

  // 获取所有笔记（不按文件夹过滤）
  async getAllNotes() {
    const endpoint = `${API_CONFIG.ENDPOINTS.NOTES}?all_notes=true`;
    const result = await apiCall(endpoint);
    return result.notes || [];
  },

  // 创建笔记
  async createNote(noteData) {
    const result = await apiCall(API_CONFIG.ENDPOINTS.NOTES, {
      method: 'POST',
      body: JSON.stringify(noteData)
    });
    return result.note;
  },

  // 获取笔记详情
  async getNoteDetail(noteId) {
    const result = await apiCall(`${API_CONFIG.ENDPOINTS.NOTES}/${noteId}`);
    return result.note;
  },

  // 更新笔记
  async updateNote(noteId, noteData) {
    const result = await apiCall(`${API_CONFIG.ENDPOINTS.NOTES}/${noteId}`, {
      method: 'PUT',
      body: JSON.stringify(noteData)
    });
    return result.note;
  },

  // 删除笔记
  async deleteNote(noteId) {
    await apiCall(`${API_CONFIG.ENDPOINTS.NOTES}/${noteId}`, {
      method: 'DELETE'
    });
    return true;
  },

  // 获取文件夹列表
  async getFolders() {
    const result = await apiCall(API_CONFIG.ENDPOINTS.NOTE_FOLDERS);
    return result.folders || [];
  },

  // 创建文件夹
  async createFolder(folderData) {
    const result = await apiCall(API_CONFIG.ENDPOINTS.NOTE_FOLDERS, {
      method: 'POST',
      body: JSON.stringify(folderData)
    });
    return result.folder;
  }
};

/**
 * 交易管理API
 */
export const transactionAPI = {
  // 获取交易记录
  async getTransactions() {
    const result = await apiCall(API_CONFIG.ENDPOINTS.TRANSACTIONS);
    return result.transactions || [];
  },
  
  // 创建交易
  async createTransaction(transactionData) {
    const result = await apiCall(API_CONFIG.ENDPOINTS.TRANSACTIONS, {
      method: 'POST',
      body: JSON.stringify(transactionData)
    });
    return result.transaction;
  },
  
  // 获取市场商品
  async getMarketItems(limit = 20) {
    const result = await apiCall(`${API_CONFIG.ENDPOINTS.MARKET_ITEMS}?limit=${limit}`);
    return result.items || [];
  }
};

/**
 * 社交网络API
 */
export const socialAPI = {
  // 添加用户
  async addUser(ownerUserId, userData) {
    const result = await apiCall(`${API_CONFIG.ENDPOINTS.SOCIAL_USERS}?owner_id=${ownerUserId}`, {
      method: 'POST',
      body: JSON.stringify({
        account_id: userData.accountId,
        space: userData.space,
        is_inheritor: userData.isInheritor || false
      })
    });
    return result;
  },

  // 获取用户权限列表
  async getUserPermissions(ownerUserId, space = null) {
    let url = `${API_CONFIG.ENDPOINTS.SOCIAL_USERS}?owner_id=${ownerUserId}`;
    if (space) {
      url += `&space=${space}`;
    }
    const result = await apiCall(url);
    return result || [];
  },

  // 更新用户权限
  async updateUserPermission(ownerUserId, permissionId, updateData) {
    const result = await apiCall(`${API_CONFIG.ENDPOINTS.SOCIAL_USERS}/${permissionId}?owner_id=${ownerUserId}`, {
      method: 'PUT',
      body: JSON.stringify(updateData)
    });
    return result;
  },

  // 移除用户权限
  async removeUserPermission(ownerUserId, permissionId) {
    const result = await apiCall(`${API_CONFIG.ENDPOINTS.SOCIAL_USERS}/${permissionId}?owner_id=${ownerUserId}`, {
      method: 'DELETE'
    });
    return result;
  },

  // 获取社交统计数据
  async getSocialStats(ownerUserId) {
    const result = await apiCall(`${API_CONFIG.ENDPOINTS.SOCIAL_STATS}?owner_id=${ownerUserId}`);
    return result;
  },

  // 搜索用户
  async searchUser(accountId) {
    const result = await apiCall(`${API_CONFIG.ENDPOINTS.SOCIAL_SEARCH}?account_id=${accountId}`);
    return result;
  }
};

// 默认导出所有API
export default {
  assetsAPI,
  memoryAPI,
  testAPI,
  documentsAPI,
  notesAPI,
  transactionAPI,
  socialAPI
};
