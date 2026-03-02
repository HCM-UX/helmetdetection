from ultralytics import YOLO
from ..config import settings
import numpy as np
from PIL import Image
import io

# 单例加载模型（避免重复加载，提升性能）
_model = None


def get_yolo_model():
    global _model
    if _model is None:
        # 加载你本地的best.pt模型
        _model = YOLO(settings.MODEL_PATH)
        # 验证模型类别是否匹配
        print(f"✅ 模型加载成功！类别数：{len(_model.names)}，类别：{_model.names}")
    return _model


def detect_image(image: Image.Image):
    """
    输入PIL Image，返回适配前端的检测结果
    返回格式：{total, safe_count, unsafe_count, boxes, results}
    """
    model = get_yolo_model()
    # 执行YOLO推理（使用配置的置信度阈值）
    results = model(image, conf=settings.CONF_THRESHOLD)

    # 初始化统计数据
    total = 0  # 总检测目标数
    safe_count = 0  # 佩戴头盔数（Helmet）
    unsafe_count = 0  # 未佩戴头盔数（No Helmet）
    detections = []  # 原始检测结果
    boxes = []  # 前端可视化检测框（百分比格式）

    # 获取图片宽高（用于转换检测框为百分比）
    img_width, img_height = image.size

    # 解析YOLO检测结果
    for r in results:
        for box in r.boxes:
            # 基础信息解析
            cls_id = int(box.cls[0])  # 类别索引
            conf = round(float(box.conf[0]), 2)  # 置信度（保留2位小数）
            class_name = settings.CLASS_NAMES.get(cls_id, "Unknown")  # 类别名称
            xyxy = box.xyxy[0].tolist()  # 检测框坐标 [x1, y1, x2, y2]

            # 统计逻辑（适配你的三类标注）
            total += 1
            if class_name == "Helmet":
                safe_count += 1
                helmet_status = "佩戴头盔"
                box_type = "safe"
            elif class_name == "No Helmet":
                unsafe_count += 1
                helmet_status = "未佩戴头盔"
                box_type = "unsafe"
            else:  # Worker
                helmet_status = "工作人员"
                box_type = "worker"

            # 转换检测框为百分比（适配前端可视化）
            x1, y1, x2, y2 = xyxy
            x_percent = round((x1 / img_width) * 100, 2)
            y_percent = round((y1 / img_height) * 100, 2)
            width_percent = round(((x2 - x1) / img_width) * 100, 2)
            height_percent = round(((y2 - y1) / img_height) * 100, 2)

            # 构建前端可视化检测框数据
            boxes.append({
                "x": x_percent,
                "y": y_percent,
                "width": width_percent,
                "height": height_percent,
                "type": box_type,
                "confidence": conf
            })

            # 构建原始检测结果数据
            detections.append({
                "class": class_name,
                "confidence": conf,
                "bbox": [round(x, 2) for x in xyxy],  # 原始像素坐标
                "helmet_status": helmet_status
            })

    # 返回最终结果（适配前端格式）
    return {
        "total": total,
        "safe_count": safe_count,
        "unsafe_count": unsafe_count,
        "boxes": boxes,  # 前端绘制检测框用
        "results": detections  # 详细检测信息
    }