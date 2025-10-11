// vite.config.js
import { defineConfig, loadEnv } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'
import path from 'path'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const isProd = (env.VUE_APP_ENVIRONMENT || 'development') === 'production'
  const APP_ENV = env.VUE_APP_ENVIRONMENT || 'development';
  return {
    plugins: [uni()],
    define: {
      // ✅ 注入一个简单布尔值和字符串（无 JSON.stringify 陷阱）
      __IS_PRODUCTION__: isProd,
      __API_BASE_URL__: isProd
        ? (env.VUE_APP_PROD_API_BASE_URL || 'http://8.129.25.16:8000')
        : (env.VUE_APP_DEV_API_BASE_URL || 'http://localhost:8000'),
      __FRONTEND_URL__: isProd
        ? (env.VUE_APP_PROD_FRONTEND_URL || 'http://8.129.25.16')
        : (env.VUE_APP_DEV_FRONTEND_URL || 'http://localhost:5173'),
      __DEBUG__: (env.VUE_APP_DEBUG || 'false') === 'true'
    },
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: `@import "@/styles/variables.scss";`
        }
      }
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src')
      }
    },
    server: {
      port: 5173,
      proxy: {
        '/api': {
          target: APP_ENV === 'production'
            ? (env.VUE_APP_PROD_API_BASE_URL || 'http://8.129.25.16:8000')
            : (env.VUE_APP_DEV_API_BASE_URL || 'http://localhost:8000'),
          changeOrigin: true,
        }
      }
    }
  }
})