<template>
  <view class="login-container">
    <view class="login-content">
      <view class="back-btn" @click="handleBack">
        <text class="iconfont icon-back">←</text>
      </view>
      
      <view class="header">
        <text class="title">登录云己</text>
        <text class="subtitle">连接你的数字意识</text>
      </view>

      <view class="form-container">
        <view class="input-group">
          <text class="label">邮箱</text>
          <input 
            type="text"
            v-model="form.email"
            placeholder="请输入邮箱"
            placeholder-class="placeholder"
          />
        </view>

        <view class="input-group">
          <text class="label">密码</text>
          <input
            type="password"
            v-model="form.password"
            placeholder="请输入密码"
            placeholder-class="placeholder"
          />
        </view>

        <view class="forgot-password">
          <text @click="handleForgotPassword">忘记密码？</text>
        </view>

        <button class="login-btn" @click="handleLogin">登录</button>

        <view class="register-link">
          <text>还没有账号？</text>
          <text class="link" @click="handleRegister">立即注册</text>
        </view>
      </view>
    </view>

    <!-- AI 助手 -->
    <AIAssistant />
  </view>
</template>

<script setup>
import { ref } from 'vue'
import AIAssistant from '@/components/AIAssistant.vue'
import authManager from '@/utils/auth.js'

const form = ref({
  email: '',
  password: ''
})

const handleBack = () => {
  // 获取当前页面栈
  const pages = getCurrentPages()

  // 如果页面栈只有1个页面（说明是直接访问登录页），则跳转到欢迎页
  if (pages.length <= 1) {
    uni.redirectTo({
      url: '/pages/welcome/index'
    })
  } else {
    // 否则正常返回上一页
    uni.navigateBack()
  }
}

const handleLogin = async () => {
  if (!form.value.email || !form.value.password) {
    uni.showToast({
      title: '请填写完整信息',
      icon: 'none'
    })
    return
  }

  // 邮箱格式检查
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(form.value.email)) {
    uni.showToast({
      title: '请输入正确的邮箱格式',
      icon: 'none'
    })
    return
  }

  uni.showLoading({ title: '登录中...' })

  try {
    const result = await authManager.login(form.value.email, form.value.password)

    if (result.success) {
      uni.hideLoading()
      uni.showToast({
        title: '登录成功',
        icon: 'success'
      })

      // 跳转到意识体控制台
      setTimeout(() => {
        uni.redirectTo({
          url: '/pages/consciousness/index'
        })
      }, 1500)
    } else {
      uni.hideLoading()
      uni.showToast({
        title: result.message || '登录失败',
        icon: 'error'
      })
    }
  } catch (error) {
    uni.hideLoading()
    console.error('登录失败:', error)
    uni.showToast({
      title: '登录失败，请稍后重试',
      icon: 'error'
    })
  }
}

const handleRegister = () => {
  uni.navigateTo({
    url: '/pages/auth/register'
  })
}

const handleForgotPassword = () => {
  uni.navigateTo({
    url: '/pages/auth/forgot-password'
  })
}
</script>

<style lang="scss">
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
  padding: 40rpx;
  box-sizing: border-box;

  .login-content {
    position: relative;
    padding-top: 100rpx;

    .back-btn {
      position: absolute;
      top: 0;
      left: 0;
      padding: 20rpx;
      
      .icon-back {
        color: #ffffff;
        font-size: 40rpx;
      }
    }

    .header {
      margin-bottom: 80rpx;
      
      .title {
        font-size: 48rpx;
        color: #ffffff;
        font-weight: bold;
        margin-bottom: 20rpx;
        display: block;
      }

      .subtitle {
        font-size: 28rpx;
        color: rgba(255, 255, 255, 0.6);
      }
    }

    .form-container {
      .input-group {
        margin-bottom: 40rpx;

        .label {
          font-size: 28rpx;
          color: rgba(255, 255, 255, 0.8);
          margin-bottom: 16rpx;
          display: block;
        }

        input {
          width: 100%;
          height: 96rpx;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 16rpx;
          padding: 0 32rpx;
          color: #ffffff;
          font-size: 32rpx;
        }

        .placeholder {
          color: rgba(255, 255, 255, 0.3);
        }
      }

      .forgot-password {
        text-align: right;
        margin-bottom: 60rpx;

        text {
          color: rgba(255, 255, 255, 0.6);
          font-size: 28rpx;
        }
      }

      .login-btn {
        width: 100%;
        height: 96rpx;
        background: linear-gradient(135deg, #00a0ff 0%, #0057ff 100%);
        border-radius: 48rpx;
        color: #ffffff;
        font-size: 32rpx;
        font-weight: 500;
        margin-bottom: 40rpx;
        display: flex;
        align-items: center;
        justify-content: center;
      }

      .register-link {
        text-align: center;

        text {
          font-size: 28rpx;
          color: rgba(255, 255, 255, 0.6);

          &.link {
            color: #00a0ff;
            margin-left: 8rpx;
          }
        }
      }
    }
  }
}

/* 响应式样式 */
@media screen and (min-width: 768px) {
  .login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 60rpx;

    .login-content {
      max-width: 800rpx;
      width: 100%;
      padding-top: 0;

      .back-btn {
        top: -60rpx;
      }
    }
  }
}

/* 修复 uni-app Toast 图标居中问题 */
::v-deep .uni-toast {
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
}

::v-deep .uni-toast .uni-icon {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  margin: 0 auto !important;
}

::v-deep .uni-toast .uni-toast__content {
  text-align: center !important;
}
</style>