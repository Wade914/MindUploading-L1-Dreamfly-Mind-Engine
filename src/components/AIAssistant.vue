<template>
  <view class="ai-assistant">
    <!-- 聊天窗口 -->
    <view 
      class="chat-window" 
      :class="{ 'show': isOpen }"
      @click.stop
    >
      <!-- 窗口头部 -->
      <view class="chat-header">
        <view class="header-left">
          <image class="avatar-small" src="/static/avatar.jpg" mode="aspectFill"></image>
          <view class="header-info">
            <text class="header-title">AI 助手</text>
            <text class="header-status">在线</text>
          </view>
        </view>
        <view class="header-actions">
          <text class="action-btn" @click="minimizeWindow">—</text>
          <text class="action-btn" @click="closeWindow">✕</text>
        </view>
      </view>

      <!-- 消息列表 -->
      <scroll-view class="message-list" scroll-y :scroll-top="scrollTop">
        <!-- 欢迎消息 -->
        <view class="message-item ai-message" v-if="messages.length === 0">
          <view class="message-bubble">
            <text class="message-text">你好！我是 DreamFly 的 AI 助手，有什么可以帮助你的吗？</text>
          </view>
        </view>

        <!-- 消息列表 -->
        <view 
          v-for="(msg, index) in messages" 
          :key="index"
          class="message-item"
          :class="msg.type === 'user' ? 'user-message' : 'ai-message'"
        >
          <view class="message-bubble">
            <text class="message-text">{{ msg.content }}</text>
          </view>
        </view>

        <!-- 加载中 -->
        <view class="message-item ai-message" v-if="isLoading">
          <view class="message-bubble">
            <view class="typing-indicator">
              <view class="dot"></view>
              <view class="dot"></view>
              <view class="dot"></view>
            </view>
          </view>
        </view>
      </scroll-view>

      <!-- 输入框 -->
      <view class="input-area">
        <input
          type="text"
          class="message-input"
          v-model="inputText"
          placeholder="输入你的问题..."
          @confirm="sendMessage"
        />
        <view class="send-btn" @click="sendMessage">
          <text class="send-icon">➤</text>
        </view>
      </view>
    </view>

    <!-- 悬浮按钮 -->
    <view 
      class="float-button" 
      :class="{ 'hide': isOpen }"
      @click="toggleWindow"
    >
      <image class="avatar-icon" src="/static/avatar.jpg" mode="aspectFill"></image>
      <view class="pulse-ring"></view>
    </view>
  </view>
</template>

<script setup>
import { ref, nextTick, onMounted, onBeforeUnmount } from 'vue'

const isOpen = ref(false)
const inputText = ref('')
const messages = ref([])
const isLoading = ref(false)
const scrollTop = ref(0)

// 监听页面切换，自动关闭聊天窗口
let pageHideHandler = null

onMounted(() => {
  // 在 H5 环境下监听页面隐藏事件
  // #ifdef H5
  pageHideHandler = () => {
    if (isOpen.value) {
      isOpen.value = false
    }
  }

  // 监听页面可见性变化
  document.addEventListener('visibilitychange', () => {
    if (document.hidden && isOpen.value) {
      isOpen.value = false
    }
  })

  // 监听路由变化（uni-app 的页面切换）
  window.addEventListener('beforeunload', pageHideHandler)
  // #endif
})

onBeforeUnmount(() => {
  // 清理事件监听
  // #ifdef H5
  if (pageHideHandler) {
    window.removeEventListener('beforeunload', pageHideHandler)
  }
  // #endif

  // 组件卸载时关闭窗口
  isOpen.value = false
})

// 切换窗口
const toggleWindow = () => {
  isOpen.value = !isOpen.value
}

// 关闭窗口
const closeWindow = () => {
  isOpen.value = false
}

// 最小化窗口
const minimizeWindow = () => {
  isOpen.value = false
}

