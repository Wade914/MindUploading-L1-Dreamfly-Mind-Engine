import { defineConfig, loadEnv } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd())

  return {
    plugins: [
      uni(),
    ],
    // 定义全局常量，注入到代码中
    define: {
      'process.env.VUE_APP_ENVIRONMENT': JSON.stringify(env.VUE_APP_ENVIRONMENT || 'development'),
      'process.env.VUE_APP_DEV_API_BASE_URL': JSON.stringify(env.VUE_APP_DEV_API_BASE_URL || 'http://localhost:8000'),
      'process.env.VUE_APP_PROD_API_BASE_URL': JSON.stringify(env.VUE_APP_PROD_API_BASE_URL || 'https://upme.cool'),
      'process.env.VUE_APP_DEV_FRONTEND_URL': JSON.stringify(env.VUE_APP_DEV_FRONTEND_URL || 'http://localhost:5173'),
      'process.env.VUE_APP_PROD_FRONTEND_URL': JSON.stringify(env.VUE_APP_PROD_FRONTEND_URL || 'https://upme.cool'),
      'process.env.VUE_APP_DEBUG': JSON.stringify(env.VUE_APP_DEBUG || 'false'),
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
          target: env.VUE_APP_ENVIRONMENT === 'production'
            ? (env.VUE_APP_PROD_API_BASE_URL || 'https://upme.cool')
            : (env.VUE_APP_DEV_API_BASE_URL || 'http://localhost:8000'),
          changeOrigin: true,
        }
      }
    }
  }
})
