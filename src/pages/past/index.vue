<template>
  <view class="past-container">
    <view class="header">
      <text class="title">往事</text>
      <text class="subtitle">记录你的生命故事</text>
    </view>
    
    <view class="content">
      <view class="empty-state">
        <image class="empty-image" src="/static/images/clock.png" mode="aspectFit"></image>
        <text class="empty-text">这里将是你的回忆录</text>
        <text class="empty-subtext">记录下那些值得铭记的时刻</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import TabBar from '@/components/TabBar.vue'

const currentTab = ref('past')
</script>

<style lang="scss">
.past-container {
  min-height: 100vh;
  background: #fff;
  padding: 40px 30px 120px;
}

.header {
  margin-bottom: 40px;
  
  .title {
    font-size: 28px;
    color: #000;
    font-weight: bold;
    margin-bottom: 8px;
    display: block;
  }
  
  .subtitle {
    font-size: 14px;
    color: #666;
  }
}

.content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  
  .empty-image {
    width: 160px;
    height: 160px;
    margin-bottom: 30px;
    opacity: 0.5;
  }
  
  .empty-text {
    font-size: 18px;
    color: #333;
    margin-bottom: 10px;
    font-weight: 500;
  }
  
  .empty-subtext {
    font-size: 14px;
    color: #999;
  }
}
</style> 