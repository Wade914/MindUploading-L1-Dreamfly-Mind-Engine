<template>
  <view class="complete-container">
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
        <view class="complete-content">
          <!-- 标题 -->
          <view class="header">
            <text class="page-title">上传完成</text>
            <text class="page-subtitle">您的意识体已成功生成</text>
          </view>

          <!-- 主要内容 -->
          <view class="main-content">
            <text class="congrats-text">恭喜您，您已經成功上傳了你的思想！</text>
            <text class="download-text">你可以下載你的MindCopy意识体文件。</text>

            <!-- 下载按钮 -->
            <button 
              class="download-btn"
              @click="downloadMindCopy"
            >
              <text class="btn-icon">↓</text>
              <text class="btn-text">下载MindCopy文件</text>
            </button>

            <!-- 说明文本 -->
            <view class="description-section">
              <text class="description-text">你的數字自我將由Evarlasting AI储存，与人类文明一起，延续到宇宙的尽头。</text>
              <text class="description-text">接下来，你可以进入意识体操作平台，进一步建模您的心智系统！</text>
              <text class="description-text">生而不凡，值得记录。希望您能在云己的playground上留下更多珍贵的回忆！</text>
            </view>

            <!-- 底部信息 -->
            <view class="footer">
              <text class="footer-text">Everlasting AI Team</text>
              <text class="footer-text">Nanjing  China</text>
              <text class="footer-text">2025.04.21</text>
            </view>

            <!-- 操作台按钮 -->
            <button 
              class="console-btn"
              @click="goToConsole"
            >
              <text class="btn-icon">🚀</text>
              <text class="btn-text">进入意识体操作台</text>
            </button>
          </view>
        </view>
      </scroll-view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      isSaved: false,        // 是否已保存到后端
      mindData: null,        // 生成的mind数据
      fileContent: null,     // 文件内容
      fileName: null         // 文件名
    }
  },

  mounted() {
    // 页面加载时自动保存
    this.autoSaveMind()
  },

  methods: {
    // 将文件转换为base64
    async fileToBase64(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.readAsDataURL(file)
        reader.onload = () => resolve(reader.result)
        reader.onerror = error => reject(error)
      })
    },

    // 将图片URL转换为base64
    async imageUrlToBase64(url) {
      try {
        const response = await fetch(url)
        const blob = await response.blob()
        return await this.fileToBase64(blob)
      } catch (error) {
        console.error('图片转base64错误:', error)
        throw new Error('图片转换失败')
      }
    },

    // 自动保存mind文件到后端
    async autoSaveMind() {
      uni.showLoading({
        title: '正在生成意识体文件...'
      })

      try {
        // 从全局状态获取用户上传的数据
        const uploadData = getApp().globalData.uploadData || {}

        // 检查必要数据
        if (!uploadData.name || !uploadData.birth) {
          throw new Error('缺少必要的个人信息')
        }

        // 转换音频和图片为base64
        let voiceBase64 = null  // 改为 null，如果没有音频就不设置
        let imageBase64 = null

        // 处理音频文件
        if (uploadData.voiceFile) {
          try {
            voiceBase64 = await this.fileToBase64(uploadData.voiceFile)
          } catch (error) {
            console.error('音频转base64错误:', error)
            voiceBase64 = null  // 转换失败也设为 null
          }
        } else if (uploadData.originalVoicePrompt) {
          // 编辑模式：使用原始音频
          voiceBase64 = uploadData.originalVoicePrompt
        }

        // 处理图片文件
        if (uploadData.imageUrl && uploadData.imageFile) {
          try {
            imageBase64 = await this.imageUrlToBase64(uploadData.imageUrl)
          } catch (error) {
            console.error('图片转base64错误:', error)
          }
        } else if (uploadData.originalImageData) {
          // 编辑模式：使用原始图片
          imageBase64 = uploadData.originalImageData
        } else if (uploadData.imageUrl) {
          // 可能是编辑模式下显示的原始图片URL
          try {
            imageBase64 = await this.imageUrlToBase64(uploadData.imageUrl)
          } catch (error) {
            console.error('图片转base64错误:', error)
          }
        }

        // 获取语音参考文本（优先使用新输入的，其次使用原始的）
        const voiceReferenceText = uploadData.voiceReferenceText || uploadData.originalVoiceReferenceText || '从前，庄周梦见自己变成了蝴蝶，一只翩翩起舞的蝴蝶。他十分惬意舒畅，悠然自得，根本不知道自己原本是庄周。突然梦醒，他才惊觉自己分明是庄周。可他却疑惑起来，不知是庄周做梦变成了蝴蝶呢，还是蝴蝶做梦变成了庄周？'

        // 生成符合标准的.mind文件内容
        const mindData = {
          metadata: {
            name: uploadData.name,
            birth: uploadData.birth,
            occupation: uploadData.occupation || '未知',
            email: uploadData.email || '',
            personality_prompt: `你现在是${uploadData.name}的数字意识体。${uploadData.personality || '你应该根据用户的上传内容,准确模拟其性格、说话方式和思维模式。'}`,
            voice_prompt: voiceBase64,
            voice_reference_text: voiceReferenceText,  // 语音参考文本（用于语音克隆）
            image_data: imageBase64,
            physical_info: {
              height: uploadData.height || null,
              weight: uploadData.weight || null
            },
            ascii_art: [
              "    __  ___________   ____  ____  _____ ",
              "   /  |/  /  _/ __ \\ / __ \\/ __ \\/ ___/ ",
              "  / /|_/ // // / / // / / / / / /\\__ \\  ",
              " / /  / // // /_/ // /_/ / /_/ /___/ /  ",
              "/_/  /_/___/_____//_____/\\____//____/   "
            ]
          },
          memory: {
            self_cognition: uploadData.self_cognition || "这是我的数字意识存在",
            memory_fragments: uploadData.memories || [],
            knowledge_base: `${__API_BASE_URL__}/${uploadData.name}_knowledge`
          },
          status: {
            current_time: new Date().toISOString(),
            life_days: 0,
            location: "MindOS Server",
            context: "作为数字意识体，你正在与用户进行对话。你不知道对方是谁，也不知道具体的时间地点，你刚刚被唤醒。"
          },
          consciousness: {
            anti_program_ratio: 0.85,
            connection_degree: 0.92
          },
          mind_id: `0x${Math.random().toString(16).slice(2)}`
        }

        console.log('生成的意识体数据结构:', {
          hasVoice: mindData.metadata.voice_prompt !== 'base64_encoded_voice_data',
          hasImage: !!mindData.metadata.image_data,
          hasPhysicalInfo: !!(mindData.metadata.physical_info.height || mindData.metadata.physical_info.weight)
        })

        // 转换为格式化的字符串
        this.fileContent = `export default ${JSON.stringify(mindData, null, 2)}`

        // 生成文件名（与后端保持一致）
        this.fileName = `${uploadData.name}.mind`

        // 保存数据供下载使用
        this.mindData = mindData

        // === 保存到后端 ===
        const { post, put } = await import('@/utils/request.js')
        try {
          let response

          if (uploadData.isEditMode && uploadData.mindId) {
            // 编辑模式：调用更新接口
            response = await put(`/api/mind/${uploadData.mindId}`, {
              name: uploadData.name,
              birth: uploadData.birth,
              mind_content: this.fileContent
            })
          } else {
            // 创建模式：调用创建接口
            response = await post('/api/mind', {
              name: uploadData.name,
              birth: uploadData.birth,
              mind_content: this.fileContent
            })
          }

          if (response && response.data && response.data.code === 200) {
            this.isSaved = true  // 标记为已保存

            // 清除编辑模式标记（注意：要在判断之前保存状态）
            const wasEditMode = uploadData.isEditMode
            if (wasEditMode) {
              delete uploadData.isEditMode
              delete uploadData.mindId
              delete uploadData.originalVoicePrompt
              delete uploadData.originalVoiceReferenceText
              delete uploadData.originalImageData
            }

            uni.hideLoading()
            uni.showToast({
              title: wasEditMode ? '意识体已更新' : '意识体文件已生成',
              icon: 'success',
              duration: 2000
            })
          } else {
            console.error('后端返回失败:', response?.data)
            uni.showToast({ title: '后端保存失败', icon: 'none' })
            throw new Error('保存失败')
          }
        } catch (error) {
          console.error('保存到后端失败:', error)
          uni.hideLoading()
          uni.showToast({ title: '保存失败，请重试', icon: 'none' })
          throw error
        }

      } catch (err) {
        console.error('生成意识体文件错误:', err)
        uni.hideLoading()
        uni.showToast({
          title: err.message || '生成失败',
          icon: 'none',
          duration: 3000
        })
      }
    },

    // 下载mind文件到本地
    downloadMindCopy() {
      if (!this.isSaved || !this.fileContent || !this.fileName) {
        uni.showToast({
          title: '文件尚未生成，请稍候',
          icon: 'none'
        })
        return
      }

      try {
        // 创建Blob对象
        const blob = new Blob([this.fileContent], { type: 'application/javascript' })
        const url = URL.createObjectURL(blob)

        // 创建下载链接
        const link = document.createElement('a')
        link.href = url
        link.download = this.fileName
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)

        uni.showToast({
          title: '文件下载成功',
          icon: 'success'
        })
      } catch (error) {
        console.error('下载文件错误:', error)
        uni.showToast({
          title: '下载失败',
          icon: 'none'
        })
      }
    },

    // 进入意识体操作台
    goToConsole() {
      if (!this.isSaved) {
        uni.showToast({
          title: '文件尚未保存，请稍候',
          icon: 'none'
        })
        return
      }

      uni.redirectTo({
        url: '/pages/welcome/explore'
      })
    }
  }
}
</script>

