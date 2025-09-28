import { defineConfig } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    uni(),
  ],
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
        target: process.env.VUE_APP_ENVIRONMENT === 'production'
          ? (process.env.VUE_APP_PROD_API_BASE_URL || 'https://api.your-domain.com')
          : (process.env.VUE_APP_DEV_API_BASE_URL || 'http://localhost:8000'),
        changeOrigin: true,
      }
    }
  }
})
