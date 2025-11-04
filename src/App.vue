<script>
export default {
  onLaunch: function () {
    console.log('App Launch')
  },
  onShow: function () {
    console.log('App Show')
  },
  onHide: function () {
    console.log('App Hide')
  },
}
</script>

<style>
@import url("@/static/css/toast-fix.css");

/* 全局样式重置 */
page {
  background-color: #f5f5f5;
  height: 100%;
}

/* 修复 uni-app H5 平台 input 无法输入的问题 */
uni-input,
uni-input input {
  pointer-events: auto !important;
  user-select: text !important;
  -webkit-user-select: text !important;
  cursor: text !important;
}

/* 如需定制 toast，仅做非布局属性，不要覆盖 display/position 等核心属性，避免影响隐藏 */
/* 保留空位，后续按需添加安全的样式覆盖 */
</style>
