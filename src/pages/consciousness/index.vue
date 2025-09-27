<template>
  <view class="consciousness-container">
    <!-- 左侧导航栏 -->
    <view class="nav-sidebar">
      <view class="user-info">
        <view class="user-greeting">
          <text class="welcome-text">Welcome back, </text>
          <text class="user-name">{{ userName }}</text>
        </view>
        <text class="logout-link" @click="handleLogout">Logout</text>
      </view>
      
      <view class="nav-stats">
        <view class="stat-item">
          <text class="stat-value">{{ consciousnessLevel }}%</text>
          <text class="stat-label">意识协合度</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ memoryCount }}</text>
          <text class="stat-label">记忆片段</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ interactionCount }}</text>
          <text class="stat-label">互动次数</text>
        </view>
      </view>

      <view class="nav-menu">
        <view class="menu-item" :class="{ active: currentModule === 'knowledge' }" @click="switchModule('knowledge')">
          <text class="iconfont icon-book"></text>
          <text class="menu-text">知识库</text>
          <text class="menu-desc">{{ knowledgePoints }}个知识节点</text>
        </view>
        
        <view class="menu-item" :class="{ active: currentModule === 'memory' }" @click="switchModule('memory')">
          <text class="iconfont icon-memory"></text>
          <text class="menu-text">记忆中心</text>
          <text class="menu-desc">时间线、故事、经历</text>
        </view>
        
        <view class="menu-item" :class="{ active: currentModule === 'personality' }" @click="switchModule('personality')">
          <text class="iconfont icon-personality"></text>
          <text class="menu-text">性格系统</text>
          <text class="menu-desc">特质、偏好、决策模型</text>
        </view>
        
        <view class="menu-item" :class="{ active: currentModule === 'assets' }" @click="switchModule('assets')">
          <text class="iconfont icon-diamond"></text>
          <text class="menu-text">数字资产</text>
          <text class="menu-desc">{{ assetsCount }}个永恒资产</text>
        </view>
        
        <view class="menu-item" :class="{ active: currentModule === 'social' }" @click="switchModule('social')">
          <text class="iconfont icon-network"></text>
          <text class="menu-text">社交网络</text>
          <text class="menu-desc">关系网络图谱</text>
        </view>
      </view>

      <view class="nav-actions">
        <button class="action-btn square-btn" @click="goToSquare">
          <text class="iconfont icon-square"></text>
          云己广场
        </button>
        <button class="action-btn chat-btn" @click="startChat">
          <text class="iconfont icon-message"></text>
          与意识体对话
        </button>
        <button class="action-btn share-btn" @click="shareConsciousness">
          <text class="iconfont icon-share"></text>
          分享意识空间
        </button>
      </view>
    </view>

    <!-- 中间内容区 -->
    <view class="main-content">
      <view class="content-header">
        <text
          class="consciousness-status"
          :class="{ 'dormant-clickable': status === '休眠' }"
          @click="status === '休眠' ? goToCreateMind() : null"
        >
          意识体状态：{{ status }}
        </text>
        <text class="last-sync" v-if="status === '活跃'">上次同步：{{ lastSyncTime }}</text>
      </view>
      
      <!-- 动态内容区，根据currentModule显示不同内容 -->
      <view class="module-content">
        <component :is="currentModuleComponent"></component>
      </view>
    </view>

    <!-- 自定义弹窗 -->
    <CustomModal
      :visible="modal.visible"
      :title="modal.title"
      :content="modal.content"
      :show-cancel="modal.showCancel"
      :cancel-text="modal.cancelText"
      :confirm-text="modal.confirmText"
      :type="modal.type"
      @confirm="handleModalConfirm"
      @cancel="handleModalCancel"
    />
  </view>
</template>

<script>
import { assetsAPI } from '@/utils/api.js'
import authManager from '@/utils/auth.js'
import { get } from '@/utils/request.js'
import { setModalInstance } from '@/utils/modal.js'
import CustomModal from '@/components/CustomModal.vue'
import KnowledgeModule from './knowledge/index.vue'
import MemoryModule from './memory/index.vue'
import PersonalityModule from './personality/index.vue'
import AssetsModule from './assets/index.vue'
import SocialModule from './social/index.vue'

