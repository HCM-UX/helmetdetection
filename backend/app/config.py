import os

class Settings:
    # 1. 配置你的模型绝对路径（关键！）
    MODEL_PATH = r"D:\pythonProject1\runs\detect\train\weights\best.pt"
    # 2. 服务配置
    HOST = "0.0.0.0"
    PORT = 5000
    RELOAD = True  # 开发模式热重载
    # 3. 模型类别映射（和你的yaml配置一致）
    CLASS_NAMES = {
        0: "Helmet",
        1: "No Helmet",
        2: "Worker"
    }
    # 4. 检测置信度阈值
    CONF_THRESHOLD = 0.5

settings = Settings()