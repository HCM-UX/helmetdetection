import { createApp } from 'vue'
import App from './App.vue'  // 修正 App.vue 的路径
import router from './src/router/index.js'  // 修正 router 的路径

const app = createApp(App)
app.use(router)
app.mount('#app')