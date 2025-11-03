// API配置和用户认证模块
// 用于所有square相关的HTML页面

// API配置
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000'  // 本地开发
    : 'http://upme.cool';       // 生产环境

// 获取token（从localStorage读取，与uni-app共享）
function getAuthToken() {
    return localStorage.getItem('auth_token') || localStorage.getItem('token');
}

// 获取当前用户信息 (从 JWT token 解析,和 Vue 的 authManager 保持一致)
function getCurrentUser() {
    const token = localStorage.getItem('auth_token');
    if (!token) {
        return null;
    }

    try {
        // 简单的 JWT 解析 (格式: header.payload.signature)
        const payload = JSON.parse(atob(token.split('.')[1]));
        return {
            user_id: payload.user_id,
            username: payload.username,
            email: payload.email
        };
    } catch (error) {
        console.error('解析 token 失败:', error);
        return null;
    }
}

// 页面导航函数（用于HTML页面之间的跳转 - 保留历史记录）
function navigateTo(page, params = {}) {
    const routes = {
        'square': '/pages/square/index',
        'homepage': '/pages/square/homepage/index',
        'profile': '/pages/square/profile/index',
        'mindos': '/pages/square/mindos/index',
        'wittgenstein': '/pages/square/wittgenstein/index',
        'following': '/pages/square/following/index',
        'messages': '/pages/square/messages/index',
        'consciousness': '/pages/consciousness/index'
    };

    let route = routes[page];
    if (route) {
        // 添加查询参数
        if (Object.keys(params).length > 0) {
            const queryString = Object.entries(params)
                .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
                .join('&');
            route = `${route}?${queryString}`;
        }

        // 检测是否在uni-app的web-view中
        if (typeof uni !== 'undefined' && typeof uni.postMessage === 'function') {
            // 在uni-app的web-view中，使用postMessage通知外层应用跳转
            uni.postMessage({
                data: {
                    action: 'navigateTo',
                    url: route
                }
            });
        } else if (window.parent !== window) {
            // 在iframe中，尝试修改父窗口的hash
            try {
                window.parent.location.hash = route;
            } catch (e) {
                // 跨域限制，使用postMessage
                window.parent.postMessage({
                    type: 'navigateTo',
                    url: route
                }, '*');
            }
        } else {
            // 在普通浏览器中，直接使用hash路由跳转
            window.location.hash = route;
        }
    } else {
        console.error(`未知的页面: ${page}`);
    }
}

// 页面重定向函数（替换当前页面，会更新URL）
function redirectTo(page) {
    const routes = {
        'square': '/pages/square/index',
        'homepage': '/pages/square/homepage/index',
        'profile': '/pages/square/profile/index',
        'mindos': '/pages/square/mindos/index',
        'wittgenstein': '/pages/square/wittgenstein/index',
        'following': '/pages/square/following/index',
        'messages': '/pages/square/messages/index',
        'consciousness': '/pages/consciousness/index'
    };

    const route = routes[page];
    if (route) {
        // 检测是否在uni-app的web-view中
        if (typeof uni !== 'undefined' && typeof uni.postMessage === 'function') {
            // 在uni-app的web-view中，使用postMessage通知外层应用重定向
            uni.postMessage({
                data: {
                    action: 'redirectTo',
                    url: route
                }
            });
        } else if (window.parent !== window) {
            // 在iframe中，尝试修改父窗口的hash
            try {
                window.parent.location.replace(window.parent.location.origin + '/#' + route);
            } catch (e) {
                // 跨域限制，使用postMessage
                window.parent.postMessage({
                    type: 'redirectTo',
                    url: route
                }, '*');
            }
        } else {
            // 在普通浏览器中，使用replace替换当前历史记录
            window.location.replace(window.location.origin + '/#' + route);
        }
    } else {
        console.error(`未知的页面: ${page}`);
    }
}

// API调用封装
async function apiCall(endpoint, options = {}) {
    const token = getAuthToken();
    const headers = {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
    };

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers: { ...headers, ...options.headers }
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API调用失败:', error);
        throw error;
    }
}

