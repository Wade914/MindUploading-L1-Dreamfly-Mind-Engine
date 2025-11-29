# 创建新的思想数据上传页面
<template>
  <view class="minddata-container">
    <!-- 背景视频 -->
    <video
      class="background-video"
      src="/static/layer.mp4"
      loop
      muted
      autoplay
      :controls="false"
      object-fit="cover"
    ></video>

    <!-- 内容遮罩 -->
    <view class="content-overlay">
      <!-- 问答内容 -->
      <scroll-view 
        class="qa-content"
        scroll-y="true"
        :scroll-with-animation="true"
        :enhanced="true"
        :show-scrollbar="true"
      >
        <!-- 进度指示器 -->
        <view class="progress-bar">
          <view 
            class="progress-dot" 
            v-for="index in 6" 
            :key="index"
            :class="{ 'active': currentPage >= index, 'done': currentPage > index }"
          ></view>
        </view>

        <!-- 问题页面容器 -->
        <swiper
          class="qa-swiper"
          :current="currentPage - 1"
          :duration="300"
          :disable-touch="true"
        >
          <!-- 人格信息页 -->
          <swiper-item>
            <view class="qa-page" :class="{ 'appear': currentPage === 1 }">
              <text class="page-title">基本信息</text>
              <text class="page-subtitle">建模灵魂关键信息</text>
              
              <!-- 添加基本信息收集 -->
              <view class="input-row">
                <view class="input-group half">
                  <text class="input-label">姓名</text>
                  <input 
                    type="text"
                    class="input-field"
                    v-model="formData.basicInfo.name"
                    placeholder="请输入您的姓名"
                  />
                </view>
                
                <view class="input-group half">
                  <text class="input-label">出生日期</text>
                  <input 
                    type="date"
                    class="input-field"
                    v-model="formData.basicInfo.birth"
                    placeholder="YYYY-MM-DD"
                  />
                </view>
              </view>

              <view class="input-row">
                <view class="input-group half">
                  <text class="input-label">职业</text>
                  <input 
                    type="text"
                    class="input-field"
                    v-model="formData.basicInfo.occupation"
                    placeholder="请输入您的职业"
                  />
                </view>
                
                <view class="input-group half">
                  <text class="input-label">邮箱</text>
                  <input 
                    type="email"
                    class="input-field"
                    v-model="formData.basicInfo.email"
                    placeholder="请输入您的邮箱"
                  />
                </view>
              </view>
              
              <view class="input-group">
                <text class="question">一句话形容你自己</text>
                <textarea 
                  class="input-area"
                  v-model="formData.personality.selfDescription"
                  placeholder="请用一句话描述你自己..."
                ></textarea>
              </view>
              
              <view class="input-group">
                <text class="question">是什么让"你"成为"你"?</text>
                <textarea 
                  class="input-area"
                  v-model="formData.personality.essence"
                  placeholder="分享你的独特之处..."
                ></textarea>
              </view>
            </view>
          </swiper-item>

          <!-- 人生五个瞬间页(1-5) -->
          <swiper-item v-for="(moment, index) in 5" :key="index + 1">
            <view class="qa-page" :class="{ 'appear': currentPage === index + 2 }">
              <text class="page-title">人生瞬间 {{ index + 1 }}/5</text>
              <text class="page-subtitle">{{ getMomentTitle(index).title }}</text>
              
              <view class="input-group">
                <text class="question">{{ getMomentTitle(index).question }}</text>
                <text class="input-label">事件描述</text>
                <textarea 
                  class="input-area"
                  v-model="formData.moments[index].description"
                  placeholder="请描述这个重要时刻..."
                ></textarea>
              </view>
              
              <view class="input-row">
                <view class="input-group half">
                  <text class="input-label">时间</text>
                  <input 
                    type="text"
                    class="input-field"
                    v-model="formData.moments[index].time"
                    placeholder="YYYY-MM-DD"
                  />
                </view>
                
                <view class="input-group half">
                  <text class="input-label">地点</text>
                  <input 
                    type="text"
                    class="input-field"
                    v-model="formData.moments[index].location"
                    placeholder="请输入地点"
                  />
                </view>
              </view>
            </view>
          </swiper-item>
        </swiper>

        <!-- 导航按钮 -->
        <view class="navigation-buttons">
          <button 
            class="nav-button back"
            v-if="currentPage > 1"
            @click="prevPage"
          >
            <text class="button-icon">←</text>
            <text class="button-text">上一步</text>
          </button>
          
          <button 
            class="nav-button next"
            @click="nextPage"
          >
            <text class="button-text">{{ currentPage === 6 ? '完成' : '下一步' }}</text>
            <text class="button-icon">{{ currentPage === 6 ? '✓' : '→' }}</text>
          </button>
        </view>
      </scroll-view>
    </view>

    <!-- AI 助手 -->
    <AIAssistant />
  </view>
