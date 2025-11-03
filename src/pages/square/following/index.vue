<template>
  <view class="container">
    <web-view :src="webviewUrl" @message="handleMessage"></web-view>
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
    this.webviewUrl = `${baseUrl}/static/square/following.html`;
    console.log('加载关注页面HTML:', this.webviewUrl);
  },
  onShow() {
    console.log('关注页面显示');
  },
  methods: {
    handleMessage(e) {
      console.log('收到HTML消息:', e.detail.data);

      const data = e.detail.data[0] || e.detail.data || {};
      const { type, action, url } = data;

      if (action === 'redirectTo' && url) {
        console.log('重定向到:', url);
        uni.redirectTo({
          url: url,
          fail: (err) => {
            console.error('重定向失败:', err);
            uni.showToast({
              title: '页面跳转失败',
              icon: 'none'
            });
          }
        });
      } else if (action === 'navigateTo' && url) {
        console.log('跳转到:', url);
        uni.navigateTo({
          url: url,
          fail: (err) => {
            console.error('跳转失败:', err);
            uni.showToast({
              title: '页面跳转失败',
              icon: 'none'
            });
          }
        });
      }
    }
  }
};
</script>

<style scoped>
.container {
  width: 100%;
  height: 100vh;
}
</style>

