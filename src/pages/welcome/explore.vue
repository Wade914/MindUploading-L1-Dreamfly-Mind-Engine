<template>
  <view class="explore-page">
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
    <scroll-view
      class="content-overlay"
      scroll-y="true"
      :scroll-with-animation="true"
    >
      <!-- 返回按钮 -->
      <view class="back-button" @click="goBack">
        <text class="back-icon">←</text>
        <text class="back-text">返回</text>
      </view>

      <!-- 标题区域 -->
      <view class="title-section">
        <text class="main-title">探索数字生命</text>
        <text class="sub-title">梦蝶心智模型引擎</text>
      </view>
      
      <!-- 引擎界面 -->
      <view class="engine-container">
        <!-- 文件拖放区 -->
        <view 
          class="drop-zone"
          :class="{ 'active': isDragging, 'has-file': selectedFile }"
          @dragenter.prevent="handleDragOver"
          @dragover.prevent="handleDragOver"
          @dragleave.prevent="handleDragLeave"
          @drop.prevent="handleDrop"
          @click="triggerFileInput"
        >
          <view class="drop-content" v-if="!selectedFile">
            <text class="drop-icon">📁</text>
            <text class="drop-title">拖入意识体文件</text>
            <text class="drop-desc">或点击选择文件</text>
            <input 
              type="file" 
              class="file-input" 
              ref="fileInput"
              @change="handleFileSelect"
              accept=".mind,.mind.js"
            />
          </view>
          <view class="file-info" v-else>
            <view class="file-header">
              <text class="file-icon">🧠</text>
              <text class="file-name">{{ selectedFile.name }}</text>
            </view>
            <text class="file-status">意识体文件已就绪</text>
          </view>
        </view>
        

        
        <!-- 状态显示 -->
        <view class="status-section">
          <view class="status-item">
            <text class="status-label">引擎状态</text>
            <text class="status-value" :class="{ 'active': engineStatus === 'ready' }">
              {{ engineStatus === 'ready' ? '就绪' : '待机' }}
            </text>
          </view>
          <view class="status-item">
            <text class="status-label">意识体状态</text>
            <text class="status-value" :class="{ 'active': consciousnessStatus === 'active' }">
              {{ consciousnessStatus === 'active' ? '活跃' : '休眠' }}
            </text>
          </view>
          <view class="status-item loading-item" v-if="isLoading">
            <text class="status-label">加载进度</text>
            <view class="loading-container">
              <view class="loading-bar">
                <view 
                  class="loading-progress"
                  :style="{ width: loadingProgress + '%' }"
                ></view>
              </view>
              <text class="loading-percentage">{{ loadingProgress }}%</text>
            </view>
            <text class="loading-text">{{ loadingText }}</text>
          </view>
        </view>
        
        <!-- 控制按钮 -->
        <view class="control-section">
          <button 
            class="control-btn"
            :class="{ 'disabled': !canStart || isLoading }"
            @click="startEngine"
          >
            <text class="btn-icon">{{ isLoading ? '⚡️' : '🚀' }}</text>
            <text class="btn-text">{{ isLoading ? '引擎启动中...' : '启动引擎' }}</text>
          </button>
        </view>
      </view>
      
      <!-- 意识体广场 -->
      <view class="minds-plaza">
        <view class="plaza-header">
          <text class="plaza-title">意识体广场</text>
          <text class="plaza-subtitle">探索已存在的数字意识体</text>
        </view>
        
        <view class="minds-grid">
          <!-- 史蒂夫·乔布斯 -->
          <view class="mind-card" @click="loadMind('jobs')">
            <image class="mind-avatar" src="/static/minds/jobs.png" mode="aspectFill"></image>
            <view class="mind-info">
              <text class="mind-name">史蒂夫·乔布斯</text>
              <text class="mind-desc">苹果公司联合创始人</text>
              <text class="mind-quote">"Stay hungry, stay foolish."</text>
            </view>
            <button class="mind-btn">加载意识体</button>
          </view>
          
          <!-- 孔子 -->
          <view class="mind-card" @click="loadMind('confucius')">
            <image class="mind-avatar" src="/static/minds/confucious.png" mode="aspectFill"></image>
            <view class="mind-info">
              <text class="mind-name">孔子</text>
              <text class="mind-desc">儒家思想创始人</text>
              <text class="mind-quote">"学而不思则罔，思而不学则殆。"</text>
            </view>
            <button class="mind-btn">加载意识体</button>
          </view>
          
          <!-- 亚里士多德 -->
          <view class="mind-card" @click="loadMind('aristotle')">
            <image class="mind-avatar" src="/static/minds/aristotle.png" mode="aspectFill"></image>
            <view class="mind-info">
              <text class="mind-name">亚里士多德</text>
              <text class="mind-desc">古希腊哲学家</text>
              <text class="mind-quote">"We are what we repeatedly do."</text>
            </view>
            <button class="mind-btn">加载意识体</button>
          </view>
        </view>
      </view>
      
      <!-- 说明文本 -->
      <view class="description-section">
        <text class="description-title">关于梦蝶心智模型引擎</text>
        <text class="description-text">
          梦蝶心智模型引擎是数字生命意识的核心驱动系统。通过加载意识体文件，您可以进入意识体的状态空间，与其进行深度对话和交互。引擎采用先进的量子计算架构，能够完美模拟意识体的思维模式和情感特征。
        </text>
      </view>
    </scroll-view>
  </view>
