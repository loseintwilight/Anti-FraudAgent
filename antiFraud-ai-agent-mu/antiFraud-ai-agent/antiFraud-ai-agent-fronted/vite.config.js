import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import fs from 'fs'
import path from 'path'
import os from 'os'

/**
 * 复制 load.jpg 作为 favicon 和反诈卫士头像的 Vite 插件
 * 每次 dev/build 时自动执行
 */
function copyLoadImagePlugin() {
  const SOURCE_PATHS = [
    'd:\\Anti-FraudAgent\\load.jpg',
    'd:/Anti-FraudAgent/load.jpg',
    '/d/Anti-FraudAgent/load.jpg',
  ]

  function findSource() {
    for (const p of SOURCE_PATHS) {
      if (fs.existsSync(p)) return p
    }
    const cwd = process.cwd()
    const alternatives = [
      path.join(cwd, 'load.jpg'),
      path.join(cwd, '..', '..', '..', '..', 'load.jpg'),
      path.join(os.homedir(), 'load.jpg'),
    ]
    for (const alt of alternatives) {
      try {
        if (fs.existsSync(alt)) return alt
      } catch (e) { /* ignore */ }
    }
    return null
  }

  return {
    name: 'copy-load-image',
    buildStart() {
      const source = findSource()
      if (!source) {
        console.warn('[copy-load-image] 未找到 d:\\Anti-FraudAgent\\load.jpg，跳过 favicon 复制')
        return
      }

      const targets = [
        { file: 'public/favicon.jpg', desc: '浏览器标签图标(web端)' },
        { file: 'src/assets/load.jpg', desc: '反诈卫士头像' },
        // 同时复制到 RuoYi 管理后台
        { file: path.resolve(__dirname, '..', '..', '..', '..', 'RuoYi-Vue-master', 'ruoyi-ui', 'public', 'favicon.jpg'), desc: '浏览器标签图标(管理后台)' },
      ]

      for (const { file, desc } of targets) {
        const dest = path.resolve(__dirname, file)
        const destDir = path.dirname(dest)
        if (!fs.existsSync(destDir)) {
          fs.mkdirSync(destDir, { recursive: true })
        }
        try {
          fs.copyFileSync(source, dest)
          console.log(`[copy-load-image] OK: ${desc} (${file})`)
        } catch (e) {
          console.error(`[copy-load-image] FAILED: ${file} -`, e.message)
        }
      }
    },
  }
}

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [copyLoadImagePlugin(), vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8123',
        changeOrigin: true,
      },
      '/admin-api': {
        target: 'http://localhost:8081',
        changeOrigin: true,
      },
    },
  },
})
