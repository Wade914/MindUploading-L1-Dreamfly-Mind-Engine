<template>
  <view class="imagedata-container">
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
      <scroll-view
        class="scroll-container"
        scroll-y="true"
        :scroll-with-animation="true"
      >
        <view class="image-content">
          <!-- 标题区域 -->
          <view class="header">
            <text class="page-title">形象上传</text>
            <text class="page-subtitle">为意识体塑造您的形象</text>
          </view>

          <!-- 照片指引 -->
          <view class="guide-section">
            <view class="guide-item">
              <text class="guide-title">照片要求</text>
              <text class="guide-content">• 照片应为高分辨率（至少1080p）</text>
              <text class="guide-content">• 正面展示面部，表情自然</text>
              <text class="guide-content">• 保证光线良好，背景简洁、无杂物</text>
            </view>
          </view>

          <!-- 照片预览区 -->
          <view class="preview-section">
            <view class="preview-container" @click="openCamera">
              <image 
                v-if="imageUrl" 
                :src="imageUrl" 
                class="preview-image"
                mode="aspectFit"
              />
              <view v-else class="preview-placeholder">
                <text class="placeholder-icon">+</text>
                <text class="placeholder-text">点击拍摄或上传照片</text>
              </view>
            </view>

            <!-- 控制按钮 -->
            <view class="control-buttons">
              <button 
                class="control-btn camera"
                @click="openCamera"
              >
                <text class="btn-icon">📷</text>
                <text class="btn-text">拍摄照片</text>
              </button>

              <button 
                class="control-btn upload"
                @click="openFileSelector"
              >
                <text class="btn-icon">↑</text>
                <text class="btn-text">上传照片</text>
              </button>
            </view>
          </view>

          <!-- 身体数据输入区 -->
          <view class="data-input-section">
            <view class="input-group">
              <text class="input-label">身高 (cm)</text>
              <input
                type="text"
                inputmode="decimal"
                class="input-field"
                v-model="height"
                placeholder="请输入身高"
                @input="handleHeightInput"
              />
            </view>

            <view class="input-group">
              <text class="input-label">体重 (kg)</text>
              <input
                type="text"
                inputmode="decimal"
                class="input-field"
                v-model="weight"
                placeholder="请输入体重"
                @input="handleWeightInput"
              />
            </view>
          </view>

          <!-- 上传按钮 -->
          <button
            class="submit-btn"
            :disabled="!isFormValid"
            @click="uploadData"
          >
            <text class="btn-text">确认上传</text>
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

