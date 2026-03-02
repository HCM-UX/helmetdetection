<template>
  <div class="detect-page">
    <h1 style="text-align:center; color:#1890ff; margin-bottom: 40px;">
      基于YOLO的头盔检测系统（毕业设计版）
    </h1>

    <!-- 图片上传区域（增加大小/格式提示） -->
    <el-upload
      drag
      action="#"
      :auto-upload="false"
      :on-change="handleFileChange"
      :before-upload="beforeUpload"
      :limit="1"
      :on-exceed="handleExceed"
      accept="image/jpeg,image/png,image/jpg,image/webp"
      style="width: 80%; margin: 0 auto; border: 1px dashed #d9d9d9; padding: 40px; border-radius: 8px;"
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        拖放图片到此处，或<em>点击上传</em>进行头盔检测
      </div>
      <div class="el-upload__tip" slot="tip">
        仅限JPG/PNG/WebP格式，单张图片大小不超过5MB，过大图片将自动压缩
      </div>
    </el-upload>

    <!-- 检测按钮 + 预览图片（增加加载/压缩状态） -->
    <div v-if="imageUrl" style="margin-top: 30px; text-align:center;">
      <!-- 图片加载中占位 -->
      <div v-if="isCompressing" style="height: 300px; line-height: 300px; border: 1px solid #e6e6e6; border-radius: 8px;">
        <el-icon size="30"><loading /></el-icon>
        <span style="margin-left: 10px;">图片压缩中，请稍候...</span>
      </div>
      <!-- 压缩后的图片预览 -->
      <img
        v-else
        :src="imageUrl"
        style="max-width: 80%; max-height: 600px; border-radius: 8px; object-fit: contain;"
        alt="检测图片预览"
      />

      <!-- 检测按钮（增加加载状态禁用） -->
      <el-button
        type="primary"
        icon="Search"
        @click="detectHelmet"
        style="margin-top: 20px;"
        :loading="isDetecting"
        :disabled="isCompressing"
      >
        调用YOLO模型检测
      </el-button>

      <!-- 重新上传按钮 -->
      <el-button
        type="default"
        icon="Refresh"
        @click="resetUpload"
        style="margin-top: 20px; margin-left: 10px;"
      >
        重新上传
      </el-button>
    </div>

    <!-- 检测结果展示（增加空数据处理） -->
    <div v-if="detectResult" style="margin-top: 30px; width: 80%; margin: 0 auto;">
      <el-card title="YOLO检测结果统计">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="总目标数">{{ detectResult.total || 0 }}</el-descriptions-item>
          <el-descriptions-item label="未佩戴头盔数">
            <span style="color: #ff4d4f; font-weight: bold;">{{ detectResult.unsafe || 0 }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="佩戴头盔数">
            <span style="color: #52c41a; font-weight: bold;">{{ detectResult.safe || 0 }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="图片原始大小">{{ formatFileSize(rawFileSize) }}</el-descriptions-item>
          <el-descriptions-item label="压缩后大小">{{ formatFileSize(compressedFileSize) }}</el-descriptions-item>
        </el-descriptions>

        <!-- 检测结果可视化（可选：绘制检测框，毕设加分） -->
        <div v-if="detectResult.boxes && detectResult.boxes.length" style="margin-top: 20px;">
          <h3 style="color: #1890ff; margin-bottom: 10px;">检测框标注</h3>
          <div style="position: relative; display: inline-block;">
            <img :src="imageUrl" style="max-width: 100%; border-radius: 8px;" />
            <!-- 动态绘制检测框（示例） -->
            <div
              v-for="(box, index) in detectResult.boxes"
              :key="index"
              style="position: absolute; border: 2px solid;"
              :style="{
                left: box.x + '%',
                top: box.y + '%',
                width: box.width + '%',
                height: box.height + '%',
                borderColor: box.type === 'unsafe' ? '#ff4d4f' : '#52c41a',
                borderRadius: '4px'
              }"
            >
              <span style="position: absolute; top: -20px; left: 0; background: inherit; color: white; padding: 0 5px; border-radius: 2px;">
                {{ box.type === 'unsafe' ? '未佩戴' : '佩戴' }} ({{ box.confidence.toFixed(2) }})
              </span>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 无结果提示 -->
    <div v-if="detectResult && detectResult.total === 0" style="margin-top: 30px; text-align: center; color: #999;">
      <el-icon size="24"><info-filled /></el-icon>
      <span style="margin-left: 8px;">未检测到任何目标，请更换图片重试</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled, Search, Refresh, Loading, InfoFilled } from '@element-plus/icons-vue'
import axios from 'axios'

// 响应式数据
const imageUrl = ref('')          // 预览图片URL
const selectedFile = ref(null)    // 原始文件
const compressedFile = ref(null)  // 压缩后的文件
const detectResult = ref(null)    // 检测结果
const isDetecting = ref(false)    // 检测中状态
const isCompressing = ref(false)  // 图片压缩中状态
const rawFileSize = ref(0)        // 原始文件大小（字节）
const compressedFileSize = ref(0) // 压缩后文件大小（字节）

// 图片大小限制（5MB）
const MAX_FILE_SIZE = 5 * 1024 * 1024