// 页面加载时检查登录状态
window.addEventListener('DOMContentLoaded', () => {
    const user = getCurrentUser();
    if (!user) {
        console.warn('用户未登录');
        // 可以显示登录提示或跳转
    }
});

// 临时Mock数据开关（后端API开发完成后设为false）
const MOCK_ENABLED = false;

// ==================== API调用示例函数 ====================

// 示例：获取帖子列表
async function getPosts(page = 1, pageSize = 10) {
    if (MOCK_ENABLED) {
        // 返回Mock数据
        return {
            success: true,
            data: {
                posts: [],
                total: 0,
                page: page,
                pageSize: pageSize
            }
        };
    } else {
        // 调用真实API
        return await apiCall(`/api/square/posts?page=${page}&page_size=${pageSize}`);
    }
}

// 示例：发布帖子
async function createPost(postData) {
    if (MOCK_ENABLED) {
        return { success: true, data: { id: Date.now() } };
    } else {
        return await apiCall('/api/square/posts', {
            method: 'POST',
            body: JSON.stringify(postData)
        });
    }
}

// 示例：点赞帖子
async function likePost(postId) {
    if (MOCK_ENABLED) {
        return { success: true };
    } else {
        return await apiCall(`/api/square/posts/${postId}/like`, {
            method: 'POST'
        });
    }
}

// 示例：评论帖子
async function commentPost(postId, content) {
    if (MOCK_ENABLED) {
        return { success: true, data: { id: Date.now() } };
    } else {
        return await apiCall(`/api/square/posts/${postId}/comments`, {
            method: 'POST',
            body: JSON.stringify({ content })
        });
    }
}

// 示例：关注用户
async function followUser(userId) {
    if (MOCK_ENABLED) {
        return { success: true };
    } else {
        return await apiCall(`/api/square/users/${userId}/follow`, {
            method: 'POST'
        });
    }
}

// 示例：获取用户信息
async function getUserInfo(userId) {
    if (MOCK_ENABLED) {
        return {
            success: true,
            data: {
                user_id: userId,
                username: '示例用户',
                avatar: `https://picsum.photos/seed/${userId}/200/200`
            }
        };
    } else {
        return await apiCall(`/api/square/users/${userId}`);
    }
}

// 示例：更新用户资料
async function updateUserProfile(profileData) {
    if (MOCK_ENABLED) {
        return { success: true };
    } else {
        return await apiCall('/api/square/users/profile', {
            method: 'PUT',
            body: JSON.stringify(profileData)
        });
    }
}

// ==================== 收藏相关API ====================

/**
 * 切换收藏状态（收藏/取消收藏）
 * @param {number} thoughtId - 思想元胞ID
 * @returns {Promise<Object>} - 返回收藏状态
 */
async function toggleBookmark(thoughtId) {
    const currentUser = getCurrentUser();
    if (!currentUser) {
        throw new Error('用户未登录');
    }

    if (MOCK_ENABLED) {
        // Mock模式：模拟收藏切换
        return {
            success: true,
            data: {
                is_bookmarked: true,
                message: '收藏成功'
            }
        };
    } else {
        // 真实API调用
        return await apiCall(`/api/square/thoughts/${thoughtId}/bookmark?user_id=${currentUser.user_id}`, {
            method: 'POST'
        });
    }
}

/**
 * 获取用户的收藏列表
 * @param {string} userId - 用户ID（可选，默认当前用户）
 * @param {number} page - 页码
 * @param {number} pageSize - 每页数量
 * @returns {Promise<Object>} - 返回收藏列表
 */
async function getBookmarks(userId = null, page = 1, pageSize = 20) {
    const currentUser = getCurrentUser();
    if (!currentUser) {
        throw new Error('用户未登录');
    }

    const targetUserId = userId || currentUser.user_id;

    if (MOCK_ENABLED) {
        // Mock模式：返回空收藏列表
        return {
            success: true,
            data: {
                bookmarks: [],
                total: 0,
                page: page,
                page_size: pageSize,
                has_more: false
            }
        };
    } else {
        // 真实API调用
        return await apiCall(
            `/api/square/bookmarks?user_id=${targetUserId}&current_user_id=${currentUser.user_id}&page=${page}&page_size=${pageSize}`
        );
    }
}

