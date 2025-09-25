<template>
  <view class="social-module">
    <view class="module-header">
      <text class="title">权限管理</text>
      <view class="network-stats">
        <view class="stat-item">
          <text class="stat-value">{{ totalConnections }}</text>
          <text class="stat-label">已关联用户</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ inheritorsCount }}</text>
          <text class="stat-label">继承人</text>
        </view>
      </view>
    </view>

    <view class="network-container">
      <view class="network-filters">
        <view class="filter-group">
          <button 
            v-for="(space, index) in accessSpaces"
            :key="index"
            class="filter-btn"
            :class="{ active: currentSpace === space.value }"
            @click="currentSpace = space.value"
          >
            <text class="filter-icon">{{ space.icon }}</text>
            {{ space.name }}
          </button>
        </view>
        <button class="add-user-btn" @click="showAddUserModal = true">
          <text class="btn-icon">+</text>
          添加用户
        </button>
      </view>

      <view class="space-content">
        <view class="space-description">
          <text class="desc-title">{{ getCurrentSpaceInfo.name }}</text>
          <text class="desc-text">{{ getCurrentSpaceInfo.description }}</text>
        </view>

        <view class="users-grid">
          <view 
            v-for="(user, index) in filteredUsers"
            :key="index"
            class="user-card"
            :class="{ 'inheritor': user.isInheritor }"
          >
            <view class="user-avatar">{{ user.avatar }}</view>
            <view class="user-info">
              <text class="user-name">{{ user.name }}</text>
              <text class="user-id">ID: {{ user.accountId }}</text>
              <view class="user-tags">
                <text 
                  v-for="(tag, tagIndex) in user.tags"
                  :key="tagIndex"
                  class="tag"
                >{{ tag }}</text>
              </view>
            </view>
            <view class="user-actions">
              <view class="inheritance-toggle" v-if="currentSpace === 'family'">
                <switch 
                  :checked="user.isInheritor"
                  @change="toggleInheritor(user)"
                />
                <text class="toggle-label">继承人</text>
              </view>
              <button class="remove-btn" @click="removeUser(user)">移除</button>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 添加用户弹窗 -->
    <view class="modal" v-if="showAddUserModal">
      <view class="modal-content">
        <view class="modal-header">
          <text class="modal-title">添加用户</text>
          <button class="close-btn" @click="showAddUserModal = false">×</button>
        </view>
        <view class="modal-body">
          <view class="form-group">
            <text class="label">用户ID</text>
            <input v-model="newUser.accountId" placeholder="请输入用户ID" />
          </view>
          <view class="form-group">
            <text class="label">权限空间</text>
            <select v-model="newUser.space">
              <option 
                v-for="space in accessSpaces" 
                :key="space.value" 
                :value="space.value"
              >
                {{ space.name }}
              </option>
            </select>
          </view>
          <view class="form-group" v-if="newUser.space === 'family'">
            <text class="label">设为继承人</text>
            <switch 
              :checked="newUser.isInheritor"
              @change="(e) => newUser.isInheritor = e.detail.value"
            />
          </view>
        </view>
        <view class="modal-footer">
          <button class="cancel-btn" @click="showAddUserModal = false">取消</button>
          <button class="confirm-btn" @click="addUser">确认添加</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import authManager from '@/utils/auth.js'
import { socialAPI } from '@/utils/api.js'