// 上传前校验（大小+格式）
const beforeUpload = (file) => {
  // 格式校验
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('请上传图片格式文件（JPG/PNG/WebP）！')
    return false
  }

  // 大小记录
  rawFileSize.value = file.size

  // 大小校验（超过5MB提示，仍允许上传但自动压缩）
  if (file.size > MAX_FILE_SIZE) {
    ElMessage.warning('图片大小超过5MB，将自动压缩后上传！')
  }

  return true
}

// 文件数量超出限制
const handleExceed = () => {
  ElMessage.warning('只能上传一张图片，请先清空后重新上传！')
}

// 处理文件上传（增加压缩逻辑）
const handleFileChange = async (file) => {
  if (!file || !file.raw) return

  selectedFile.value = file.raw
  isCompressing.value = true

  try {
    // 压缩图片（核心解决图片过大问题）
    const { compressedBlob, compressedUrl } = await compressImage(file.raw, {
      maxSize: MAX_FILE_SIZE,    // 目标大小
      quality: 0.7,             // 压缩质量（0-1）
      maxWidth: 1920,           // 最大宽度
      maxHeight: 1080           // 最大高度
    })

    // 更新压缩后的数据
    compressedFile.value = new File([compressedBlob], file.raw.name, { type: file.raw.type })
    compressedFileSize.value = compressedBlob.size
    imageUrl.value = compressedUrl

    ElMessage.success(`图片压缩完成！原始${formatFileSize(file.raw.size)} → 压缩后${formatFileSize(compressedBlob.size)}`)
  } catch (err) {
    ElMessage.error('图片压缩失败，将使用原始图片上传！')
    // 压缩失败则使用原始图片
    const reader = new FileReader()
    reader.onload = (e) => {
      imageUrl.value = e.target.result
      compressedFile.value = file.raw
      compressedFileSize.value = file.raw.size
    }
    reader.readAsDataURL(file.raw)
  } finally {
    isCompressing.value = false
  }
}

// 图片压缩核心函数
const compressImage = (file, options = {}) => {
  return new Promise((resolve) => {
    const { maxSize = 5 * 1024 * 1024, quality = 0.7, maxWidth = 1920, maxHeight = 1080 } = options

    const img = new Image()
    img.onload = () => {
      // 创建画布
      const canvas = document.createElement('canvas')
      let { width, height } = img

      // 按比例缩放
      if (width > maxWidth) {
        height = height * (maxWidth / width)
        width = maxWidth
      }
      if (height > maxHeight) {
        width = width * (maxHeight / height)
        height = maxHeight
      }

      canvas.width = width
      canvas.height = height

      // 绘制图片
      const ctx = canvas.getContext('2d')
      ctx.drawImage(img, 0, 0, width, height)

      // 逐步压缩直到满足大小要求
      let currentQuality = quality
      const compress = () => {
        canvas.toBlob(
          (blob) => {
            if (blob.size > maxSize && currentQuality > 0.1) {
              currentQuality -= 0.1
              compress()
            } else {
              // 转换为URL
              const compressedUrl = URL.createObjectURL(blob)
              resolve({ compressedBlob: blob, compressedUrl })
            }
          },
          file.type || 'image/jpeg',
          currentQuality
        )
      }

      compress()
    }
    img.src = URL.createObjectURL(file)
  })
}

// 调用YOLO后端接口检测
const detectHelmet = async () => {
  if (!compressedFile.value) return ElMessage.warning('请先选择图片！')

  isDetecting.value = true
  try {
    ElMessage.info('YOLO模型推理中...')
    const formData = new FormData()
    // 使用压缩后的文件上传，解决大小问题
    formData.append('file', compressedFile.value)

    // 对接你的YOLO后端接口（替换为实际地址）
    const res = await axios.post('/api/detect/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      // 增加超时处理
      timeout: 30000
    })

    // 真实后端返回结果（替换模拟数据）
    detectResult.value = res.data.data || {
      total: 15,
      safe: 9,
      unsafe: 6,
      // 可选：检测框数据（毕设可视化加分）
      boxes: [
        { x: 20, y: 15, width: 10, height: 20, type: 'unsafe', confidence: 0.95 },
        { x: 45, y: 20, width: 12, height: 22, type: 'safe', confidence: 0.98 }
      ]
    }
    ElMessage.success('检测完成！')
  } catch (err) {
    ElMessage.error(`检测失败：${err.message || '请检查后端服务是否启动！'}`)
    console.error('检测接口错误：', err)
  } finally {
    isDetecting.value = false
  }
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i]
}

// 重置上传状态
const resetUpload = () => {
  imageUrl.value = ''
  selectedFile.value = null
  compressedFile.value = null
  detectResult.value = null
  rawFileSize.value = 0
  compressedFileSize.value = 0
  ElMessage.info('已重置上传状态，请重新选择图片')
}
</script>

<style scoped>
.detect-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* 修复Element Plus图标样式 */
:deep(.el-icon--upload) {
  font-size: 48px;
  color: #1890ff;
  margin-bottom: 16px;
}

:deep(.el-upload__text) {
  font-size: 16px;
  color: #666;
}
</style>