export default {
  components: {
    CustomModal,
    'module-knowledge': KnowledgeModule,
    'module-memory': MemoryModule,
    'module-personality': PersonalityModule,
    'module-assets': AssetsModule,
    'module-social': SocialModule,
  },
  data() {
    return {
      userName: '用户',
      loading: false,
      consciousnessLevel: 0,
      memoryCount: 0,
      interactionCount: 0,
      knowledgePoints: 0,
      assetsCount: 0,
      status: '检查中...',
      lastSyncTime: '2024-03-21 15:30',
      currentModule: 'knowledge',
      isModuleChanging: false,
      dashboardStats: {},
      modal: {
        visible: false,
        title: '',
        content: '',
        showCancel: true,
        cancelText: '取消',
        confirmText: '确定',
        type: 'default',
        onConfirm: null,
        onCancel: null
      }
    }
  },
  async mounted() {
    // 注册全局弹窗实例
    setModalInstance(this)

    // 严格的登录状态检查
    if (!await this.validateLoginStatus()) {
      return
    }

    // 设置用户名
    this.refreshUserInfo()

    // 检查意识体状态
    await this.checkConsciousnessStatus()

    await this.loadDashboardStats()

    // 监听子组件的刷新事件
    uni.$on('refreshDashboardStats', this.loadDashboardStats)
    uni.$on('refreshStats', this.loadDashboardStats)
    uni.$on('refreshUserInfo', this.refreshUserInfo)
  },

  async onShow() {
    // 页面显示时重新验证登录状态
    if (!await this.validateLoginStatus()) {
      return
    }

    // 页面显示时刷新用户信息，确保显示最新的登录用户
    this.refreshUserInfo()
    // 重新检查意识体状态
    await this.checkConsciousnessStatus()
  },

  beforeDestroy() {
    // 移除事件监听器
    uni.$off('refreshDashboardStats', this.loadDashboardStats)
    uni.$off('refreshStats', this.loadDashboardStats)
    uni.$off('refreshUserInfo', this.refreshUserInfo)
  },
  computed: {
    currentModuleComponent() {
      return 'module-' + this.currentModule
    }
  },
  methods: {
    // 加载仪表板统计数据
    async loadDashboardStats() {
      try {
        const stats = await assetsAPI.getDashboardStats()
        this.dashboardStats = stats
        this.consciousnessLevel = stats.consciousness_level || 0
        this.memoryCount = stats.memory_count || 0
        this.interactionCount = stats.interaction_count || 0
        this.knowledgePoints = stats.knowledge_points || 0
        this.assetsCount = stats.assets_count || 0
      } catch (error) {
        console.error('加载统计数据失败:', error)
        // 保持默认值0
      }
    },
    async switchModule(moduleName) {
      if (this.currentModule === moduleName || this.isModuleChanging) return

      this.isModuleChanging = true
      await this.$nextTick()
      this.currentModule = moduleName

      // 切换模块时刷新统计数据
      await this.loadDashboardStats()

      setTimeout(() => {
        this.isModuleChanging = false
      }, 300)
    },

    // 严格验证登录状态（服务端JWT验证）
    async validateLoginStatus() {
      try {
        // 1. 检查本地是否有token
        if (!authManager.isLoggedIn()) {
          console.log('本地登录状态检查失败，跳转到登录页')
          this.redirectToLogin()
          return false
        }

        // 2. 通过调用需要认证的API来验证token有效性
        try {
          const response = await get('/api/minds', {
            page: 1,
            page_size: 1
          })

          // 如果请求成功，说明token有效
          if (response && response.data) {
            return true
          } else {
            console.log('服务端验证失败，token可能无效')
            this.redirectToLogin()
            return false
          }
        } catch (error) {
          // 如果是401错误，说明token无效或过期
          if (error.message === '登录已过期') {
            console.log('Token已过期，已自动清除登录状态')
            return false
          }

          // 其他网络错误，暂时允许通过
          console.warn('服务端登录状态验证失败:', error)
          return true
        }
      } catch (error) {
        console.error('登录状态验证出错:', error)
        this.redirectToLogin()
        return false
      }
    },

    // 跳转到登录页面
    redirectToLogin() {
      this.showModal({
        title: '登录已过期',
        content: '请重新登录以继续使用',
        showCancel: false,
        onConfirm: () => {
          uni.reLaunch({
            url: '/pages/auth/login'
          })
        }
      })
    },

    // 刷新用户信息
    refreshUserInfo() {
      // 重新从authManager获取最新的用户信息
      const currentUser = authManager.getCurrentUser()
      if (currentUser) {
        this.userName = currentUser.username || currentUser.email || '用户'
      }
    },

    // 检查意识体状态
    async checkConsciousnessStatus() {
      try {
        const currentUser = authManager.getCurrentUser()
        if (!currentUser) {
          this.status = '未登录'
          return
        }

        // 使用新的请求工具调用后端API
        const response = await get('/api/minds', {
          page: 1,
          page_size: 1
        })

        if (response && response.data && response.data.code === 200) {
          const mindData = response.data.data

          if (mindData.items && mindData.items.length > 0) {
            // 用户有意识体文件
            this.status = '活跃'
          } else {
            // 用户没有意识体文件
            this.status = '休眠'
          }
        } else {
          // API调用失败，默认为休眠状态
          this.status = '休眠'
          console.warn('查询意识体状态失败，默认为休眠状态')
        }
      } catch (error) {
        console.error('检查意识体状态失败:', error)
        this.status = '休眠'
      }
    },

    // 跳转到创建意识体页面
    goToCreateMind() {
      uni.navigateTo({
        url: '/pages/upload/minddata'
      })
    },

    // 手动刷新统计数据
    async refreshStats() {
      await this.loadDashboardStats()
      uni.showToast({
        title: '数据已刷新',
        icon: 'success'
      })
    },
    startChat() {
      uni.navigateTo({
        url: '/pages/welcome/explore'
      })
    },
    goToSquare() {
      // 跳转到云己广场
      uni.navigateTo({
        url: '/pages/square/index'
      })
    },
    shareConsciousness() {
      this.showModal({
        title: '分享意识空间',
        content: '生成专属链接，让其他用户访问你的公开意识空间？',
        onConfirm: () => {
          uni.setClipboardData({
            data: 'https://dreamfly.ai/consciousness/' + this.userName.toLowerCase().replace(' ', '-'),
            success: () => {
              uni.showToast({
                title: '链接已复制',
                icon: 'success'
              })
            }
          })
        }
      })
    },

    // 处理登出
    handleLogout() {
      this.showModal({
        title: '确认登出',
        content: '确定要退出登录吗？',
        type: 'danger',
        confirmText: '退出登录',
        onConfirm: () => {
          // 清除用户信息和token
          authManager.logout()

          // 显示登出成功提示
          uni.showToast({
            title: '已退出登录',
            icon: 'success',
            duration: 1500
          })

          // 跳转到登录页面
          setTimeout(() => {
            uni.reLaunch({
              url: '/pages/auth/login'
            })
          }, 1500)
        }
      })
    },

    // 自定义弹窗方法
    showModal(options) {
      this.modal = {
        visible: true,
        title: options.title || '提示',
        content: options.content || '',
        showCancel: options.showCancel !== false,
        cancelText: options.cancelText || '取消',
        confirmText: options.confirmText || '确定',
        type: options.type || 'default',
        onConfirm: options.onConfirm || null,
        onCancel: options.onCancel || null
      }
    },

    // 弹窗确认处理
    handleModalConfirm() {
      if (this.modal.onConfirm) {
        this.modal.onConfirm()
      }
      this.modal.visible = false
    },

    // 弹窗取消处理
    handleModalCancel() {
      if (this.modal.onCancel) {
        this.modal.onCancel()
      }
      this.modal.visible = false
    }
  }
}
</script>

