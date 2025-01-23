import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
<<<<<<< HEAD

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
=======
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  root: './app',
  base: '/',
  build: {
    outDir: 'static/dist',
    assetsDir: 'assets',
    manifest: true,
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'app/static/js/main.js')
      },
      output: {
        format: 'es',
        entryFileNames: 'js/[name].js',
        chunkFileNames: 'js/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash][extname]'
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './app/static/js'),
      'vue': 'vue'
    },
    extensions: ['.mjs', '.js', '.ts', '.jsx', '.tsx', '.json', '.vue']
  },
  server: {
    host: '127.0.0.1',
    port: 8080,
    strictPort: true,
    fs: {
      strict: false,
      allow: ['..']
    },
    cors: true,
    proxy: {
      '^/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true
      }
    }
  },
  optimizeDeps: {
    include: ['vue', 'vue-router', 'pinia', 'axios'],
    exclude: []
  }
}) 
>>>>>>> 64562f7db6a86c60d155d116e245e7450ef2d2a7
