// C:\helmet_detection\router\index.js
import { createRouter, createWebHistory } from 'vue-router'
// 导入检测页面（下一步创建）
import ImageDetect from '../views/ImageDetect.vue'

// 路由规则：根路径指向检测页面
const routes = [
  {
    path: '/',
    name: 'ImageDetect',
    component: ImageDetect
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 导出路由（供main.js导入）
export default router