export default {
  name: 'SocialModule',
  data() {
    return {
      loading: false,
      totalConnections: 0,
      inheritorsCount: 0,
      currentSpace: 'personal',
      showAddUserModal: false,
      accessSpaces: [
        { 
          name: '个人空间', 
          value: 'personal', 
          icon: '🔒',
          description: '仅自己可见的私密空间，包含核心记忆和重要数据'
        },
        { 
          name: '家庭空间', 
          value: 'family', 
          icon: '👨‍👩‍👧‍👦',
          description: '与家人共享的空间，可设置数字遗产继承人'
        },
        { 
          name: '公开空间', 
          value: 'public', 
          icon: '🌏',
          description: '对所有人开放的公共空间，展示您愿意分享的内容'
        }
      ],
      users: [],
      newUser: {
        accountId: '',
        space: 'personal',
        isInheritor: false
      }
    }
  },
  computed: {
    getCurrentSpaceInfo() {
      return this.accessSpaces.find(space => space.value === this.currentSpace)
    },
    filteredUsers() {
      return this.users.filter(user => user.space === this.currentSpace)
    }
  },
  async mounted() {
    // 检查登录状态
    if (!authManager.isLoggedIn()) {
      authManager.requireLogin()
      return
    }

    await this.loadSocialData()
  },
  methods: {
    // 加载社交数据
    async loadSocialData() {
      this.loading = true
      try {
        const currentUserId = authManager.getCurrentUser()?.user_id
        if (!currentUserId) {
          throw new Error('用户未登录')
        }

        // 加载用户权限列表
        const permissions = await socialAPI.getUserPermissions(currentUserId)
        this.users = permissions.map(p => ({
          id: p.id,
          avatar: p.avatar,
          name: p.name,
          accountId: p.account_id,
          space: p.space,
          isInheritor: p.is_inheritor,
          tags: p.tags || []
        }))

        // 加载统计数据
        const stats = await socialAPI.getSocialStats(currentUserId)
        this.totalConnections = stats.total_connections
        this.inheritorsCount = stats.inheritors_count

      } catch (error) {
        console.error('加载社交数据失败:', error)
        uni.showToast({
          title: '加载数据失败',
          icon: 'error'
        })
      } finally {
        this.loading = false
      }
    },

    updateStats() {
      this.totalConnections = this.users.length
      this.inheritorsCount = this.users.filter(user => user.isInheritor).length
    },
    async toggleInheritor(user) {
      try {
        const currentUserId = authManager.getCurrentUser()?.user_id
        if (!currentUserId) {
          throw new Error('用户未登录')
        }

        const newInheritorStatus = !user.isInheritor
        await socialAPI.updateUserPermission(currentUserId, user.id, {
          is_inheritor: newInheritorStatus
        })

        // 更新本地数据
        user.isInheritor = newInheritorStatus
        if (user.isInheritor) {
          user.tags = [...user.tags.filter(tag => tag !== '继承人'), '继承人']
        } else {
          user.tags = user.tags.filter(tag => tag !== '继承人')
        }
        this.updateStats()

        uni.showToast({
          title: newInheritorStatus ? '已设为继承人' : '已取消继承人',
          icon: 'success'
        })
      } catch (error) {
        console.error('更新继承人状态失败:', error)
        uni.showToast({
          title: '操作失败',
          icon: 'error'
        })
      }
    },
    async removeUser(user) {
      try {
        const currentUserId = authManager.getCurrentUser()?.user_id
        if (!currentUserId) {
          throw new Error('用户未登录')
        }

        await socialAPI.removeUserPermission(currentUserId, user.id)

        // 更新本地数据
        const index = this.users.indexOf(user)
        if (index > -1) {
          this.users.splice(index, 1)
          this.updateStats()
        }

        uni.showToast({
          title: '移除成功',
          icon: 'success'
        })
      } catch (error) {
        console.error('移除用户失败:', error)
        uni.showToast({
          title: '移除失败',
          icon: 'error'
        })
      }
    },
    async addUser() {
      if (!this.newUser.accountId) {
        uni.showToast({
          title: '请输入用户ID',
          icon: 'none'
        })
        return
      }

      try {
        uni.showLoading({ title: '添加中...' })

        const currentUserId = authManager.getCurrentUser()?.user_id
        if (!currentUserId) {
          throw new Error('用户未登录')
        }

        // 调用API添加用户
        const result = await socialAPI.addUser(currentUserId, {
          accountId: this.newUser.accountId,
          space: this.newUser.space,
          isInheritor: this.newUser.space === 'family' && this.newUser.isInheritor
        })

        // 添加到本地列表
        const newUser = {
          id: result.id,
          avatar: result.avatar,
          name: result.name,
          accountId: result.account_id,
          space: result.space,
          isInheritor: result.is_inheritor,
          tags: result.tags || []
        }

        this.users.push(newUser)
        this.updateStats()

        uni.hideLoading()
        uni.showToast({
          title: '添加成功',
          icon: 'success'
        })

        // 关闭弹窗并重置表单
        this.showAddUserModal = false
        this.newUser = {
          accountId: '',
          space: 'personal',
          isInheritor: false
        }
      } catch (error) {
        uni.hideLoading()
        console.error('添加用户失败:', error)
        uni.showToast({
          title: error.message || '添加失败',
          icon: 'error'
        })
      }
    }
  },
  mounted() {
    this.updateStats()
  }
}
</script>