<style lang="scss">
.consciousness-container {
  display: flex;
  min-height: 100vh;
  background: #000;
  color: #fff;
}

.nav-sidebar {
  width: 280px;
  background: rgba(255, 255, 255, 0.05);
  padding: 30px 20px;
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.user-info {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .user-greeting {
    display: flex;
    align-items: baseline;
    gap: 4px;

    .welcome-text {
      font-size: 14px;
      color: rgba(255, 255, 255, 0.6);
    }

    .user-name {
      font-size: 24px;
      font-weight: bold;
      color: #fff;
    }
  }

  .logout-link {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.5);
    cursor: pointer;
    transition: all 0.3s ease;
    user-select: none;
    padding: 4px 8px;
    border-radius: 4px;

    &:hover {
      color: rgba(255, 255, 255, 0.8);
      background: rgba(255, 255, 255, 0.05);
    }

    &:active {
      color: rgba(255, 255, 255, 0.6);
      background: rgba(255, 255, 255, 0.02);
    }
  }
}

.nav-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  
  .stat-item {
    flex: 1;
    min-width: 100px;
    background: rgba(255, 255, 255, 0.1);
    padding: 15px;
    border-radius: 12px;
    
    .stat-value {
      font-size: 24px;
      font-weight: bold;
      display: block;
    }
    
    .stat-label {
      font-size: 12px;
      color: rgba(255, 255, 255, 0.6);
      margin-top: 4px;
    }
  }
}

.nav-menu {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
  
  .menu-item {
    padding: 15px;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.3s;
    
    &:hover, &.active {
      background: rgba(255, 255, 255, 0.15);
      transform: translateX(5px);
    }
    
    .menu-text {
      font-size: 16px;
      font-weight: 500;
    }
    
    .menu-desc {
      font-size: 12px;
      color: rgba(255, 255, 255, 0.6);
      margin-top: 4px;
    }
  }
}

.nav-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  
  .action-btn {
    width: 100%;
    padding: 12px;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    background: transparent;
    color: #fff;
    font-size: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    transition: all 0.3s;
    
    &:hover {
      background: rgba(255, 255, 255, 0.2);
    }
    



  }
}

.main-content {
  flex: 1;
  padding: 30px;
  
  .content-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    
    .consciousness-status {
      font-size: 16px;

      &::before {
        content: "";
        display: inline-block;
        width: 8px;
        height: 8px;
        background: #4CAF50;
        border-radius: 50%;
        margin-right: 8px;
      }

      &.dormant-clickable {
        cursor: pointer;
        transition: all 0.3s ease;

        &::before {
          background: #FF9800;
        }

        &:hover {
          color: #FF9800;
          text-shadow: 0 0 5px rgba(255, 152, 0, 0.3);
          transform: translateX(2px);
        }
      }
    }
    
    .last-sync {
      font-size: 14px;
      color: rgba(255, 255, 255, 0.6);
    }
  }
  
  .module-content {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    min-height: calc(100vh - 120px);
    padding: 20px;
    position: relative;
    overflow: hidden;

    .module-enter-active,
    .module-leave-active {
      transition: all 0.3s ease;
    }

    .module-enter-from {
      opacity: 0;
      transform: translateX(30px);
    }

    .module-leave-to {
      opacity: 0;
      transform: translateX(-30px);
    }
  }
}
</style> 