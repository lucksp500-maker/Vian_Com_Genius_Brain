import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      input: {
        popup: resolve(__dirname, 'popup.html'),
        // WO-007: Chrome Extension service worker + content script 추가
        // manifest.json이 background.js와 content.js를 요구함
        background: resolve(__dirname, 'src/background/browserCommandRouter.ts'),
        content: resolve(__dirname, 'src/content/domContentExtractor.ts'),
      },
      output: {
        // Chrome Extension: ES module 형식으로 각 진입점을 개별 파일로 출력
        entryFileNames: '[name].js',
        chunkFileNames: 'chunks/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash][extname]',
      },
    },
    outDir: 'dist',
    emptyOutDir: true,
  },
})