// 发送消息
const sendMessage = async () => {
  if (!inputText.value.trim()) return

  // 添加用户消息
  messages.value.push({
    type: 'user',
    content: inputText.value
  })

  const userMessage = inputText.value
  inputText.value = ''

  // 滚动到底部
  nextTick(() => {
    scrollTop.value = 99999
  })

  // 调用扣子 API
  isLoading.value = true

  try {
    // 构建请求数据
    const requestData = {
      user_id: '123456789',
      stream: true,
      auto_save_history: true,
      additional_messages: [
        {
          role: 'user',
          type: 'question',
          content: userMessage,
          content_type: 'text'
        }
      ]
    }

    // 发起流式请求
    const response = await fetch(`${__API_BASE_URL__}/api/ai/coze/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData)
    })

    if (!response.ok) {
      throw new Error('API 请求失败')
    }

    // 处理流式响应
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let aiMessage = {
      type: 'ai',
      content: ''
    }

    // 添加 AI 消息占位符
    messages.value.push(aiMessage)
    isLoading.value = false

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value, { stream: true })
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6).trim()
          if (data === '[DONE]') {
            break
          }

          try {
            const parsed = JSON.parse(data)
            if (parsed.content) {
              aiMessage.content += parsed.content
              // 触发响应式更新
              messages.value = [...messages.value]
              // 滚动到底部
              nextTick(() => {
                scrollTop.value = 99999
              })
            }
          } catch (e) {
            console.error('解析响应失败:', e)
          }
        }
      }
    }

  } catch (error) {
    console.error('发送消息失败:', error)
    isLoading.value = false
    messages.value.push({
      type: 'ai',
      content: '抱歉，服务暂时不可用，请稍后再试。'
    })
  }

  nextTick(() => {
    scrollTop.value = 99999
  })
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.ai-assistant {
  position: fixed;
  z-index: 9999;
}

/* 悬浮按钮 */
.float-button {
  position: fixed;
  right: 24px;
  bottom: 120px;
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(171, 130, 255, 0.9), rgba(171, 130, 255, 0.7));
  box-shadow: 0 8px 32px rgba(171, 130, 255, 0.4);
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
  
  &:hover {
    transform: scale(1.1);
    box-shadow: 0 12px 40px rgba(171, 130, 255, 0.6);
  }

  &.hide {
    opacity: 0;
    pointer-events: none;
    transform: scale(0);
  }

  .avatar-icon {
    width: 100%;
    height: 100%;
    border-radius: 50%;
  }

  .pulse-ring {
    position: absolute;
    top: -5px;
    left: -5px;
    right: -5px;
    bottom: -5px;
    border: 2px solid rgba(171, 130, 255, 0.6);
    border-radius: 50%;
    animation: pulse 2s infinite;
  }
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.5;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 聊天窗口 */
.chat-window {
  position: fixed;
  right: 24px;
  bottom: 206px;
  width: 360px;
  height: 500px;
  background: rgba(26, 26, 26, 0.95);
  backdrop-filter: blur(20px);
  border: 2px solid rgba(171, 130, 255, 0.3);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  opacity: 0;
  transform: scale(0.8) translateY(20px);
  pointer-events: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &.show {
    opacity: 1;
    transform: scale(1) translateY(0);
    pointer-events: auto;
  }
}

/* 窗口头部 */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid rgba(171, 130, 255, 0.2);

  .header-left {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .avatar-small {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    border: 2px solid rgba(171, 130, 255, 0.5);
  }

  .header-info {
    display: flex;
    flex-direction: column;
  }

  .header-title {
    color: $text-white;
    font-size: 16px;
    font-weight: 600;
  }

  .header-status {
    color: rgba(0, 255, 0, 0.8);
    font-size: 12px;
  }

  .header-actions {
    display: flex;
    gap: 8px;
  }

  .action-btn {
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: $text-gray;
    font-size: 18px;
    cursor: pointer;
    border-radius: 6px;
    transition: all 0.2s ease;

    &:hover {
      background: rgba(255, 255, 255, 0.1);
      color: $text-white;
    }
  }
}

/* 消息列表 */
.message-list {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

.message-item {
  margin-bottom: 16px;
  display: flex;

  &.user-message {
    justify-content: flex-end;

    .message-bubble {
      background: linear-gradient(135deg, rgba(171, 130, 255, 0.8), rgba(171, 130, 255, 0.6));
      border-radius: 16px 16px 4px 16px;
    }
  }

  &.ai-message {
    justify-content: flex-start;

    .message-bubble {
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(171, 130, 255, 0.2);
      border-radius: 16px 16px 16px 4px;
    }
  }
}

.message-bubble {
  max-width: 80%;
  padding: 12px 16px;
  animation: slideIn 0.3s ease;
}

.message-text {
  color: $text-white;
  font-size: 14px;
  line-height: 1.5;
  word-wrap: break-word;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 输入中动画 */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 4px 0;
}

.dot {
  width: 8px;
  height: 8px;
  background: rgba(171, 130, 255, 0.6);
  border-radius: 50%;
  animation: typing 1.4s infinite;

  &:nth-child(2) {
    animation-delay: 0.2s;
  }

  &:nth-child(3) {
    animation-delay: 0.4s;
  }
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.6;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

/* 输入区域 */
.input-area {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-top: 1px solid rgba(171, 130, 255, 0.2);
}

.message-input {
  flex: 1;
  height: 44px;
  padding: 0 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(171, 130, 255, 0.3);
  border-radius: 22px;
  color: $text-white;
  font-size: 14px;
  transition: all 0.3s ease;

  &:focus {
    background: rgba(255, 255, 255, 0.1);
    border-color: $primary-purple;
    outline: none;
  }

  &::placeholder {
    color: rgba(255, 255, 255, 0.3);
  }
}

.send-btn {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(171, 130, 255, 0.8), rgba(171, 130, 255, 0.6));
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    transform: scale(1.1);
    box-shadow: 0 4px 16px rgba(171, 130, 255, 0.4);
  }

  &:active {
    transform: scale(0.95);
  }
}

.send-icon {
  color: $text-white;
  font-size: 18px;
  font-weight: bold;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .chat-window {
    right: 12px;
    bottom: 180px;
    width: calc(100vw - 24px);
    max-width: 360px;
    height: 60vh;
    max-height: 500px;
  }

  .float-button {
    right: 16px;
    bottom: 100px;
    width: 64px;
    height: 64px;
  }
}
</style>

