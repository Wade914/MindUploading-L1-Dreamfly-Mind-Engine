<template>
  <view class="register-container">
    <view class="register-content">
      <view class="back-btn" @click="handleBack">
        <text class="iconfont icon-back">←</text>
      </view>
      
      <view class="header">
        <text class="title">创建账号</text>
        <text class="subtitle">开启你的数字意识之旅</text>
      </view>

      <view class="form-container">
        <view class="input-group">
          <text class="label">用户名</text>
          <input 
            type="text"
            v-model="form.username"
            placeholder="请输入用户名"
            placeholder-class="placeholder"
          />
        </view>

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

        <view class="input-group">
          <text class="label">确认密码</text>
          <input
            type="password"
            v-model="form.confirmPassword"
            placeholder="请再次输入密码"
            placeholder-class="placeholder"
          />
        </view>

        <view class="terms">
          <checkbox-group @change="handleTermsChange">
            <checkbox value="agreed" :checked="form.agreedToTerms" />
            <text class="terms-text">我已阅读并同意</text>
            <text class="terms-link" @click="handleViewTerms">服务条款</text>
            <text class="terms-text">和</text>
            <text class="terms-link" @click="handleViewPrivacy">隐私政策</text>
          </checkbox-group>
        </view>

        <button class="register-btn" @click="handleRegister" :disabled="!form.agreedToTerms">注册</button>

        <view class="login-link">
          <text>已有账号？</text>
          <text class="link" @click="handleLogin">立即登录</text>
        </view>
      </view>
    </view>

    <!-- AI 助手 -->
    <AIAssistant />
  </view>
</template>

<script setup>
import { ref } from 'vue'
import authManager from '@/utils/auth.js'
import AIAssistant from '@/components/AIAssistant.vue'

const form = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  agreedToTerms: false
})

const handleBack = () => {
  // 获取当前页面栈
  const pages = getCurrentPages()

  // 如果页面栈只有1个页面（说明是直接访问注册页），则跳转到欢迎页
  if (pages.length <= 1) {
    uni.redirectTo({
      url: '/pages/welcome/index'
    })
  } else {
    // 否则正常返回上一页
    uni.navigateBack()
  }
}

const handleTermsChange = (e) => {
  form.value.agreedToTerms = e.detail.value.length > 0
}

const handleRegister = () => {
  // 基础字段检查
  if (!form.value.username || !form.value.email || !form.value.password || !form.value.confirmPassword) {
    uni.showToast({
      title: '请填写完整信息',
      icon: 'none'
    })
    return
  }

  // 用户名长度检查
  if (form.value.username.length < 1 || form.value.username.length > 50) {
    uni.showToast({
      title: '用户名长度应在1-50个字符之间',
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

  // 密码长度检查
  if (form.value.password.length < 6 || form.value.password.length > 100) {
    uni.showToast({
      title: '密码长度应在6-100个字符之间',
      icon: 'none'
    })
    return
  }

  // 密码确认检查
  if (form.value.password !== form.value.confirmPassword) {
    uni.showToast({
      title: '两次输入的密码不一致',
      icon: 'none'
    })
    return
  }

  if (!form.value.agreedToTerms) {
    uni.showToast({
      title: '请同意服务条款和隐私政策',
      icon: 'none'
    })
    return
  }

  uni.showLoading({ title: '注册中...' })
  uni.request({
    url: '/api/register',
    method: 'POST',
    header: {
      'Content-Type': 'application/json'
    },
    data: {
      username: form.value.username,
      email: form.value.email,
      birth: null, 
      password: form.value.password
    },
    success: async (res) => {
      if (res.data.code === 200) {
        uni.showToast({ title: '注册成功', icon: 'success' })

        // 注册成功后直接使用返回的token
        const userData = res.data.data
        const token = userData.token

        if (token) {
          // 保存token到本地存储
          authManager.saveTokenToStorage(token)

          // 设置全局用户ID（兼容旧代码）
          getApp().globalData.user_id = userData.user_id

          // 新注册用户跳转到上传页面
          uni.navigateTo({ url: '/pages/upload/minddata' })
        } else {
          // 没有返回token，提示用户手动登录
          uni.showModal({
            title: '注册成功',
            content: '请返回登录页面使用新账号登录',
            showCancel: false,
            success: () => {
              uni.navigateTo({ url: '/pages/auth/login' })
            }
          })
        }
      } else {
        // 处理验证错误
        let errorMessage = res.data.message || '注册失败'

        // 如果有详细的验证错误，显示第一个错误
        if (res.data.details && res.data.details.length > 0) {
          const firstError = res.data.details[0]
          errorMessage = `${firstError.field}: ${firstError.message}`
        }

        uni.showToast({
          title: errorMessage,
          icon: 'none',
          duration: 3000  // 延长显示时间
        })
      }
    },
    fail: (err) => {
      console.error('注册请求失败:', err)
      uni.showToast({ title: '网络错误，请检查网络连接', icon: 'none' })
    },
    complete: () => uni.hideLoading()
  })
}

const handleLogin = () => {
  uni.navigateTo({
    url: '/pages/auth/login'
  })
}

const handleViewTerms = () => {
  // TODO: 查看服务条款
}

const handleViewPrivacy = () => {
  // TODO: 查看隐私政策
}
</script>

<style lang="scss">
.register-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
  padding: 40rpx;
  box-sizing: border-box;

  .register-content {
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

      .terms {
        margin-bottom: 60rpx;

        checkbox-group {
          display: flex;
          align-items: center;
          flex-wrap: wrap;
        }

        checkbox {
          margin-right: 16rpx;
          transform: scale(0.8);
        }

        .terms-text {
          font-size: 28rpx;
          color: rgba(255, 255, 255, 0.6);
        }

        .terms-link {
          font-size: 28rpx;
          color: #00a0ff;
          margin: 0 8rpx;
        }
      }

      .register-btn {
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

        &[disabled] {
          opacity: 0.5;
        }
      }

      .login-link {
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
  .register-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 60rpx;

    .register-content {
      max-width: 800rpx;
      width: 100%;
      padding-top: 0;

      .back-btn {
        top: -60rpx;
      }
    }
  }
}
</style> 