from fastapi import APIRouter, UploadFile, File, HTTPException
from ..models.yolo_model import detect_image
from ..utils.file_helper import read_upload_file
from pydantic import BaseModel
from typing import List, Dict

router = APIRouter()

# 定义响应数据模型（适配前端）
class APIResponse(BaseModel):
    status: str
    data: Dict
    error: str = None

@router.post("/image", response_model=APIResponse)
async def detect_image_endpoint(file: UploadFile = File(...)):
    try:
        # 1. 读取上传的图片文件
        image = read_upload_file(file)
        # 2. 调用YOLO模型检测
        detect_data = detect_image(image)
        # 3. 返回适配前端的响应
        return APIResponse(
            status="success",
            data=detect_data
        )
    except Exception as e:
        # 异常捕获+友好提示
        error_msg = f"检测失败：{str(e)}"
        print(f"❌ 检测接口异常：{error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)