export default {
  components: {
    AIAssistant
  },
  data() {
    return {
      imageUrl: null,
      imageFile: null,
      height: '',
      weight: '',
      cameraContext: null
    }
  },

  computed: {
    isFormValid() {
      return this.imageUrl && this.height && this.weight
    }
  },

  methods: {
    handleHeightInput(e) {
      const value = String(e.detail?.value || e.target?.value || '')
      // 只允许数字和小数点
      const numericValue = value.replace(/[^\d.]/g, '')
      // 确保只有一个小数点
      const parts = numericValue.split('.')
      if (parts.length > 2) {
        this.height = parts[0] + '.' + parts.slice(1).join('')
      } else {
        this.height = numericValue
      }
    },

    handleWeightInput(e) {
      const value = String(e.detail?.value || e.target?.value || '')
      // 只允许数字和小数点
      const numericValue = value.replace(/[^\d.]/g, '')
      // 确保只有一个小数点
      const parts = numericValue.split('.')
      if (parts.length > 2) {
        this.weight = parts[0] + '.' + parts.slice(1).join('')
      } else {
        this.weight = numericValue
      }
    },

    async openCamera() {
      try {
        // 请求摄像头权限
        const stream = await navigator.mediaDevices.getUserMedia({ video: true })
        
        // 创建视频元素
        const video = document.createElement('video')
        video.srcObject = stream
        video.autoplay = true
        
        // 等待视频加载
        await new Promise((resolve) => {
          video.onloadedmetadata = resolve
        })
        
        // 创建画布
        const canvas = document.createElement('canvas')
        canvas.width = video.videoWidth
        canvas.height = video.videoHeight
        
        // 绘制视频帧
        const ctx = canvas.getContext('2d')
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
        
        // 转换为图片
        const imageData = canvas.toDataURL('image/jpeg')
        
        // 停止视频流
        stream.getTracks().forEach(track => track.stop())
        
        // 处理图片
        this.handleImageSelect(imageData)

        uni.showToast({
          title: '拍照成功',
          icon: 'success',
          duration: 1500,
          mask: false
        })
        // 兜底：强制在 1.6s 后关闭，避免偶发卡住
        setTimeout(() => {
          try { uni.hideToast() } catch (e) {}
        }, 1600)
      } catch (err) {
        uni.showToast({
          title: '无法访问摄像头',
          icon: 'none'
        })
        console.error('摄像头错误:', err)
      }
    },

    openFileSelector() {
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: ['album'],
        success: (res) => {
          this.handleImageSelect(res.tempFilePaths[0])
        },
        fail: (err) => {
          uni.showToast({
            title: '无法选择图片',
            icon: 'none'
          })
          console.error('选择图片错误:', err)
        }
      })
    },

    handleImageSelect(tempFilePath) {
      this.imageUrl = tempFilePath
      this.imageFile = tempFilePath
    },

    async uploadData() {
      console.log('uploadData 被调用')
      console.log('表单验证状态:', this.isFormValid)
      console.log('当前数据:', {
        imageUrl: this.imageUrl,
        height: this.height,
        weight: this.weight
      })

      if (!this.isFormValid) {
        uni.showToast({
          title: '请完成所有必填项',
          icon: 'none',
          duration: 2000
        })
        return
      }

      uni.showLoading({
        title: '上传中...'
      })

      try {
        // 确保globalData存在
        if (!getApp().globalData) {
          getApp().globalData = {}
        }
        if (!getApp().globalData.uploadData) {
          getApp().globalData.uploadData = {}
        }

        // 保存图片和身体数据到全局状态
        getApp().globalData.uploadData.imageUrl = this.imageUrl
        getApp().globalData.uploadData.imageFile = this.imageFile
        getApp().globalData.uploadData.height = this.height
        getApp().globalData.uploadData.weight = this.weight

        console.log('保存的数据:', {
          imageUrl: this.imageUrl,
          height: this.height,
          weight: this.weight
        })

        uni.hideLoading()
        uni.showToast({
          title: '上传成功',
          icon: 'success',
          duration: 1500
        })

        // 跳转到生成页面
        setTimeout(() => {
          uni.navigateTo({
            url: '/pages/upload/complete'
          })
        }, 1500)
      } catch (err) {
        uni.hideLoading()
        uni.showToast({
          title: '上传失败',
          icon: 'none',
          duration: 2000
        })
        console.error('上传错误:', err)
      }
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

.imagedata-container {
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
    pointer-events: auto;

    .scroll-container {
      height: 100%;
      padding: 40px;
      pointer-events: auto;
    }

    .image-content {
      max-width: 800px;
      margin: 0 auto;
      padding-bottom: 40px;
      min-height: 100%;
      display: flex;
      flex-direction: column;
      gap: 40px;
      pointer-events: auto;

      .header {
        text-align: center;
        padding-bottom: 20px;

        .page-title {
          font-size: 36px;
          font-weight: bold;
          color: $text-white;
          margin-bottom: 8px;
          display: block;
          text-shadow: 0 0 15px rgba(171, 130, 255, 0.4);
        }

        .page-subtitle {
          font-size: 18px;
          color: $primary-purple;
          display: block;
        }
      }

      .guide-section {
        padding: 30px;
        background: rgba(171, 130, 255, 0.05);
        border-radius: 16px;
        backdrop-filter: blur(10px);
        position: relative;
        z-index: 1;

        .guide-item {
          .guide-title {
            font-size: 18px;
            color: $primary-purple;
            margin-bottom: 12px;
            display: block;
            font-weight: 500;
          }

          .guide-content {
            font-size: 16px;
            color: $text-white;
            line-height: 1.6;
            display: block;
          }
        }
      }

      .preview-section {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 20px;
        position: relative;
        z-index: 1;

        .preview-container {
          width: 100%;
          max-width: 400px;
          height: 400px;
          background: rgba(255, 255, 255, 0.05);
          border: 2px dashed $primary-purple;
          border-radius: 16px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          overflow: hidden;
          transition: all 0.3s ease;
          position: relative;
          z-index: 2;

          &:hover {
            border-color: $text-white;
            background: rgba(255, 255, 255, 0.1);
          }

          .preview-image {
            width: 100%;
            height: 100%;
            object-fit: cover;
          }

          .preview-placeholder {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 12px;

            .placeholder-icon {
              font-size: 48px;
              color: $primary-purple;
            }

            .placeholder-text {
              font-size: 16px;
              color: $text-gray;
            }
          }
        }

        .control-buttons {
          display: flex;
          gap: 20px;

          .control-btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 12px 24px;
            background: $bg-gray;
            border: 1px solid $primary-purple;
            border-radius: 24px;
            cursor: pointer;
            transition: all 0.3s ease;
            gap: 8px;

            &:hover {
              background: rgba(171, 130, 255, 0.15);
              box-shadow: 0 5px 25px rgba(171, 130, 255, 0.25);
              transform: translateY(-2px);
            }

            .btn-icon {
              font-size: 18px;
              color: $primary-purple;
            }

            .btn-text {
              font-size: 16px;
              color: $text-white;
            }

            &.upload {
              background: $primary-purple;

              .btn-icon,
              .btn-text {
                color: $text-white;
              }
            }
          }
        }
      }

      .data-input-section {
        display: flex;
        flex-direction: column;
        gap: 20px;
        padding: 30px;
        background: rgba(171, 130, 255, 0.15);
        border-radius: 16px;
        position: relative;
        z-index: 10;
        pointer-events: auto !important;

        .input-group {
          display: flex;
          flex-direction: column;
          gap: 8px;
          pointer-events: auto !important;

          .input-label {
            font-size: 16px;
            color: $primary-purple;
            font-weight: 500;
            user-select: none;
          }

          .input-field {
            width: 100%;
            height: 48px;
            padding: 0 16px;
            background: rgba(255, 255, 255, 0.05);
            border: 2px solid rgba(171, 130, 255, 0.3);
            border-radius: 8px;
            color: $text-white;
            font-size: 16px;
            line-height: 44px;
            text-align: left;
            transition: all 0.3s ease;

            &:focus {
              background: rgba(255, 255, 255, 0.1);
              border-color: $primary-purple;
              outline: none;
              box-shadow: 0 0 20px rgba(171, 130, 255, 0.3);
            }

            &::placeholder {
              color: rgba(255, 255, 255, 0.3);
              line-height: 44px;
            }
          }

          // 针对 uni-app 编译后的 uni-input 元素
          uni-input {
            display: block;
            width: 100%;
            height: 48px;

            // uni-app 生成的包裹层
            .uni-input-wrapper {
              position: relative;
              display: flex;
              align-items: center;
              height: 100%;
            }

            // uni-app 生成的 placeholder 层
            .uni-input-placeholder {
              pointer-events: none;
              position: absolute;
              left: 16px;
              top: 0;
              height: 100%;
              display: flex;
              align-items: center;
              color: rgba(255, 255, 255, 0.3);
              font-size: 16px;
            }

            // 内部真实的 input 元素
            input,
            .uni-input-input {
              width: 100%;
              height: 100%;
              background: transparent;
              border: none;
              outline: none;
              color: $text-white;
              font-size: 16px;
              line-height: 44px;
              text-align: left;
              padding: 0;
            }
          }
        }
      }

      .submit-btn {
        padding: 16px 32px;
        background: $primary-purple;
        border: none;
        border-radius: 24px;
        cursor: pointer;
        transition: all 0.3s ease;
        margin-top: 20px;
        position: relative;
        z-index: 50;
        pointer-events: auto !important;
        touch-action: manipulation;
        -webkit-tap-highlight-color: transparent;

        &:hover:not(:disabled) {
          box-shadow: 0 5px 25px rgba(171, 130, 255, 0.4);
          transform: translateY(-2px);
        }

        &:active:not(:disabled) {
          transform: translateY(0);
        }

        &:disabled,
        &[disabled] {
          opacity: 0.4 !important;
          cursor: not-allowed !important;
          transform: none !important;
          background: rgba(171, 130, 255, 0.3) !important;
          pointer-events: none !important;
          box-shadow: none !important;
        }

        // uni-app H5 平台的 disabled 属性支持
        &[aria-disabled="true"] {
          opacity: 0.4 !important;
          cursor: not-allowed !important;
          transform: none !important;
          background: rgba(171, 130, 255, 0.3) !important;
          pointer-events: none !important;
          box-shadow: none !important;
        }

        .btn-text {
          font-size: 18px;
          color: $text-white;
          font-weight: 500;
          pointer-events: none;
          user-select: none;
        }
      }
    }
  }
}
</style> 