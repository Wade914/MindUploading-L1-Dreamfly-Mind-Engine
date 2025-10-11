import { defineConfig, loadEnv } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'
import path from 'path'

export default defineConfig(({ mode }) => {
  // 加载 .env 文件（注意：dev 命令默认 mode = 'development'）
  const env = loadEnv(mode, process.cwd(), '') // 第三个参数 '' 表示加载所有变量，不限于 VITE_

  // 确保 VUE_APP_ENVIRONMENT 有值
  const appEnv = env.VUE_APP_ENVIRONMENT || 'development'

  return {
    plugins: [uni()],
define: {
  'process.env': {
    VUE_APP_ENVIRONMENT: JSON.stringify(APP_ENV), // ✅ 字符串需要 stringify
    VUE_APP_DEBUG: JSON.stringify(env.VUE_APP_DEBUG || 'false'), // ✅ 布尔/字符串需要
    VUE_APP_DEV_API_BASE_URL: env.VUE_APP_DEV_API_BASE_URL || 'http://localhost:8000', // ❌ 不要 stringify！
    VUE_APP_PROD_API_BASE_URL: env.VUE_APP_PROD_API_BASE_URL || 'http://8.129.25.16:8000', // ❌ 不要 stringify！
    VUE_APP_DEV_FRONTEND_URL: env.VUE_APP_DEV_FRONTEND_URL || 'http://localhost:5173',
    VUE_APP_PROD_FRONTEND_URL: env.VUE_APP_PROD_FRONTEND_URL || 'http://8.129.25.16',
  }
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
          target: appEnv === 'production'
            ? (env.VUE_APP_PROD_API_BASE_URL || 'http://8.129.25.16:8000')
            : (env.VUE_APP_DEV_API_BASE_URL || 'http://localhost:8000'),
          changeOrigin: true,
        }
      }
    }
  }
})