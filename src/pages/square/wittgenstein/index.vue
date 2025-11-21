<template>
  <view class="wittgenstein-container">
    <web-view :src="htmlUrl" @message="handleMessage"></web-view>

    <!-- AI 助手 -->
    <AIAssistant />
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import authManager from '@/utils/auth.js'
import AIAssistant from '@/components/AIAssistant.vue'

const htmlUrl = ref('/static/square/wittgenstein.html')

onMounted(() => {
  // 检查用户是否登录
  if (!authManager.isLoggedIn()) {
    uni.showToast({
      title: '请先登录',
      icon: 'none'
    })
    setTimeout(() => {
      uni.navigateBack()
    }, 1500)
    return
  }

  console.log('加载维特根斯坦页面HTML:', htmlUrl.value)
})

// 接收HTML页面发来的消息
const handleMessage = (e) => {
  console.log('收到HTML消息:', e.detail.data)

  const data = e.detail.data[0] || e.detail.data || {}
  const { type, action, url } = data

  if (type === 'needLogin') {
    uni.showToast({
      title: '请先登录',
      icon: 'none'
    })
    setTimeout(() => {
      uni.navigateBack()
    }, 1500)
  } else if (action === 'navigateTo' && url) {
    console.log('跳转到:', url)
    uni.navigateTo({
      url: url,
      fail: (err) => {
        console.error('跳转失败:', err)
        uni.showToast({
          title: '页面跳转失败',
          icon: 'none'
        })
      }
    })
  }
}
</script>

<style scoped>
.wittgenstein-container {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}
</style>

