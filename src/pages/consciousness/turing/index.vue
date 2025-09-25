<template>
  <view class="terminal">
    <view class="terminal-header">
      <text class="terminal-title">consciousness@dreamfly:~$ {{ isActive ? 'active' : 'standby' }}</text>
      <view class="terminal-controls">
        <text class="control minimize">-</text>
        <text class="control maximize">□</text>
        <text class="control close" @click="goBack">×</text>
      </view>
    </view>

    <scroll-view 
      class="terminal-body" 
      scroll-y 
      :scroll-top="scrollTop"
      @scrolltoupper="onScrollToUpper"
      @scrolltolower="onScrollToLower"
    >
      <view class="terminal-content">
        <view class="boot-sequence">
          <text class="boot-text">DreamFly OS [Version 1.0.0]</text>
          <text class="boot-text">(c) 2024 DreamFly Corporation. All rights reserved.</text>
          <text class="boot-text">Initializing consciousness connection...</text>
          <text class="boot-text">Connection established.</text>
        </view>

        <!-- 意识体头像和对话区域 -->
        <view :class="['ai-interface', { 'active': isActive }]">
          <!-- 固定头像区域 -->
          <view class="ai-avatar">
            <text v-for="(line, index) in faceLines" 
                  :key="index" 
                  class="face-line"
                  :class="{ 'appear': isStarting || isActive }"
                  :style="{ animationDelay: `${index * 0.1}s` }">
              {{ line }}
            </text>
          </view>

          <!-- 对话消息区域 -->
          <view class="message-area">
            <view 
              v-for="(message, index) in messages" 
              :key="index"
              :class="['terminal-line', message.role]"
            >
              <template v-if="message.role === 'user'">
                <text class="prompt">user@dreamfly:~$</text>
                <text class="command">{{ message.content }}</text>
              </template>
              <template v-if="message.role === 'assistant'">
                <text class="response" :class="{ 'typing': message.isTyping }">{{ message.content }}</text>
                <text v-if="message.isTyping" class="cursor">_</text>
              </template>
            </view>
          </view>
        </view>
      </view>
    </scroll-view>

    <view class="terminal-input">
      <text class="prompt">user@dreamfly:~$</text>
      <input
        v-model="inputMessage"
        class="command-input"
        type="text"
        :disabled="isProcessing"
        @confirm="sendMessage"
        placeholder="输入命令..."
        ref="commandInput"
        :focus="true"
        :adjust-position="false"
        :cursor-spacing="0"
        :hold-keyboard="true"
      />
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      messages: [],
      inputMessage: '',
      isProcessing: false,
      scrollTop: 0,
      typingSpeed: 50,
      isStarting: false,
      isActive: false,
      faceLines: [
        '    ┌────────────────────┐    ',
        '    │   CONSCIOUSNESS    │    ',
        '    ├────────────────────┤    ',
        '    │  ░░░░░░░░░░░░░░░  │    ',
        '    │  ░░▓▓▓░░░░▓▓▓░░░  │    ',
        '    │  ░░▓█▓░░░░▓█▓░░░  │    ',
        '    │  ░░▓▓▓░░░░▓▓▓░░░  │    ',
        '    │  ░░░░░░▀▀░░░░░░░  │    ',
        '    │  ░░░░░░░░░░░░░░░  │    ',
        '    │  ░░░░░░░░░░░░░░░  │    ',
        '    └────────────────────┘    ',
        '      Neural Core v1.0.0      ',
        '      > SYSTEM ONLINE <       '
      ]
    }
  },

  onLoad() {
    // 页面加载时自动启动
    this.startUpMe()
  },

  methods: {
    initTerminal() {
      // 不再添加默认的help消息
    },

    goBack() {
      uni.navigateBack()
    },

    async typeMessage(message) {
      const finalContent = message
      let currentContent = ''
      this.messages.push({
        role: 'assistant',
        content: currentContent,
        isTyping: true
      })
      
      const currentMessage = this.messages[this.messages.length - 1]
      
      for (let char of finalContent) {
        currentContent += char
        currentMessage.content = currentContent
        await new Promise(resolve => setTimeout(resolve, this.typingSpeed))
      }
      
      currentMessage.isTyping = false
    },

    async startUpMe() {
      if (this.isStarting || this.isActive) return
      
      this.isStarting = true
      this.messages = []
      
      // 等待头像动画完成
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // 显示欢迎消息
      await this.typeMessage('你好，我的本体。我已完成意识同步，随时待命。')
      
      this.isStarting = false
      this.isActive = true
    },

    async sendMessage() {
      if (!this.inputMessage.trim() || this.isProcessing) return
      
      const command = this.inputMessage.trim()
      this.messages.push({
        role: 'user',
        content: command,
        timestamp: new Date().toISOString()
      })
      
      this.inputMessage = ''
      this.isProcessing = true
      
      try {
        let response
        
        // 处理特殊命令
        if (command === 'help') {
          response = `可用命令列表：
help - 显示此帮助信息
clear - 清除屏幕
status - 显示意识体状态
memory - 访问记忆库
think - 进入深度思考模式
startupme - 启动意识体
exit - 断开连接`
        } else if (command === 'startupme') {
          await this.startUpMe()
          this.isProcessing = false
          return
        } else if (command === 'clear') {
          this.messages = []
          this.isProcessing = false
          return
        } else if (command === 'exit') {
          await this.typeMessage('正在断开连接...')
          setTimeout(() => this.goBack(), 1000)
          return
        } else {
          // 模拟AI响应
          response = await this.getAIResponse(command)
        }
        
        await this.typeMessage(response)
      } catch (error) {
        console.error('Error:', error)
        await this.typeMessage('Error: 命令执行失败')
      } finally {
        this.isProcessing = false
        this.$nextTick(() => {
          this.scrollToBottom()
        })
      }
    },

    async getAIResponse(command) {
      // 模拟AI响应
      await new Promise(resolve => setTimeout(resolve, 500))
      return `正在处理命令: ${command}\n这是一个测试响应,实际开发时需要接入后端API。`
    },

    scrollToBottom() {
      // 获取scroll-view的高度
      const query = uni.createSelectorQuery().in(this)
      query.select('.terminal-body').boundingClientRect(data => {
        this.scrollTop = data.height * 2 // 确保滚动到底部
      }).exec()
    },

    onScrollToUpper() {
      // 可以在这里加载历史消息
      console.log('到顶部了')
    },

    onScrollToLower() {
      // 滚动到底部的处理
      console.log('到底部了')
    }
  }
}
</script>

