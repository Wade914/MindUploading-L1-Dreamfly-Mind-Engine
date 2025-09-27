<template>
  <view v-if="visible" class="custom-modal" @click="handleMaskClick">
    <view class="modal-content" @click.stop>
      <!-- 标题 -->
      <view class="modal-header">
        <text class="modal-title">{{ title }}</text>
        <button v-if="showClose" class="close-btn" @click="handleCancel">×</button>
      </view>
      
      <!-- 内容 -->
      <view class="modal-body">
        <text class="modal-text">{{ content }}</text>
      </view>
      
      <!-- 按钮 -->
      <view class="modal-footer">
        <button 
          v-if="showCancel" 
          class="modal-btn cancel-btn" 
          @click="handleCancel"
        >
          {{ cancelText }}
        </button>
        <button 
          class="modal-btn confirm-btn" 
          :class="{ danger: type === 'danger' }"
          @click="handleConfirm"
        >
          {{ confirmText }}
        </button>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  name: 'CustomModal',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      default: '提示'
    },
    content: {
      type: String,
      default: ''
    },
    showCancel: {
      type: Boolean,
      default: true
    },
    showClose: {
      type: Boolean,
      default: false
    },
    cancelText: {
      type: String,
      default: '取消'
    },
    confirmText: {
      type: String,
      default: '确定'
    },
    type: {
      type: String,
      default: 'default', // default, danger
      validator: (value) => ['default', 'danger'].includes(value)
    },
    maskClosable: {
      type: Boolean,
      default: false
    }
  },
  emits: ['confirm', 'cancel', 'close'],
  methods: {
    handleConfirm() {
      this.$emit('confirm')
    },
    handleCancel() {
      this.$emit('cancel')
    },
    handleMaskClick() {
      if (this.maskClosable) {
        this.$emit('cancel')
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.custom-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: rgba(31, 31, 31, 0.95);
  border-radius: 16px;
  width: 90%;
  max-width: 400px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
}

.modal-header {
  padding: 24px 24px 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  .modal-title {
    font-size: 18px;
    font-weight: 600;
    color: #fff;
  }
  
  .close-btn {
    background: transparent;
    border: none;
    color: rgba(255, 255, 255, 0.6);
    font-size: 24px;
    cursor: pointer;
    padding: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    
    &:hover {
      color: #fff;
    }
  }
}

.modal-body {
  padding: 20px 24px;
  
  .modal-text {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.8);
    line-height: 1.6;
  }
}

.modal-footer {
  padding: 0 24px 24px 24px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.modal-btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  min-width: 80px;
  
  &.cancel-btn {
    background: transparent;
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: rgba(255, 255, 255, 0.8);
    
    &:hover {
      background: rgba(255, 255, 255, 0.05);
      border-color: rgba(255, 255, 255, 0.3);
      color: #fff;
    }
  }
  
  &.confirm-btn {
    background: #1890ff;
    color: #fff;
    
    &:hover {
      background: #40a9ff;
    }
    
    &.danger {
      background: #ff4d4f;
      
      &:hover {
        background: #ff7875;
      }
    }
  }
}
</style>
