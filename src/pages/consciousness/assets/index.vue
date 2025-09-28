<template>
  <view class="digital-assets">
    <view class="module-header">
      <text class="title">数字资产管理</text>
      <view class="asset-stats">
        <view class="stat-item">
          <text class="stat-value">{{ totalAssetValue }}</text>
          <text class="stat-label">总资产估值</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ monthlyRevenue }}</text>
          <text class="stat-label">月度收益</text>
        </view>
      </view>
    </view>

    <view class="assets-container">
      <!-- 意识体看板 -->
      <view class="consciousness-dashboard">
        <view class="section-header">
          <text class="section-title">意识体看板</text>
          <view class="dashboard-tabs">
            <button 
              class="tab-btn"
              :class="{ active: currentTab === 'owned' }"
              @click="currentTab = 'owned'"
            >
              我的意识体
            </button>
            <button 
              class="tab-btn"
              :class="{ active: currentTab === 'purchased' }"
              @click="currentTab = 'purchased'"
            >
              已获取意识体
            </button>
          </view>
        </view>

        <view class="consciousness-cards">
          <view v-if="loading" class="loading-container">
            <text class="loading-text">加载中...</text>
          </view>
          <view v-else-if="currentConsciousness.length === 0" class="empty-container">
            <text class="empty-text">暂无数据</text>
          </view>
          <view
            v-else
            v-for="(consciousness, index) in currentConsciousness"
            :key="consciousness.id || index"
            class="consciousness-detail-card"
          >
            <view class="card-main">
              <view class="consciousness-avatar">
                <image 
                  :src="consciousness.avatar || '/static/avatar.jpg'"
                  class="avatar-img"
                />
                <view 
                  class="status-indicator"
                  :class="consciousness.status"
                ></view>
              </view>
              <view class="consciousness-info">
                <view class="info-header">
                  <text class="consciousness-name">{{ consciousness.name }}</text>
                  <view class="header-actions">
                    <text class="consciousness-type">{{ consciousness.type }}</text>
                    <button
                      class="action-btn publish"
                      :class="{ 'published': consciousness.status === 'active' }"
                      @click="togglePublish(consciousness)"
                    >
                      {{ consciousness.status === 'active' ? '下架' : '发布' }}
                    </button>
                  </view>
                </view>
                <text class="consciousness-desc">{{ consciousness.description }}</text>
                <view class="consciousness-attributes">
                  <view class="attribute-item">
                    <text class="attribute-icon">🧠</text>
                    <text class="attribute-label">意识完整度</text>
                    <text class="attribute-value">{{ consciousness.completeness || 0 }}%</text>
                  </view>
                  <view class="attribute-item">
                    <text class="attribute-icon">⚡</text>
                    <text class="attribute-label">活跃度</text>
                    <text class="attribute-value">{{ consciousness.activity || 0 }}%</text>
                  </view>
                  <view class="attribute-item">
                    <text class="attribute-icon">🔄</text>
                    <text class="attribute-label">同步状态</text>
                    <text class="attribute-value">{{ consciousness.syncStatus || '未知' }}</text>
                  </view>
                </view>
                <view class="tags-container">
                  <view 
                    v-for="(tag, tagIndex) in consciousness.tags"
                    :key="tagIndex"
                    class="tag"
                  >
                    {{ tag }}
                  </view>
                </view>
              </view>
            </view>
            
            <!-- 定价设置部分 -->
            <view class="pricing-section" v-if="currentTab === 'owned'">
              <view class="pricing-header">
                <text class="pricing-title">定价设置</text>
                <button 
                  class="edit-btn"
                  @click="togglePricingEdit(consciousness)"
                >
                  {{ consciousness.isEditing ? '保存' : '编辑' }}
                </button>
              </view>
              <view class="pricing-options">
                <view class="price-option">
                  <checkbox 
                    v-model="consciousness.pricingModel.preview.enabled"
                    :disabled="!consciousness.isEditing"
                  />
                  <text class="option-label">免费阅览</text>
                  <input 
                    v-if="consciousness.pricingModel.preview.enabled"
                    type="number"
                    v-model="consciousness.pricingModel.preview.duration"
                    :disabled="!consciousness.isEditing"
                    class="duration-input"
                    placeholder="试用时长(分钟)"
                  />
                </view>
                <view class="price-option">
                  <checkbox 
                    v-model="consciousness.pricingModel.rent.enabled"
                    :disabled="!consciousness.isEditing"
                  />
                  <text class="option-label">租赁模式</text>
                  <input 
                    v-if="consciousness.pricingModel.rent.enabled"
                    type="number"
                    v-model="consciousness.pricingModel.rent.price"
                    :disabled="!consciousness.isEditing"
                    class="price-input"
                    placeholder="每月租金"
                  />
                </view>
                <view class="price-option">
                  <checkbox 
                    v-model="consciousness.pricingModel.buy.enabled"
                    :disabled="!consciousness.isEditing"
                  />
                  <text class="option-label">买断模式</text>
                  <input 
                    v-if="consciousness.pricingModel.buy.enabled"
                    type="number"
                    v-model="consciousness.pricingModel.buy.price"
                    :disabled="!consciousness.isEditing"
                    class="price-input"
                    placeholder="买断价格"
                  />
                </view>
              </view>
            </view>

            <view class="card-footer">
              <view class="stats">
                <view class="stat-item">
                  <text class="stat-value">{{ consciousness.interactions }}</text>
                  <text class="stat-label">互动次数</text>
                </view>
                <view class="stat-item">
                  <text class="stat-value">{{ consciousness.rating }}</text>
                  <text class="stat-label">评分</text>
                </view>
                <view class="stat-item">
                  <text class="stat-value">{{ consciousness.lastSync }}</text>
                  <text class="stat-label">最近同步</text>
                </view>
              </view>
              <view class="actions">
                <button 
                  class="action-btn sync"
                  @click="syncConsciousness(consciousness)"
                >
                  同步
                </button>
                <button 
                  class="action-btn interact"
                  @click="interactWithConsciousness(consciousness)"
                >
                  对话
                </button>
                <button 
                  class="action-btn more"
                  @click="showMoreOptions(consciousness)"
                >
                  更多
                </button>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 数字凭证托管 -->
      <view class="credentials-section">
        <view class="section-header">
          <text class="section-title">数字凭证托管</text>
          <text class="section-desc">安全加密存储您的数字身份</text>
        </view>
        <view class="credentials-grid">
          <view 
            v-for="(platform, index) in platforms"
            :key="index"
            class="platform-card"
            :class="{ 'is-connected': platform.isConnected }"
          >
            <text class="platform-icon">{{ platform.icon }}</text>
            <view class="platform-info">
              <text class="platform-name">{{ platform.name }}</text>
              <text class="platform-status">{{ platform.isConnected ? '已连接' : '未连接' }}</text>
            </view>
            <button 
              class="platform-action"
              @click="handlePlatformAction(platform)"
            >
              {{ platform.isConnected ? '管理' : '连接' }}
            </button>
          </view>
        </view>
      </view>

      <!-- 思想资产评估 -->
      <view class="valuation-section">
        <view class="section-header">
          <text class="section-title">思想资产评估</text>
          <text class="section-desc">基于AI的数据价值分析</text>
        </view>
        <view class="valuation-cards">
          <view class="valuation-card knowledge">
            <text class="card-title">知识储备</text>
            <text class="value-score">{{ knowledgeScore }}</text>
            <view class="value-metrics">
              <view class="metric-item">
                <text class="metric-label">专业深度</text>
                <text class="metric-value">{{ metrics.professionalDepth }}</text>
              </view>
              <view class="metric-item">
                <text class="metric-label">知识广度</text>
                <text class="metric-value">{{ metrics.knowledgeBreadth }}</text>
              </view>
            </view>
          </view>
          <view class="valuation-card experience">
            <text class="card-title">经验价值</text>
            <text class="value-score">{{ experienceScore }}</text>
            <view class="value-metrics">
              <view class="metric-item">
                <text class="metric-label">实践经验</text>
                <text class="metric-value">{{ metrics.practicalExperience }}</text>
              </view>
              <view class="metric-item">
                <text class="metric-label">创新能力</text>
                <text class="metric-value">{{ metrics.innovationCapability }}</text>
              </view>
            </view>
          </view>
          <view class="valuation-card potential">
            <text class="card-title">发展潜力</text>
            <text class="value-score">{{ potentialScore }}</text>
            <view class="value-metrics">
              <view class="metric-item">
                <text class="metric-label">成长趋势</text>
                <text class="metric-value">{{ metrics.growthTrend }}</text>
              </view>
              <view class="metric-item">
                <text class="metric-label">市场价值</text>
                <text class="metric-value">{{ metrics.marketValue }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 意识体市场 -->
      <view class="market-section">
        <view class="section-header">
          <text class="section-title">意识体市场</text>
          <text class="section-desc">发现和获取优质意识资产</text>
        </view>
        <view class="market-filters">
          <input 
            type="text" 
            class="search-input"
            v-model="searchQuery"
            placeholder="搜索意识体..."
          >
          <select v-model="selectedCategory" class="category-select">
            <option value="">全部类别</option>
            <option 
              v-for="category in categories"
              :key="category.value"
              :value="category.value"
            >
              {{ category.label }}
            </option>
          </select>
        </view>
        <view class="consciousness-grid">
          <view 
            v-for="(item, index) in filteredMarketItems"
            :key="index"
            class="consciousness-card"
          >
            <view class="card-header">
              <text class="consciousness-name">{{ item.name }}</text>
              <text class="consciousness-price">{{ formatPrice(item.price) }}</text>
            </view>
            <text class="consciousness-desc">{{ item.description }}</text>
            <view class="consciousness-stats">
              <view class="stat-item">
                <text class="stat-label">评分</text>
                <text class="stat-value">{{ item.rating }}/10</text>
              </view>
              <view class="stat-item">
                <text class="stat-label">类型</text>
                <text class="stat-value">{{ item.type }}</text>
              </view>
            </view>
            <view class="card-actions">
              <button 
                class="action-btn preview"
                @click="previewConsciousness(item)"
              >
                预览
              </button>
              <button 
                class="action-btn"
                :class="item.purchaseType"
                @click="handlePurchase(item)"
              >
                {{ item.purchaseType === 'buy' ? '购买' : '租赁' }}
              </button>
            </view>
          </view>
        </view>
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
      :mask-closable="true"
      @confirm="handleModalConfirm"
      @cancel="handleModalCancel"
    />
  </view>
</template>

<script>
import { assetsAPI, transactionAPI } from '@/utils/api.js'
import CustomModal from '@/components/CustomModal.vue'
import { buildApiUrl } from '@/utils/config.js'

export default {
  name: 'DigitalAssets',
  components: {
    CustomModal
  },
  data() {
    return {
      loading: false,
      totalAssetValue: '¥0',
      monthlyRevenue: '¥0',
      dashboardStats: {},
      myConsciousness: [],
      searchQuery: '',
      selectedCategory: '',
      knowledgeScore: 0,
      experienceScore: 0,
      potentialScore: 0,
      metrics: {
        professionalDepth: '待评估',
        knowledgeBreadth: '待评估',
        practicalExperience: '待评估',
        innovationCapability: '待评估',
        growthTrend: '待评估',
        marketValue: '待评估'
      },
      platforms: [
        {
          icon: '🔑',
          name: 'DreamID',
          isConnected: false
        },
        {
          icon: '💼',
          name: '专业认证',
          isConnected: false
        },
        {
          icon: '🌐',
          name: '社交账号',
          isConnected: false
        },
        {
          icon: '📱',
          name: '数字身份',
          isConnected: false
        }
      ],
      categories: [
        { label: '专业技能', value: '专业技能' },
        { label: '创意艺术', value: '创意艺术' },
        { label: '科研学术', value: '科研学术' },
        { label: '商业洞见', value: '商业洞见' },
        { label: '个人助手', value: '个人助手' },
        { label: '测试类型', value: '测试类型' }
      ],
      marketItems: [],
      currentTab: 'owned',
      ownedConsciousness: [],
      purchasedConsciousness: [],
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
    await this.loadData()
  },
  computed: {
    filteredMarketItems() {
      return this.marketItems.filter(item => {
        const matchesSearch = item.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
                            item.description.toLowerCase().includes(this.searchQuery.toLowerCase())
        const matchesCategory = !this.selectedCategory || item.type === this.selectedCategory
        return matchesSearch && matchesCategory
      })
    },
    currentConsciousness() {
      return this.currentTab === 'owned' ? this.ownedConsciousness : this.purchasedConsciousness
    }
  },
  methods: {
    // 加载所有数据
    async loadData() {
      this.loading = true
      try {
        await Promise.all([
          this.loadDashboardStats(),
          this.loadUserAssets(),
          this.loadMarketItems()
        ])
      } catch (error) {
        console.error('加载数据失败:', error)
        uni.showToast({
          title: '数据加载失败',
          icon: 'error'
        })
      } finally {
        this.loading = false
      }
    },

    // 加载仪表板统计数据
    async loadDashboardStats() {
      try {
        const stats = await assetsAPI.getDashboardStats()
        this.dashboardStats = stats
        this.totalAssetValue = `¥${(stats.total_revenue || 0).toLocaleString()}`
        this.monthlyRevenue = `¥${(stats.monthly_revenue || 0).toLocaleString()}`
      } catch (error) {
        console.error('加载统计数据失败:', error)
      }
    },

    // 加载用户意识体（从minds表）
    async loadUserAssets() {
      try {
        const { get } = await import('@/utils/request.js');
        const response = await get('/api/minds', {
          page: 1,
          page_size: 100  // 获取所有用户的意识体
        });

        if (response && response.data && response.data.code === 200) {
          const mindData = response.data.data;
          if (mindData.items && mindData.items.length > 0) {
            // 将minds数据转换为前端需要的格式
            this.ownedConsciousness = await Promise.all(mindData.items.map(async (mind) => {
              // 获取mind文件内容以提取头像
              let avatar = '/static/avatar.jpg'; // 默认头像
              try {
                const mindContentResponse = await uni.request({
                  url: buildApiUrl(`/api/mind/${mind.filename}`),
                  method: 'GET'
                });

                if (mindContentResponse.data && mindContentResponse.data.code === 200) {
                  let content = mindContentResponse.data.data;
                  if (content.includes('export default')) {
                    content = content.replace(/export\s+default\s+/, '').trim();
                  }
                  const mindFileData = JSON.parse(content);

                  // 检查是否有image_data字段
                  if (mindFileData.metadata && mindFileData.metadata.image_data) {
                    // 如果image_data已经是完整的data URL，直接使用
                    if (mindFileData.metadata.image_data.startsWith('data:')) {
                      avatar = mindFileData.metadata.image_data;
                    } else {
                      // 如果只是base64编码，添加data URL前缀
                      avatar = `data:image/jpeg;base64,${mindFileData.metadata.image_data}`;
                    }
                  }
                }
              } catch (error) {
                console.error('获取mind文件头像失败:', error);
              }

              return {
                id: mind.id,
                name: mind.name,
                type: mind.type || 'MindCopy',
                description: `创建于 ${mind.birth || '未知'}`,
                avatar: avatar, // 使用从mind文件中提取的头像
                completeness: 100, // mind文件默认完整
                activity: 85, // 默认活跃度
                syncStatus: 'synced',
                status: 'active',
                tags: [mind.protocol || 'MCP-v1', mind.blockchain || 'ethereum'],
                interactions: 0,
                rating: 9.5,
                lastSync: this.formatTime(mind.updated_at),
                isEditing: false,
                filename: mind.filename, // 保存文件名用于删除
                pricingModel: {
                  preview: { enabled: false, duration: 0 },
                  rent: { enabled: false, price: 0 },
                  buy: { enabled: false, price: 0 }
                }
              };
            }));
            console.log('加载用户意识体成功:', this.ownedConsciousness);
          } else {
            this.ownedConsciousness = [];
          }
        }
      } catch (error) {
        console.error('加载用户意识体失败:', error)
        this.ownedConsciousness = []
      }
    },

    // 加载市场商品
    async loadMarketItems() {
      try {
        const items = await transactionAPI.getMarketItems(20)
        this.marketItems = items.map(item => ({
          id: item.id,
          name: item.name,
          price: this.getItemPrice(item.pricing_model),
          description: item.description,
          rating: item.rating,
          type: item.type,
          purchaseType: this.getItemPurchaseType(item.pricing_model)
        }))
      } catch (error) {
        console.error('加载市场商品失败:', error)
      }
    },

    // 获取商品价格
    getItemPrice(pricingModel) {
      if (!pricingModel) return 0
      if (pricingModel.buy && pricingModel.buy.enabled) {
        return pricingModel.buy.price
      }
      if (pricingModel.rent && pricingModel.rent.enabled) {
        return pricingModel.rent.price
      }
      return 0
    },

    // 获取商品购买类型
    getItemPurchaseType(pricingModel) {
      if (!pricingModel) return 'buy'
      if (pricingModel.buy && pricingModel.buy.enabled) {
        return 'buy'
      }
      if (pricingModel.rent && pricingModel.rent.enabled) {
        return 'rent'
      }
      return 'buy'
    },

    // 格式化时间
    formatTime(timeStr) {
      if (!timeStr) return '未知'
      const now = new Date()
      const time = new Date(timeStr)
      const diff = now - time
      const minutes = Math.floor(diff / 60000)

      if (minutes < 1) return '刚刚'
      if (minutes < 60) return `${minutes}分钟前`
      if (minutes < 1440) return `${Math.floor(minutes / 60)}小时前`
      return `${Math.floor(minutes / 1440)}天前`
    },
    getStatusText(status) {
      const statusMap = {
        published: '已发布',
        draft: '草稿',
        reviewing: '审核中'
      }
      return statusMap[status] || status
    },
    async togglePricingEdit(consciousness) {
      if (consciousness.isEditing) {
        // 保存定价设置
        try {
          await assetsAPI.updateAsset(consciousness.id, {
            pricing_model: consciousness.pricingModel
          })
          uni.showToast({
            title: '定价设置已保存',
            icon: 'success'
          })
        } catch (error) {
          console.error('保存定价设置失败:', error)
          uni.showToast({
            title: '保存失败',
            icon: 'error'
          })
          return
        }
      }
      consciousness.isEditing = !consciousness.isEditing
    },
    async togglePublish(consciousness) {
      try {
        const newStatus = consciousness.status === 'active' ? 'inactive' : 'active'
        await assetsAPI.updateAsset(consciousness.id, {
          status: newStatus
        })
        consciousness.status = newStatus
        uni.showToast({
          title: newStatus === 'active' ? '已发布' : '已下架',
          icon: 'success'
        })
      } catch (error) {
        console.error('更新发布状态失败:', error)
        uni.showToast({
          title: '操作失败',
          icon: 'error'
        })
      }
    },
    previewAsset(asset) {
      // 预览意识体资产
    },
    handlePlatformAction(platform) {
      // 处理平台连接/管理逻辑
    },
    formatPrice(price) {
      return `¥${price.toLocaleString()}`
    },
    previewConsciousness(item) {
      // 预览意识体逻辑
    },
    handlePurchase(item) {
      // 处理购买/租赁逻辑
    },
    async syncConsciousness(consciousness) {
      // 同步意识体数据
      consciousness.syncStatus = '同步中'
      consciousness.status = 'syncing'

      try {
        // 这里可以调用同步API
        await new Promise(resolve => setTimeout(resolve, 2000)) // 模拟同步过程

        consciousness.syncStatus = '已同步'
        consciousness.status = 'active'
        consciousness.lastSync = '刚刚'

        uni.showToast({
          title: '同步完成',
          icon: 'success'
        })
      } catch (error) {
        consciousness.syncStatus = '同步失败'
        consciousness.status = 'error'
        console.error('同步失败:', error)
        uni.showToast({
          title: '同步失败',
          icon: 'error'
        })
      }
    },
    interactWithConsciousness(consciousness) {
      // 跳转到意识体对话页面
      uni.navigateTo({
        url: `/pages/consciousness/interaction/index?file=${encodeURIComponent(consciousness.filename)}`
      });
    },
    showMoreOptions(consciousness) {
      // 显示操作选项弹窗
      this.showModal({
        title: '意识体操作',
        content: `选择对"${consciousness.name}"的操作：`,
        showCancel: true,
        cancelText: '编辑',
        confirmText: '删除',
        type: 'danger',
        onConfirm: () => {
          this.deleteConsciousness(consciousness);
        },
        onCancel: () => {
          this.editConsciousness(consciousness);
        }
      });
    },

    // 编辑意识体
    editConsciousness(consciousness) {
      // 跳转到编辑页面
      uni.navigateTo({
        url: `/pages/upload/minddata?edit=true&id=${consciousness.id}`
      });
    },

    // 删除意识体
    async deleteConsciousness(consciousness) {
      this.showModal({
        title: '确认删除',
        content: `确定要删除意识体"${consciousness.name}"吗？此操作不可恢复。`,
        type: 'danger',
        confirmText: '删除',
        onConfirm: async () => {
          try {
            // 调用删除API
            const response = await uni.request({
              url: buildApiUrl(`/api/mind/${consciousness.id}`),
              method: 'DELETE'
            });

            if (response.data && response.data.code === 200) {
              uni.showToast({
                title: '删除成功',
                icon: 'success'
              });
              // 重新加载意识体列表
              await this.loadUserAssets();
              // 刷新父页面统计数据
              uni.$emit('refreshDashboardStats');
            } else {
              throw new Error(response.data?.msg || '删除失败');
            }
          } catch (error) {
            console.error('删除意识体失败:', error);
            uni.showToast({
              title: '删除失败',
              icon: 'error'
            });
          }
        }
      });
    },

    // 导出意识体
    exportConsciousness(consciousness) {
      uni.showToast({
        title: '导出功能开发中',
        icon: 'none'
      });
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
.digital-assets {
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
    
    .asset-stats {
      display: flex;
      gap: 20px;
      
      .stat-item {
        text-align: right;
        
        .stat-value {
          font-size: 24px;
          font-weight: bold;
          color: #1890ff;
          display: block;
        }
        
        .stat-label {
          font-size: 14px;
          color: rgba(255, 255, 255, 0.6);
        }
      }
    }
  }
  
  .assets-container {
    display: grid;
    gap: 30px;
    
    .section-header {
      margin-bottom: 20px;
      
      .section-title {
        font-size: 18px;
        font-weight: 500;
        margin-bottom: 4px;
        display: block;
      }
      
      .section-desc {
        font-size: 14px;
        color: rgba(255, 255, 255, 0.6);
      }
    }
    
    .consciousness-dashboard {
      margin-bottom: 30px;
      
      .dashboard-tabs {
        display: flex;
        gap: 16px;
        margin-top: 12px;
        
        .tab-btn {
          padding: 8px 20px;
          border-radius: 8px;
          font-size: 14px;
          background: transparent;
          border: 1px solid rgba(255, 255, 255, 0.2);
          color: rgba(255, 255, 255, 0.8);
          cursor: pointer;
          transition: all 0.3s;
          
          &:hover {
            background: rgba(255, 255, 255, 0.05);
          }
          
          &.active {
            background: #1890ff;
            border-color: #1890ff;
            color: #fff;
          }
        }
      }
      
      .consciousness-cards {
        display: grid;
        gap: 24px;
        margin-top: 24px;

        .loading-container,
        .empty-container {
          text-align: center;
          padding: 60px 20px;

          .loading-text,
          .empty-text {
            font-size: 16px;
            color: rgba(255, 255, 255, 0.6);
          }
        }
        
        .consciousness-detail-card {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 16px;
          padding: 24px;
          
          .card-main {
            display: flex;
            gap: 24px;
            margin-bottom: 24px;
            
            .consciousness-avatar {
              position: relative;
              
              .avatar-img {
                width: 120px;
                height: 120px;
                border-radius: 16px;
                object-fit: cover;
              }
              
              .status-indicator {
                position: absolute;
                bottom: 8px;
                right: 8px;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                border: 2px solid rgba(0, 0, 0, 0.2);
                
                &.active {
                  background: #52c41a;
                }
                
                &.syncing {
                  background: #faad14;
                  animation: pulse 1.5s infinite;
                }
                
                &.inactive {
                  background: #ff4d4f;
                }
              }
            }
            
            .consciousness-info {
              flex: 1;
              
              .info-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 12px;
                
                .consciousness-name {
                  font-size: 20px;
                  font-weight: 500;
                }
                
                .header-actions {
                  display: flex;
                  align-items: center;
                  gap: 12px;
                  
                  .action-btn.publish {
                    padding: 4px 12px;
                    border-radius: 6px;
                    font-size: 14px;
                    background: #1890ff;
                    color: #fff;
                    border: none;
                    cursor: pointer;
                    
                    &:hover {
                      background: #40a9ff;
                    }
                    
                    &.published {
                      background: #ff4d4f;
                      
                      &:hover {
                        background: #ff7875;
                      }
                    }
                  }
                }
              }
              
              .consciousness-desc {
                font-size: 14px;
                color: rgba(255, 255, 255, 0.6);
                line-height: 1.5;
                margin-bottom: 16px;
              }
              
              .consciousness-attributes {
                display: flex;
                gap: 24px;
                margin-bottom: 16px;
                
                .attribute-item {
                  display: flex;
                  align-items: center;
                  gap: 8px;
                  
                  .attribute-icon {
                    font-size: 16px;
                  }
                  
                  .attribute-label {
                    font-size: 14px;
                    color: rgba(255, 255, 255, 0.4);
                  }
                  
                  .attribute-value {
                    font-size: 14px;
                    color: #1890ff;
                    font-weight: 500;
                  }
                }
              }
              
              .tags-container {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                
                .tag {
                  padding: 4px 12px;
                  border-radius: 12px;
                  font-size: 12px;
                  background: rgba(255, 255, 255, 0.05);
                  color: rgba(255, 255, 255, 0.8);
                }
              }
            }
          }
          
          .pricing-section {
            background: rgba(255, 255, 255, 0.02);
            border-radius: 12px;
            padding: 16px;
            margin: 16px 0;
            
            .pricing-header {
              display: flex;
              justify-content: space-between;
              align-items: center;
              margin-bottom: 16px;
              
              .pricing-title {
                font-size: 16px;
                font-weight: 500;
              }
              
              .edit-btn {
                padding: 4px 12px;
                border-radius: 6px;
                font-size: 14px;
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 0.2);
                color: #fff;
                cursor: pointer;
                
                &:hover {
                  background: rgba(255, 255, 255, 0.05);
                }
              }
            }
            
            .pricing-options {
              display: grid;
              gap: 16px;
              
              .price-option {
                display: flex;
                align-items: center;
                gap: 12px;
                
                .option-label {
                  font-size: 14px;
                  color: rgba(255, 255, 255, 0.8);
                  min-width: 80px;
                }
                
                .price-input,
                .duration-input {
                  background: rgba(255, 255, 255, 0.1);
                  border: 1px solid rgba(255, 255, 255, 0.2);
                  border-radius: 6px;
                  padding: 6px 12px;
                  color: #fff;
                  font-size: 14px;
                  width: 120px;
                  
                  &:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                  }
                  
                  &:focus {
                    border-color: #1890ff;
                    outline: none;
                  }
                }
              }
            }
          }

          .card-footer {
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            padding-top: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            
            .stats {
              display: flex;
              gap: 24px;
              
              .stat-item {
                text-align: center;
                
                .stat-value {
                  font-size: 16px;
                  font-weight: 500;
                  color: rgba(255, 255, 255, 0.9);
                  display: block;
                }
                
                .stat-label {
                  font-size: 12px;
                  color: rgba(255, 255, 255, 0.4);
                  margin-top: 4px;
                }
              }
            }
            
            .actions {
              display: flex;
              gap: 12px;
              
              .action-btn {
                padding: 8px 16px;
                border-radius: 8px;
                font-size: 14px;
                border: none;
                cursor: pointer;
                
                &.sync {
                  background: rgba(255, 255, 255, 0.1);
                  color: #fff;
                  
                  &:hover {
                    background: rgba(255, 255, 255, 0.15);
                  }
                }
                
                &.interact {
                  background: #1890ff;
                  color: #fff;
                  
                  &:hover {
                    background: #40a9ff;
                  }
                }
                
                &.more {
                  background: transparent;
                  border: 1px solid rgba(255, 255, 255, 0.2);
                  color: rgba(255, 255, 255, 0.8);
                  
                  &:hover {
                    background: rgba(255, 255, 255, 0.05);
                  }
                }
              }
            }
          }
        }
      }
    }
    
    .credentials-section {
      .credentials-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 20px;
        
        .platform-card {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 16px;
          padding: 20px;
          display: flex;
          align-items: center;
          gap: 12px;
          
          &.is-connected {
            border: 1px solid rgba(24, 144, 255, 0.3);
          }
          
          .platform-icon {
            font-size: 24px;
          }
          
          .platform-info {
            flex: 1;
            
            .platform-name {
              font-size: 16px;
              font-weight: 500;
              margin-bottom: 4px;
              display: block;
            }
            
            .platform-status {
              font-size: 12px;
              color: rgba(255, 255, 255, 0.4);
            }
          }
          
          .platform-action {
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 14px;
            background: #1890ff;
            border: none;
            color: #fff;
            cursor: pointer;
            
            &:hover {
              background: #40a9ff;
            }
          }
        }
      }
    }
    
    .valuation-section {
      .valuation-cards {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 20px;
        
        .valuation-card {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 16px;
          padding: 20px;
          
          .card-title {
            font-size: 16px;
            font-weight: 500;
            margin-bottom: 12px;
            display: block;
          }
          
          .value-score {
            font-size: 36px;
            font-weight: bold;
            color: #1890ff;
            margin-bottom: 20px;
            display: block;
          }
          
          .value-metrics {
            display: grid;
            gap: 12px;
            
            .metric-item {
              display: flex;
              justify-content: space-between;
              align-items: center;
              
              .metric-label {
                font-size: 14px;
                color: rgba(255, 255, 255, 0.6);
              }
              
              .metric-value {
                font-size: 14px;
                color: rgba(255, 255, 255, 0.8);
              }
            }
          }
          
          &.knowledge {
            background: linear-gradient(135deg, rgba(24, 144, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
          }
          
          &.experience {
            background: linear-gradient(135deg, rgba(250, 84, 28, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
          }
          
          &.potential {
            background: linear-gradient(135deg, rgba(82, 196, 26, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
          }
        }
      }
    }
    
    .market-section {
      .market-filters {
        display: flex;
        gap: 16px;
        margin-bottom: 20px;
        
        .search-input,
        .category-select {
          background: rgba(255, 255, 255, 0.1);
          border: 1px solid rgba(255, 255, 255, 0.2);
          border-radius: 8px;
          padding: 8px 12px;
          color: #fff;
          font-size: 14px;
          
          &:focus {
            border-color: #1890ff;
            outline: none;
          }
        }
        
        .search-input {
          flex: 1;
        }
        
        .category-select {
          width: 200px;
          
          option {
            background: #1f1f1f;
          }
        }
      }
      
      .consciousness-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 20px;
        
        .consciousness-card {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 16px;
          padding: 20px;
          
          .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            
            .consciousness-name {
              font-size: 16px;
              font-weight: 500;
            }
            
            .consciousness-price {
              font-size: 16px;
              color: #1890ff;
            }
          }
          
          .consciousness-desc {
            font-size: 14px;
            color: rgba(255, 255, 255, 0.6);
            margin-bottom: 16px;
            line-height: 1.4;
          }
          
          .consciousness-stats {
            display: flex;
            gap: 16px;
            margin-bottom: 16px;
            
            .stat-item {
              .stat-label {
                font-size: 12px;
                color: rgba(255, 255, 255, 0.4);
                margin-bottom: 4px;
                display: block;
              }
              
              .stat-value {
                font-size: 14px;
                color: rgba(255, 255, 255, 0.8);
              }
            }
          }
          
          .card-actions {
            display: flex;
            gap: 12px;
            
            .action-btn {
              flex: 1;
              padding: 8px;
              border-radius: 8px;
              font-size: 14px;
              border: none;
              cursor: pointer;
              
              &.preview {
                background: rgba(255, 255, 255, 0.1);
                color: #fff;
                
                &:hover {
                  background: rgba(255, 255, 255, 0.15);
                }
              }
              
              &.buy {
                background: #1890ff;
                color: #fff;
                
                &:hover {
                  background: #40a9ff;
                }
              }
              
              &.rent {
                background: #13c2c2;
                color: #fff;
                
                &:hover {
                  background: #36cfc9;
                }
              }
            }
          }
        }
      }
    }
  }
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.8;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}
</style> 