</template>

<script>
import AIAssistant from '@/components/AIAssistant.vue'
import { get } from '@/utils/request.js'

export default {
  components: {
    AIAssistant
  },
  data() {
    return {
      currentPage: 1,
      isEditMode: false,  // 是否为编辑模式
      mindId: null,       // 编辑时的意识体ID
      mindFilename: null, // 编辑时的文件名
      formData: {
        basicInfo: {
          name: '',
          birth: '',
          occupation: '',
          email: ''
        },
        personality: {
          selfDescription: '',
          essence: ''
        },
        moments: [
          { description: '', time: '', location: '' },
          { description: '', time: '', location: '' },
          { description: '', time: '', location: '' },
          { description: '', time: '', location: '' },
          { description: '', time: '', location: '' }
        ]
      }
    }
  },

  onLoad(options) {
    // 检查是否为编辑模式
    if (options.mode === 'edit' && options.mind_id) {
      this.isEditMode = true
      this.mindId = options.mind_id
      this.mindFilename = options.filename ? decodeURIComponent(options.filename) : null
      this.loadMindData()
    }
  },

  methods: {
    async loadMindData() {
      // 加载现有意识体数据
      if (!this.mindFilename) {
        uni.showToast({
          title: '无法加载意识体数据',
          icon: 'none'
        })
        return
      }

      uni.showLoading({ title: '加载中...' })

      try {
        const response = await get(`/api/mind/${encodeURIComponent(this.mindFilename)}`)

        if (response && response.data && response.data.code === 200) {
          const mindContent = response.data.data

          // 解析 mind 文件内容
          const jsonStr = mindContent.replace('export default ', '').trim()
          const mindData = JSON.parse(jsonStr)

          // 填充表单数据
          const metadata = mindData.metadata || {}
          const memory = mindData.memory || {}

          this.formData.basicInfo.name = metadata.name || ''
          this.formData.basicInfo.birth = metadata.birth || ''
          this.formData.basicInfo.occupation = metadata.occupation || ''
          this.formData.basicInfo.email = metadata.email || ''

          // 解析 personality_prompt
          const personalityPrompt = metadata.personality_prompt || ''
          // 提取自我描述（去除前缀）
          const selfDescMatch = personalityPrompt.match(/你现在是.*?的数字意识体。(.*)/)
          this.formData.personality.selfDescription = selfDescMatch ? selfDescMatch[1] : personalityPrompt

          this.formData.personality.essence = memory.self_cognition || ''

          // 解析记忆片段
          const fragments = memory.memory_fragments || []
          for (let i = 0; i < Math.min(fragments.length, 5); i++) {
            const fragment = fragments[i]
            if (fragment) {
              this.formData.moments[i].time = fragment.time || ''
              // 尝试从 content 中提取 location 和 description
              const content = fragment.content || ''
              const locationMatch = content.match(/在(.+?)，(.*)/)
              if (locationMatch) {
                this.formData.moments[i].location = locationMatch[1]
                this.formData.moments[i].description = locationMatch[2]
              } else {
                this.formData.moments[i].description = content
              }
            }
          }

          // 保存原始的 voice_prompt 和 image_data（编辑时需要保留）
          if (!getApp().globalData) {
            getApp().globalData = {}
          }
          if (!getApp().globalData.uploadData) {
            getApp().globalData.uploadData = {}
          }

          // 标记为编辑模式，保存原始数据
          getApp().globalData.uploadData.isEditMode = true
          getApp().globalData.uploadData.mindId = this.mindId
          getApp().globalData.uploadData.originalVoicePrompt = metadata.voice_prompt || null
          getApp().globalData.uploadData.originalVoiceReferenceText = metadata.voice_reference_text || null
          getApp().globalData.uploadData.originalImageData = metadata.image_data || null

          // 保存 physical_info（身高体重）
          const physicalInfo = metadata.physical_info || {}
          getApp().globalData.uploadData.originalHeight = physicalInfo.height || ''
          getApp().globalData.uploadData.originalWeight = physicalInfo.weight || ''

          uni.hideLoading()
          uni.showToast({
            title: '数据加载成功',
            icon: 'success'
          })
        } else {
          throw new Error('获取意识体数据失败')
        }
      } catch (error) {
        uni.hideLoading()
        console.error('加载意识体数据失败:', error)
        uni.showToast({
          title: '加载失败: ' + error.message,
          icon: 'none'
        })
      }
    },

    getMomentTitle(index) {
      const titles = [
        {
          title: '人生的决定性时刻',
          question: '在您的人生旅途中，有没有那些特别的时刻，它们如同璀璨的星辰，照亮了您的道路，改变了您的方向？我想聆听那些决定性的瞬间，那些在您心中留下深刻印记的转折点。请与我分享那些宝贵的记忆：它们发生在何时何地，又是怎样的经历，让您的人生因此而不同？'
        },
        {
          title: '温暖的童年回忆',
          question: '您能否回忆一下，在您的童年时期，有没有一个特别的场景或事件，让您至今仍然感到温馨和怀念？它发生在您多大的时候，又对您后来的成长产生了怎样的影响？'
        },
        {
          title: '少年时期的启发',
          question: '在您的少年时期，有没有一次经历，让您对世界有了新的认识或发现了自己的兴趣和热情？那是一个怎样的发现，它又是如何塑造了您的兴趣和价值观的？'
        },
        {
          title: '青年时代的梦想',
          question: '当您步入青年时期，有没有一个梦想或目标，让您为之奋斗并感到无比激动？这个梦想是什么，您是如何一步步接近它的，又遇到了哪些挑战？'
        },
        {
          title: '成年后的责任与成就',
          question: '成年后，您是否承担了某些重要的责任，或者实现了一些令您自豪的成就？这些责任和成就是什么，它们对您的个人生活和职业生涯有什么样的影响？'
        },
        {
          title: '人生智慧的传承',
          question: '随着年龄的增长，您是否开始对自己的人生进行反思，或者有了一些想要传承给下一代的智慧和经验？您最希望分享给年轻人的是什么，您认为这些经验对他们有何重要意义？'
        }
      ]
      return titles[index]
    },

    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--
      }
    },

    nextPage() {
      if (this.currentPage < 6) {
        this.currentPage++
      } else {
        this.submitForm()
      }
    },

    submitForm() {
      // 验证必填字段
      if (!this.formData.basicInfo.name || !this.formData.basicInfo.birth) {
        uni.showToast({
          title: '请填写姓名和出生日期',
          icon: 'none'
        })
        return
      }



      // 确保globalData存在
      if (!getApp().globalData) {
        getApp().globalData = {}
      }

      // 保留编辑模式的原始数据
      const existingData = getApp().globalData.uploadData || {}

      // 保存到全局状态
      const uploadData = {
        ...existingData,  // 保留原有数据（如编辑模式下的 voice/image）
        name: this.formData.basicInfo.name,
        birth: this.formData.basicInfo.birth,
        occupation: this.formData.basicInfo.occupation,
        email: this.formData.basicInfo.email,
        personality: this.formData.personality.selfDescription + '\n' + this.formData.personality.essence,
        self_cognition: this.formData.personality.selfDescription,
        memories: this.formData.moments.map(moment => ({
          time: moment.time,
          content: `在${moment.location || '某处'}，${moment.description}`
        })).filter(m => m.time && m.content),
        // 编辑模式相关
        isEditMode: this.isEditMode,
        mindId: this.mindId
      }

      getApp().globalData.uploadData = uploadData

      uni.showToast({
        title: '提交成功',
        icon: 'success'
      })

      // 跳转到音色上传页面
      setTimeout(() => {
        uni.navigateTo({
          url: '/pages/upload/voicedata'
        })
      }, 1500)
    }
  }
}
</script>

