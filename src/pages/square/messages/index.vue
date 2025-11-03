<template>
  <view class="container">
    <web-view :src="webviewUrl"></web-view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      webviewUrl: ''
    };
  },
  onLoad() {
    // 获取静态HTML文件的URL
    const baseUrl = window.location.origin;
    this.webviewUrl = `${baseUrl}/static/square/messages.html`;
    console.log('加载消息页面HTML:', this.webviewUrl);
  },
  onShow() {
    console.log('消息页面显示');
  }
};
</script>

<style scoped>
.container {
  width: 100%;
  height: 100vh;
}
</style>

