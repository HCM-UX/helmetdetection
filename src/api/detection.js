import axios from 'axios'

// 创建axios实例
const request = axios.create({
  baseURL: '/api',  // 匹配Vite代理配置，转发到后端5000端口
  timeout: 10000
})

// 图片头盔检测接口
export const detectImage = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/detect/image',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}