<style lang="scss">
// 继承之前的配色方案
$primary-purple: rgba(171, 130, 255, 0.85);
$primary-purple-glow: rgba(171, 130, 255, 0.2);
$text-white: rgba(255, 255, 255, 0.95);
$text-gray: rgba(255, 255, 255, 0.75);
$bg-dark: #121212;
$bg-gray: rgba(255, 255, 255, 0.08);

.minddata-container {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background: $bg-dark;

  .background-video {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    z-index: 1;
    opacity: 0.6;
  }

  .content-overlay {
    position: relative;
    z-index: 2;
    height: 100vh;
    background: linear-gradient(to bottom, rgba(0,0,0,0.8), rgba(0,0,0,0.4));

    .qa-content {
      height: 100%;
      padding: 40px 20px;

      .progress-bar {
        position: sticky;
        top: 0;
        z-index: 10;
        background: rgba(0,0,0,0.5);
        padding: 20px 0;
        backdrop-filter: blur(10px);
        display: flex;
        justify-content: center;
        gap: 16px;
        margin-bottom: 40px;

        .progress-dot {
          width: 12px;
          height: 12px;
          border-radius: 50%;
          background: $bg-gray;
          transition: all 0.3s ease;

          &.active {
            background: $primary-purple;
            box-shadow: 0 0 10px $primary-purple-glow;
          }

          &.done {
            background: $text-white;
          }
        }
      }

      .qa-swiper {
        height: calc(100vh - 200px);
        
        .qa-page {
          padding: 20px;
          opacity: 0;
          transform: translateY(20px);
          transition: all 0.8s ease;
          height: 100%;
          overflow-y: auto;

          &.appear {
            opacity: 1;
            transform: translateY(0);
          }

          .page-title {
            font-size: 36px;
            font-weight: bold;
            color: $text-white;
            margin-bottom: 8px;
            display: block;
            text-shadow: 0 0 15px rgba(171, 130, 255, 0.4);
          }

          .page-subtitle {
            font-size: 24px;
            color: $primary-purple;
            margin-bottom: 30px;
            display: block;
            font-weight: 500;
          }

          .input-group {
            margin-bottom: 30px;

            .question {
              font-size: 16px;
              color: $text-white;
              margin-bottom: 20px;
              display: block;
              line-height: 1.8;
              letter-spacing: 0.5px;
              padding: 20px;
              background: rgba(171, 130, 255, 0.1);
              border-radius: 12px;
              border-left: 4px solid $primary-purple;
            }

            .input-label {
              font-size: 14px;
              color: $text-gray;
              margin-bottom: 8px;
              display: block;
            }

            .input-area {
              width: 100%;
              min-height: 120px;
              padding: 16px;
              background: $bg-gray;
              border: 1px solid rgba(171, 130, 255, 0.3);
              border-radius: 8px;
              color: $text-white;
              font-size: 16px;
              line-height: 1.6;
              resize: none;
              backdrop-filter: blur(5px);
              transition: all 0.3s ease;

              &:focus {
                border-color: $primary-purple;
                box-shadow: 0 0 20px rgba(171, 130, 255, 0.2);
                outline: none;
              }
            }

            .input-field {
              width: 100%;
              height: 48px;
              padding: 0 16px;
              background: $bg-gray;
              border: 1px solid rgba(171, 130, 255, 0.3);
              border-radius: 8px;
              color: $text-white;
              font-size: 16px;
              backdrop-filter: blur(5px);
              transition: all 0.3s ease;

              &:focus {
                border-color: $primary-purple;
                box-shadow: 0 0 20px rgba(171, 130, 255, 0.2);
                outline: none;
              }
            }
          }

          .input-row {
            display: flex;
            gap: 20px;
            margin-top: 20px;

            .input-group.half {
              flex: 1;
            }
          }
        }
      }

      .navigation-buttons {
        display: flex;
        justify-content: space-between;
        padding: 20px 40px;
        
        .nav-button {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          padding: 12px 24px;
          background: $bg-gray;
          border: 1px solid $primary-purple;
          border-radius: 24px;
          cursor: pointer;
          transition: all 0.3s ease;
          backdrop-filter: blur(5px);

          &:hover {
            background: rgba(171, 130, 255, 0.15);
            box-shadow: 0 5px 25px rgba(171, 130, 255, 0.25);
            transform: translateY(-2px);
          }

          .button-text {
            font-size: 16px;
            color: $text-white;
            margin: 0 8px;
          }

          .button-icon {
            font-size: 18px;
            color: $primary-purple;
          }

          &.next {
            background: $primary-purple;
            
            .button-text,
            .button-icon {
              color: $text-white;
            }

            &:hover {
              background: rgba(171, 130, 255, 0.95);
            }
          }
        }
      }
    }
  }
}
</style> 