<style lang="scss">
.social-module {
  height: 100%;
  
  .module-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    
    .title {
      font-size: 24px;
      font-weight: bold;
    }
    
    .network-stats {
      display: flex;
      gap: 24px;
      
      .stat-item {
        text-align: right;
        
        .stat-value {
          font-size: 20px;
          font-weight: 500;
          display: block;
        }
        
        .stat-label {
          font-size: 14px;
          color: rgba(255, 255, 255, 0.6);
        }
      }
    }
  }
  
  .network-container {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 24px;
    
    .network-filters {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
      
      .filter-group {
        display: flex;
        gap: 12px;
      }
      
      .filter-btn, .add-user-btn {
        background: transparent;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: #fff;
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 14px;
        display: flex;
        align-items: center;
        gap: 6px;
        transition: all 0.3s;
        
        &:hover, &.active {
          background: rgba(255, 255, 255, 0.1);
        }
        
        .filter-icon, .btn-icon {
          font-size: 16px;
        }
      }
      
      .add-user-btn {
        background: rgba(255, 255, 255, 0.1);
      }
    }
    
    .space-content {
      .space-description {
        margin-bottom: 24px;
        padding: 16px;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 12px;
        
        .desc-title {
          font-size: 18px;
          font-weight: 500;
          margin-bottom: 8px;
          display: block;
        }
        
        .desc-text {
          font-size: 14px;
          color: rgba(255, 255, 255, 0.6);
          line-height: 1.4;
        }
      }
      
      .users-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 16px;
        
        .user-card {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 12px;
          padding: 16px;
          display: flex;
          gap: 16px;
          
          &.inheritor {
            border: 1px solid rgba(255, 255, 255, 0.3);
            background: rgba(255, 255, 255, 0.08);
          }
          
          .user-avatar {
            font-size: 32px;
            width: 48px;
            height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 24px;
          }
          
          .user-info {
            flex: 1;
            
            .user-name {
              font-size: 16px;
              font-weight: 500;
              margin-bottom: 4px;
              display: block;
            }
            
            .user-id {
              font-size: 14px;
              color: rgba(255, 255, 255, 0.6);
              margin-bottom: 8px;
              display: block;
            }
            
            .user-tags {
              display: flex;
              gap: 8px;
              flex-wrap: wrap;
              
              .tag {
                font-size: 12px;
                color: rgba(255, 255, 255, 0.8);
                background: rgba(255, 255, 255, 0.1);
                padding: 2px 8px;
                border-radius: 4px;
              }
            }
          }
          
          .user-actions {
            display: flex;
            flex-direction: column;
            gap: 8px;
            
            .inheritance-toggle {
              display: flex;
              align-items: center;
              gap: 8px;
              
              .toggle-label {
                font-size: 14px;
                color: rgba(255, 255, 255, 0.8);
              }
            }
            
            .remove-btn {
              background: rgba(255, 255, 255, 0.1);
              border: none;
              color: #ff4d4f;
              padding: 4px 8px;
              border-radius: 4px;
              font-size: 14px;
              
              &:hover {
                background: rgba(255, 77, 79, 0.1);
              }
            }
          }
        }
      }
    }
  }
  
  .modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    
    .modal-content {
      background: #1f1f1f;
      border-radius: 16px;
      width: 400px;
      
      .modal-header {
        padding: 16px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
        
        .modal-title {
          font-size: 18px;
          font-weight: 500;
        }
        
        .close-btn {
          background: transparent;
          border: none;
          color: rgba(255, 255, 255, 0.6);
          font-size: 20px;
          cursor: pointer;
          
          &:hover {
            color: #fff;
          }
        }
      }
      
      .modal-body {
        padding: 16px;
        
        .form-group {
          margin-bottom: 16px;
          
          .label {
            display: block;
            font-size: 14px;
            margin-bottom: 8px;
            color: rgba(255, 255, 255, 0.8);
          }
          
          input, select {
            width: 100%;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            padding: 8px 12px;
            color: #fff;
            font-size: 14px;

            &:focus {
              border-color: rgba(255, 255, 255, 0.3);
              outline: none;
            }
          }

          select {
            option {
              background: #2a2a2a;
              color: #fff;
              padding: 8px 12px;

              &:hover {
                background: #3a3a3a;
              }

              &:checked {
                background: #4a4a4a;
              }
            }
          }
        }
      }
      
      .modal-footer {
        padding: 16px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        justify-content: flex-end;
        gap: 12px;
        
        button {
          padding: 8px 16px;
          border-radius: 8px;
          font-size: 14px;
          
          &.cancel-btn {
            background: transparent;
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #fff;
            
            &:hover {
              background: rgba(255, 255, 255, 0.1);
            }
          }
          
          &.confirm-btn {
            background: #1890ff;
            border: none;
            color: #fff;
            
            &:hover {
              background: #40a9ff;
            }
          }
        }
      }
    }
  }
}
</style> 