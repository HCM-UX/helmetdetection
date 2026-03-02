from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .api.detect import router as detect_router

# 创建FastAPI应用实例
app = FastAPI(
    title="基于YOLO的头盔检测系统API",
    version="1.0",
    description="支持Helmet/No Helmet/Worker三类目标检测的后端接口"
)

# 配置CORS跨域（解决前端跨域请求问题）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有域名，生产环境建议指定前端域名（如http://127.0.0.1:8080）
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # 允许的请求方法
    allow_headers=["*"],  # 允许的请求头
)

# 注册检测接口路由（前缀：/detect）
app.include_router(
    detect_router,
    prefix="/detect",
    tags=["头盔检测接口"]
)

# 根路径健康检查接口（用于验证服务是否启动）
@app.get("/", tags=["健康检查"])
async def root():
    return {
        "status": "success",
        "message": "头盔检测系统后端服务运行正常",
        "api_docs": "http://127.0.0.1:5000/docs"  # 自动生成的API文档地址
    }