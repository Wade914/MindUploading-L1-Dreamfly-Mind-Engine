import { defineConfig, loadEnv } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'
import path from 'path'

export default defineConfig(({ mode }) => {
  // 加载 .env 文件（不限 VITE_ 前缀）
  const env = loadEnv(mode, process.cwd(), '')

  // ✅ 必须用 const 声明！
  const APP_ENV = env.VUE_APP_ENVIRONMENT || 'development'

  return {
    plugins: [uni()],
    define: {
      'process.env': {
        // 字符串字面量用于比较 → 需要 JSON.stringify
        VUE_APP_ENVIRONMENT: JSON.stringify(APP_ENV),
        VUE_APP_DEBUG: JSON.stringify(env.VUE_APP_DEBUG || 'false'),

        // 字符串字面量用于拼接 URL → ❌ 不要 JSON.stringify！
        VUE_APP_DEV_API_BASE_URL: env.VUE_APP_DEV_API_BASE_URL || 'http://localhost:8000',
        VUE_APP_PROD_API_BASE_URL: env.VUE_APP_PROD_API_BASE_URL || 'http://8.129.25.16:8000',
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
          target: APP_ENV === 'production'
            ? (env.VUE_APP_PROD_API_BASE_URL || 'http://8.129.25.16:8000')
            : (env.VUE_APP_DEV_API_BASE_URL || 'http://localhost:8000'),
          changeOrigin: true,
        }
      }
    }
  }
})