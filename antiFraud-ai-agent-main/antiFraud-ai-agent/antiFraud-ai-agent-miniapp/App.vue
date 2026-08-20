<script setup>
import { onLaunch } from '@dcloudio/uni-app'

onLaunch(() => {
  console.log('App Launch')
})
</script>

<style>
/* 全局样式 */
page {
  background-color: #f5f7fa;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  color: #333;
  box-sizing: border-box;
}

view,
scroll-view,
swiper,
movable-view,
cover-view {
  box-sizing: border-box;
}

::-webkit-scrollbar {
  display: none;
  width: 0;
  height: 0;
}
</style>