</template>

<script>
import authManager from '@/utils/auth.js'
import { get } from '@/utils/request.js'

export default {
  data() {
    return {
      isDragging: false,
      engineStatus: 'standby',
      consciousnessStatus: 'dormant',
      canStart: false,
      selectedFile: null,
      isLoading: false,
      loadingProgress: 0,
      loadingText: '',
      mindContent: null,
      targetDir: '/pages/consciousness/interaction'
    }
  },
  async mounted() {
    // 添加全局拖拽事件监听
    const dropZone = document.querySelector('.drop-zone')
    if (dropZone) {
      dropZone.addEventListener('dragenter', this.handleDragOver)
      dropZone.addEventListener('dragover', this.handleDragOver)
      dropZone.addEventListener('dragleave', this.handleDragLeave)
      dropZone.addEventListener('drop', this.handleDrop)
    }

    // 自动加载当前用户的mind文件
    await this.loadUserMindFile()
  },
  beforeDestroy() {
    // 移除全局拖拽事件监听
    const dropZone = document.querySelector('.drop-zone')
    if (dropZone) {
      dropZone.removeEventListener('dragenter', this.handleDragOver)
      dropZone.removeEventListener('dragover', this.handleDragOver)
      dropZone.removeEventListener('dragleave', this.handleDragLeave)
      dropZone.removeEventListener('drop', this.handleDrop)
    }
  },
  methods: {
    handleDragOver(event) {
      event.preventDefault()
      event.stopPropagation()
      this.isDragging = true
      this.debugInfo = '文件悬停中...'
    },
    
    handleDragLeave(event) {
      event.preventDefault()
      event.stopPropagation()
      const rect = event.target.getBoundingClientRect()
      const x = event.clientX
      const y = event.clientY
      
      // 只有当鼠标真正离开拖放区域时才重置状态
      if (
        x <= rect.left ||
        x >= rect.right ||
        y <= rect.top ||
        y >= rect.bottom
      ) {
        this.isDragging = false
        this.debugInfo = '鼠标离开拖放区域'
      }
    },
    
    handleDrop(event) {
      event.preventDefault()
      event.stopPropagation()
      this.isDragging = false
      
      try {
        const dt = event.dataTransfer
        const files = dt.files
        
        this.debugInfo = `检测到文件拖放: ${files.length} 个文件`
        console.log('拖放的文件:', files)
        
        if (files && files.length > 0) {
          const file = files[0]
          this.debugInfo = `正在处理文件: ${file.name} (${file.type})`
          console.log('处理文件:', file)
          this.processFile(file)
        }
      } catch (error) {
        this.debugInfo = `拖放处理错误: ${error.message}`
        console.error('拖放处理错误:', error)
      }
    },
    
    triggerFileInput() {
      const fileInput = this.$refs.fileInput
      if (fileInput) {
        fileInput.click()
      }
    },
    
    handleFileSelect(event) {
      try {
        const file = event.target.files[0]
        if (file) {
          this.debugInfo = `已选择文件: ${file.name} (${file.type})`
          console.log('选择的文件:', file)
          this.processFile(file)
        }
      } catch (error) {
        this.debugInfo = `文件选择错误: ${error.message}`
        console.error('文件选择错误:', error)
      }
    },
    
    async processFile(file) {
      if (!file) {
        this.debugInfo = '未获取到文件'
        return
      }
      
      this.debugInfo = `开始处理文件: ${file.name} (${file.type})`
      console.log('开始处理文件:', file)
      
      if (!file.name.endsWith('.mind') && !file.name.endsWith('.mind.js')) {
        this.debugInfo = '文件类型不正确，请选择.mind或.mind.js文件'
        uni.showToast({
          title: '请选择.mind或.mind.js文件',
          icon: 'none',
          duration: 2000
        })
        return
      }

      try {
        // 读取文件内容
        this.debugInfo = '正在读取文件内容...'
        const content = await this.readFileContent(file)
        this.debugInfo = `文件内容读取成功，长度: ${content.length}`
        console.log('文件内容:', content.substring(0, 100) + '...')
        
        // 解析并验证内容
        const mindData = this.parseMindContent(content)
        this.debugInfo = '文件内容解析成功，正在验证...'
        
        if (!this.validateMindData(mindData)) {
          throw new Error('意识体文件格式无效')
        }
        
        // 保存文件到指定路径
        const targetPath = `/pages/consciousness/interaction/${file.name}`
        try {
          const fs = uni.getFileSystemManager()
          fs.writeFileSync(targetPath, content, 'utf8')
          this.debugInfo = '文件已保存到: ' + targetPath
        } catch (error) {
          console.error('保存文件失败:', error)
          this.debugInfo = '文件保存失败，但将继续加载'
        }
        
        // 更新UI状态
        this.selectedFile = {
          name: file.name.replace(/\.js$/, ''),
          content: content
        }
        this.canStart = true
        this.debugInfo = '文件处理成功，可以启动引擎'
        
        // 保存到全局状态
        if (!getApp().globalData) {
          getApp().globalData = {}
        }
        getApp().globalData.uploadedMind = {
          name: this.selectedFile.name,
          content: content
        }
        
        uni.showToast({
          title: '文件加载成功',
          icon: 'success',
          duration: 2000
        })
        
      } catch (error) {
        this.debugInfo = `处理失败: ${error.message}`
        console.error('文件处理错误:', error)
        uni.showToast({
          title: error.message || '文件处理失败',
          icon: 'none',
          duration: 2000
        })
      }
    },
    
    readFileContent(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = (e) => {
          this.debugInfo = '文件读取完成'
          console.log('文件读取完成')
          resolve(e.target.result)
        }
        reader.onerror = (e) => {
          this.debugInfo = `文件读取失败: ${e.target.error}`
          console.error('文件读取失败:', e.target.error)
          reject(new Error('文件读取失败'))
        }
        reader.readAsText(file)
      })
    },
    
    parseMindContent(content) {
      try {
        // 如果内容是JS模块格式，提取JSON部分
        if (content.includes('export default')) {
          content = content.replace(/export\s+default\s+/, '')
        }
        return JSON.parse(content)
      } catch (error) {
        throw new Error('文件格式解析失败')
      }
    },
    
    validateMindData(data) {
      const required = ['metadata', 'memory', 'status', 'consciousness']
      const missing = required.filter(key => !data[key])
      
      if (missing.length > 0) {
        throw new Error(`缺少必要字段: ${missing.join(', ')}`)
      }
      
      if (!data.metadata.name || !data.metadata.personality_prompt) {
        throw new Error('缺少必要的元数据字段')
      }
      
      return true
    },
    
    startEngine() {
      if (!this.canStart || this.isLoading) return
      
      this.isLoading = true
      this.loadingProgress = 0
      this.loadingText = `${this.selectedFile.name} 加载中...`
      
      const interval = setInterval(() => {
        if (this.loadingProgress < 100) {
          this.loadingProgress += 2
          
          if (this.loadingProgress < 30) {
            this.loadingText = '正在初始化意识核心...'
          } else if (this.loadingProgress < 60) {
            this.loadingText = '正在同步思维模型...'
          } else if (this.loadingProgress < 90) {
            this.loadingText = '正在校准情感参数...'
          } else {
            this.loadingText = '意识同步即将完成...'
          }
        } else {
          clearInterval(interval)
          this.engineStatus = 'ready'
          this.consciousnessStatus = 'active'
          
          setTimeout(() => {
            uni.navigateTo({
              url: `/pages/consciousness/interaction/index?file=${encodeURIComponent(this.selectedFile.name)}`
            })
          }, 500)
        }
      }, 50)
    },
    loadMind(mindId) {
      // 设置选中的意识体
      this.selectedFile = {
        name: mindId + '.mind'
      };
      this.canStart = true;

      // 显示加载提示
      uni.showToast({
        title: '意识体加载成功',
        icon: 'success',
        duration: 2000
      });

      // 自动滚动到顶部的引擎控制区
      uni.pageScrollTo({
        scrollTop: 0,
        duration: 300
      });
    },

    // 返回按钮点击事件
    goBack() {
      // 使用 reLaunch 确保能正确跳转到意识首页
      uni.reLaunch({
        url: '/pages/consciousness/index'
      })
    },

    // 自动加载当前用户的mind文件
    async loadUserMindFile() {
      try {
        const userInfo = authManager.getCurrentUser()
        if (!userInfo) {
          console.log('用户未登录，跳过自动加载mind文件')
          return
        }

        // 使用新的请求工具调用后端API
        const response = await get('/api/minds', {
          page: 1,
          page_size: 10
        })

        if (response && response.data && response.data.code === 200) {
          const mindData = response.data.data

          if (mindData.items && mindData.items.length > 0) {
            // 取第一个mind记录（用户的意识体）
            const userMind = mindData.items[0]
            const filename = userMind.filename

            // 自动设置用户的mind文件
            this.selectedFile = {
              name: filename
            }
            this.canStart = true

            console.log('自动加载用户mind文件成功:', filename, userMind)
          } else {
            console.log('用户还没有创建意识体文件')
          }
        } else {
          console.warn('查询用户mind文件失败:', response?.data)
        }
      } catch (error) {
        console.warn('自动加载用户mind文件失败:', error)
      }
    }
  }
}
</script>