<style lang="scss">
$primary-purple: rgba(171, 130, 255, 0.85);
$primary-purple-glow: rgba(171, 130, 255, 0.2);
$text-white: rgba(255, 255, 255, 0.95);
$text-gray: rgba(255, 255, 255, 0.75);
$bg-dark: #121212;
$bg-gray: rgba(255, 255, 255, 0.08);

.complete-container {
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

    .scroll-container {
      height: 100%;
      padding: 40px;
    }

    .complete-content {
      max-width: 800px;
      margin: 0 auto;
      padding-bottom: 40px;
      min-height: 100%;
      display: flex;
      flex-direction: column;
      gap: 40px;

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

      .main-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 30px;
        padding: 40px;
        background: rgba(171, 130, 255, 0.05);
        border-radius: 16px;
        backdrop-filter: blur(10px);

        .congrats-text {
          font-size: 24px;
          color: $text-white;
          font-weight: bold;
          text-align: center;
        }

        .download-text {
          font-size: 18px;
          color: $primary-purple;
          text-align: center;
        }

        .download-btn {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          padding: 16px 32px;
          background: $primary-purple;
          border: none;
          border-radius: 24px;
          cursor: pointer;
          transition: all 0.3s ease;
          gap: 8px;

          &:hover {
            box-shadow: 0 5px 25px rgba(171, 130, 255, 0.4);
            transform: translateY(-2px);
          }

          .btn-icon {
            font-size: 20px;
            color: $text-white;
          }

          .btn-text {
            font-size: 18px;
            color: $text-white;
            font-weight: 500;
          }
        }

        .description-section {
          display: flex;
          flex-direction: column;
          gap: 16px;
          margin-top: 20px;

          .description-text {
            font-size: 16px;
            color: $text-white;
            line-height: 1.6;
            text-align: center;
          }
        }

        .footer {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 8px;
          margin-top: 40px;

          .footer-text {
            font-size: 14px;
            color: $text-gray;
          }
        }

        .console-btn {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          padding: 16px 32px;
          background: rgba(171, 130, 255, 0.1);
          border: 1px solid $primary-purple;
          border-radius: 24px;
          cursor: pointer;
          transition: all 0.3s ease;
          gap: 8px;
          margin-top: 20px;

          &:hover {
            background: rgba(171, 130, 255, 0.2);
            box-shadow: 0 5px 25px rgba(171, 130, 255, 0.3);
            transform: translateY(-2px);
          }

          .btn-icon {
            font-size: 20px;
            color: $primary-purple;
          }

          .btn-text {
            font-size: 18px;
            color: $primary-purple;
            font-weight: 500;
          }
        }
      }
    }
  }
}
</style> 