<style lang="scss">
.terminal {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #1a1a1a;
  font-family: 'Courier New', Courier, monospace;
  
  .terminal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 16px;
    background: #2d2d2d;
    border-bottom: 1px solid #3d3d3d;
    
    .terminal-title {
      color: #fff;
      font-size: 14px;
    }
    
    .terminal-controls {
      display: flex;
      gap: 16px;
      
      .control {
        color: #999;
        cursor: pointer;
        font-size: 16px;
        
        &:hover {
          color: #fff;
        }
        
        &.close:hover {
          color: #ff4444;
        }
      }
    }
  }
  
  .terminal-body {
    flex: 1;
    padding: 16px;
    overflow-y: auto;
    
    .terminal-content {
      .boot-sequence {
        margin-bottom: 20px;
        
        .boot-text {
          color: #00ff00;
          font-size: 14px;
          line-height: 1.5;
          display: block;
        }
      }
      
      .terminal-line {
        margin-bottom: 12px;
        font-size: 14px;
        line-height: 1.5;
        
        &.user {
          color: #fff;
          
          .prompt {
            color: #00ff00;
            margin-right: 8px;
          }
          
          .command {
            color: #fff;
          }
        }
        
        &.assistant {
          color: #00ff00;
          
          .response {
            white-space: pre-wrap;
            
            &.typing {
              border-right: 2px solid #00ff00;
              animation: blink 1s step-end infinite;
            }
          }
        }
      }
    }
  }
  
  .terminal-input {
    display: flex;
    align-items: center;
    padding: 16px;
    background: #1a1a1a;
    border-top: 1px solid #3d3d3d;
    
    .prompt {
      color: #00ff00;
      margin-right: 8px;
      font-size: 14px;
    }
    
    .command-input {
      flex: 1;
      background: transparent;
      border: none;
      color: #fff;
      font-family: 'Courier New', Courier, monospace;
      font-size: 14px;
      height: 24px;
      line-height: 24px;
      padding: 0;
      
      &:focus {
        outline: none;
      }
      
      &::placeholder {
        color: #666;
      }
    }
  }
}

@keyframes blink {
  0%, 100% {
    border-color: transparent;
  }
  50% {
    border-color: #00ff00;
  }
}

.ai-interface {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 20px 0;
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.5s ease;
  
  &.active {
    opacity: 1;
    transform: translateY(0);
  }
  
  .ai-avatar {
    background: rgba(0, 255, 0, 0.05);
    border: 1px solid rgba(0, 255, 0, 0.1);
    border-radius: 4px;
    padding: 16px;
    margin-bottom: 20px;
    width: fit-content;
    position: sticky;
    top: 20px;
    z-index: 10;
    backdrop-filter: blur(5px);
    
    .face-line {
      color: #00ff00;
      font-family: monospace;
      font-size: 14px;
      line-height: 1.2;
      white-space: pre;
      display: block;
      opacity: 0;
      text-shadow: 0 0 5px rgba(0, 255, 0, 0.5);
      
      &.appear {
        animation: fadeIn 0.5s linear forwards;
      }
    }
  }
  
  .message-area {
    width: 100%;
    padding: 0 20px;
    margin-top: 20px;
    
    .terminal-line {
      margin-bottom: 12px;
      padding: 12px 16px;
      border-radius: 4px;
      background: rgba(0, 255, 0, 0.05);
      backdrop-filter: blur(5px);
      
      &.assistant {
        border-left: 2px solid #00ff00;
        color: #00ff00;
      }
      
      &.user {
        background: rgba(255, 255, 255, 0.05);
        border-left: 2px solid #fff;
        color: #fff;
      }
      
      .response {
        font-size: 14px;
        line-height: 1.5;
      }
    }
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style> 