<style lang="scss">
@import '@/styles/variables.scss';

.explore-page {
  position: relative;
  width: 100%;
  height: 100vh;
  
  .background-video {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    z-index: 1;
  }
  
  .content-overlay {
    position: relative;
    z-index: 2;
    height: 100%;
    background: linear-gradient(
      to bottom,
      rgba(0, 0, 0, 0.8),
      rgba(0, 0, 0, 0.6)
    );

    .back-button {
      position: fixed;
      top: 20px;
      left: 20px;
      z-index: 10;
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px 16px;
      background: rgba(0, 0, 0, 0.7);
      border: 1px solid rgba(255, 255, 255, 0.2);
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.3s ease;
      backdrop-filter: blur(10px);

      &:hover {
        background: rgba(0, 0, 0, 0.8);
        border-color: rgba(171, 130, 255, 0.4);
        transform: translateX(-2px);
      }

      .back-icon {
        font-size: 18px;
        color: $text-white;
      }

      .back-text {
        font-size: 14px;
        color: $text-white;
      }
    }

    .title-section {
      text-align: center;
      margin-bottom: 40px;
      
      .main-title {
        font-size: 32px;
        font-weight: 500;
        color: $text-white;
        display: block;
        margin-bottom: 8px;
        text-shadow: 0 0 20px rgba(171, 130, 255, 0.3);
      }
      
      .sub-title {
        font-size: 18px;
        color: $text-gray;
        display: block;
      }
    }
    
    .engine-container {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 30px;
      max-width: 800px;
      margin: 0 auto;
      width: 100%;
      
      .drop-zone {
        width: 100%;
        height: 300px;
        border: 2px dashed rgba(255, 255, 255, 0.2);
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        
        &.active {
          border-color: $primary-purple;
          background: rgba(171, 130, 255, 0.1);
          transform: scale(1.02);
        }
        
        &.has-file {
          border-style: solid;
          border-color: $primary-purple;
          background: rgba(171, 130, 255, 0.1);
        }
        
        .drop-content {
          text-align: center;
          
          .drop-icon {
            font-size: 48px;
            display: block;
            margin-bottom: 16px;
          }
          
          .drop-title {
            font-size: 20px;
            color: $text-white;
            display: block;
            margin-bottom: 8px;
          }
          
          .drop-desc {
            font-size: 14px;
            color: $text-gray;
            display: block;
          }
          
          .file-input {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            opacity: 0;
            cursor: pointer;
            z-index: 1;
          }
        }
        
        .file-info {
          text-align: center;
          
          .file-header {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            margin-bottom: 12px;
            
            .file-icon {
              font-size: 32px;
            }
            
            .file-name {
              font-size: 24px;
              color: $text-white;
              font-weight: 500;
            }
          }
          
          .file-status {
            font-size: 14px;
            color: $primary-purple;
          }
        }
      }
      
      .status-section {
        display: flex;
        gap: 40px;
        width: 100%;
        justify-content: center;
        flex-wrap: wrap;
        
        .status-item {
          text-align: center;
          min-width: 200px;
          
          &.loading-item {
            width: 100%;
            margin-top: 20px;
            
            .loading-container {
              display: flex;
              align-items: center;
              gap: 12px;
              background: rgba(255, 255, 255, 0.05);
              padding: 8px 16px;
              border-radius: 8px;
              backdrop-filter: blur(5px);
              margin-bottom: 8px;
              
              .loading-bar {
                flex: 1;
                height: 4px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 2px;
                overflow: hidden;
                
                .loading-progress {
                  height: 100%;
                  background: $primary-purple;
                  border-radius: 2px;
                  transition: width 0.3s ease;
                  box-shadow: 0 0 10px rgba(171, 130, 255, 0.5);
                }
              }
              
              .loading-percentage {
                font-size: 14px;
                color: $primary-purple;
                min-width: 45px;
                text-align: right;
              }
            }
            
            .loading-text {
              font-size: 14px;
              color: $text-gray;
              display: block;
            }
          }
          
          .status-label {
            font-size: 14px;
            color: $text-gray;
            display: block;
            margin-bottom: 8px;
          }
          
          .status-value {
            font-size: 18px;
            color: $text-gray;
            display: block;
            padding: 8px 16px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            backdrop-filter: blur(5px);
            
            &.active {
              color: $primary-purple;
              background: rgba(171, 130, 255, 0.1);
            }
          }
        }
      }
      
      .control-section {
        .control-btn {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 16px 32px;
          background: $primary-purple;
          border: none;
          border-radius: 12px;
          color: $text-white;
          font-size: 18px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.3s ease;
          backdrop-filter: blur(5px);
          
          &:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(171, 130, 255, 0.3);
          }
          
          &.disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
          }
          
          .btn-icon {
            font-size: 24px;
          }
        }
      }
    }
    
    .minds-plaza {
      margin-top: 60px;
      padding: 0 40px;
      
      .plaza-header {
        text-align: center;
        margin-bottom: 40px;
        
        .plaza-title {
          font-size: 32px;
          font-weight: 500;
          color: $text-white;
          display: block;
          margin-bottom: 8px;
          text-shadow: 0 0 20px rgba(171, 130, 255, 0.3);
        }
        
        .plaza-subtitle {
          font-size: 16px;
          color: $text-gray;
          display: block;
        }
      }
      
      .minds-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 30px;
        margin-bottom: 40px;
        
        .mind-card {
          background: $bg-glass;
          border-radius: 16px;
          padding: 20px;
          backdrop-filter: blur(10px);
          border: 1px solid $border-light;
          transition: all 0.3s ease;
          
          &:hover {
            transform: translateY(-5px);
            box-shadow: $shadow-purple;
            border-color: $border-purple;
          }
          
          .mind-avatar {
            width: 100%;
            height: 200px;
            border-radius: 12px;
            margin-bottom: 20px;
            object-fit: cover;
          }
          
          .mind-info {
            text-align: center;
            margin-bottom: 20px;
            
            .mind-name {
              font-size: 24px;
              color: $text-white;
              display: block;
              margin-bottom: 8px;
              font-weight: 500;
            }
            
            .mind-desc {
              font-size: 14px;
              color: $text-gray;
              display: block;
              margin-bottom: 12px;
            }
            
            .mind-quote {
              font-size: 16px;
              color: $primary-purple;
              display: block;
              font-style: italic;
              line-height: 1.4;
            }
          }
          
          .mind-btn {
            width: 100%;
            padding: 12px;
            background: transparent;
            border: 1px solid $border-purple;
            border-radius: 8px;
            color: $primary-purple;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s ease;
            
            &:hover {
              background: $primary-purple;
              color: $text-white;
            }
          }
        }
      }
    }
    
    .description-section {
      margin-top: 40px;
      text-align: center;
      max-width: 800px;
      margin-left: auto;
      margin-right: auto;
      
      .description-title {
        font-size: 20px;
        color: $text-white;
        display: block;
        margin-bottom: 16px;
      }
      
      .description-text {
        font-size: 14px;
        color: $text-gray;
        line-height: 1.6;
      }
    }
  }
}



.file-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
  z-index: 1;
}
</style> 