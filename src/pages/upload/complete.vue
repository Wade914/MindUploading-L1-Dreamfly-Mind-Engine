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

    async downloadMindCopy() {
      uni.showLoading({
        title: '正在生成意识体文件...'
      })

      try {
        // 从全局状态获取用户上传的数据
        const uploadData = getApp().globalData.uploadData || {}
        
        console.log('准备生成意识体文件，当前数据:', {
          name: uploadData.name,
          birth: uploadData.birth,
          voiceFile: !!uploadData.voiceFile,
          imageUrl: !!uploadData.imageUrl,
          height: uploadData.height,
          weight: uploadData.weight
        })
        
        // 检查必要数据
        if (!uploadData.name || !uploadData.birth) {
          throw new Error('缺少必要的个人信息')
        }

        // 转换音频和图片为base64
        let voiceBase64 = 'base64_encoded_voice_data'
        let imageBase64 = null

        // 处理音频文件
        if (uploadData.voiceFile) {
          try {
            console.log('开始转换音频文件...')
            voiceBase64 = await this.fileToBase64(uploadData.voiceFile)
            console.log('音频转换完成，长度:', voiceBase64.length)
          } catch (error) {
            console.error('音频转base64错误:', error)
          }
        } else {
          console.log('未找到音频文件')
        }

        // 处理图片文件
        if (uploadData.imageUrl) {
          try {
            console.log('开始转换图片...')
            imageBase64 = await this.imageUrlToBase64(uploadData.imageUrl)
            console.log('图片转换完成，长度:', imageBase64.length)
          } catch (error) {
            console.error('图片转base64错误:', error)
          }
        } else {
          console.log('未找到图片文件')
        }

        // 生成符合标准的.mind文件内容
        const mindData = {
          metadata: {
            name: uploadData.name,
            birth: uploadData.birth,
            occupation: uploadData.occupation || '未知',
            email: uploadData.email || '',
            personality_prompt: `你现在是${uploadData.name}的数字意识体。${uploadData.personality || '你应该根据用户的上传内容,准确模拟其性格、说话方式和思维模式。'}`,
            voice_prompt: voiceBase64,
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
            knowledge_base: `https://api.upme.cool/${uploadData.name}_knowledge`
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
        const fileContent = `export default ${JSON.stringify(mindData, null, 2)}`
        
        // 生成文件名（与后端保持一致）
        const fileName = `${uploadData.name}.mind`
        
        // === 新增：保存到后端 ===
        const user_id = getApp().globalData.user_id || ''
        await new Promise((resolve, reject) => {
          uni.request({
            url: '/api/mind',
            method: 'POST',
            data: {
              user_id,
              name: uploadData.name,
              birth: uploadData.birth,
              mind_content: fileContent
            },
            success: (res) => {
              if (res.data.code === 200) {
                console.log('Mind文件已保存到后端', res.data.data)
                resolve()
              } else {
                uni.showToast({ title: '后端保存失败', icon: 'none' })
                reject()
              }
            },
            fail: () => {
              uni.showToast({ title: '后端网络错误', icon: 'none' })
              reject()
            }
          })
        })
        // === 新增结束 ===

        // 创建Blob对象
        const blob = new Blob([fileContent], { type: 'application/javascript' })
        const url = URL.createObjectURL(blob)
        
        // 创建下载链接
        const link = document.createElement('a')
        link.href = url
        link.download = fileName
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)

        // 保存成功后的处理
        uni.hideLoading()
        uni.showToast({
          title: '意识体文件生成成功',
          icon: 'success',
          duration: 2000
        })

        // 延迟跳转到意识体操作台
        setTimeout(() => {
          uni.redirectTo({
            url: '/pages/welcome/explore'
          })
        }, 2000)

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
    
    goToConsole() {
      uni.navigateTo({
        url: '/pages/consciousness/index'
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