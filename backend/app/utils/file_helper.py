from PIL import Image
import io
from fastapi import UploadFile

def read_upload_file(file: UploadFile) -> Image.Image:
    """
    读取FastAPI上传的图片文件，转换为PIL Image对象（RGB格式）
    解决图片格式异常、读取失败等问题，确保YOLO模型可正常处理
    """
    try:
        # 读取文件二进制内容
        contents = file.file.read()
        # 转换为BytesIO流，避免文件路径问题
        image_stream = io.BytesIO(contents)
        # 打开图片并转换为RGB格式（YOLO要求RGB通道）
        image = Image.open(image_stream).convert("RGB")
        return image
    except Exception as e:
        raise ValueError(f"图片读取失败：{str(e)}")
    finally:
        # 关闭文件流，避免资源泄露
        file.file.close()