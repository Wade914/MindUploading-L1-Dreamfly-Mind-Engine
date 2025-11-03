<template>
  <view class="profile-container">
    <web-view :src="htmlUrl" @message="handleMessage"></web-view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import authManager from '@/utils/auth.js'

const htmlUrl = ref('/static/square/profile.html')

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

  console.log('加载用户资料HTML:', htmlUrl.value)
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
.profile-container {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}
</style>

