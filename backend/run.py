import uvicorn
from app import app
from app.config import settings

# 启动日志配置
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info(f"🚀 启动头盔检测后端服务...")
    logger.info(f"📌 模型路径：{settings.MODEL_PATH}")
    logger.info(f"🌐 服务地址：http://{settings.HOST}:{settings.PORT}")
    logger.info(f"📖 API文档：http://{settings.HOST}:{settings.PORT}/docs")

    # 启动UVicorn服务
    uvicorn.run(
        "app:app",  # 应用入口（模块名:实例名）
        host=settings.HOST,  # 监听地址（0.0.0.0允许外网访问）
        port=settings.PORT,  # 端口号
        reload=settings.RELOAD,  # 开发模式热重载（生产环境建议关闭）
        log_level="info"  # 日志级别
    )