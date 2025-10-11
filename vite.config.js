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
      // 关键：将整个 process.env 模拟为一个静态对象（让浏览器中 process.env 可用）
      'process.env': {
        VUE_APP_ENVIRONMENT: JSON.stringify(appEnv),
        VUE_APP_DEV_API_BASE_URL: JSON.stringify(env.VUE_APP_DEV_API_BASE_URL || 'http://localhost:8000'),
        VUE_APP_PROD_API_BASE_URL: JSON.stringify(env.VUE_APP_PROD_API_BASE_URL || 'http://8.129.25.16:8000'),
        VUE_APP_DEBUG: JSON.stringify(env.VUE_APP_DEBUG || 'false'),
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