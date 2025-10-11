// vite.config.js
import { defineConfig, loadEnv } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'
import path from 'path'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const isProd = (env.VUE_APP_ENVIRONMENT || 'development') === 'production'

  return {
    plugins: [uni()],
    define: {
      __IS_PRODUCTION__: JSON.stringify(isProd),
      __API_BASE_URL__: JSON.stringify(
        isProd
          ? (env.VUE_APP_PROD_API_BASE_URL || 'http://8.129.25.16:8000')
          : (env.VUE_APP_DEV_API_BASE_URL || 'http://localhost:8000')
      ),
      __FRONTEND_URL__: JSON.stringify(
        isProd
          ? (env.VUE_APP_PROD_FRONTEND_URL || 'http://8.129.25.16')
          : (env.VUE_APP_DEV_FRONTEND_URL || 'http://localhost:5173')
      ),
      __DEBUG__: JSON.stringify((env.VUE_APP_DEBUG || 'false') === 'true')
    },
    resolve: {
      alias: { '@': path.resolve(__dirname, './src') }
    },
    server: {
      port: 5173,
      host: '0.0.0.0', // ← 关键：允许外部访问
      proxy: {
        '/api': {
          target: isProd ? 'http://8.129.25.16:8000' : 'http://localhost:8000',
          changeOrigin: true,
        }
      }
    }
  }
})