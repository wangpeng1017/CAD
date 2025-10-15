"""
文件上传 API 路由
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from datetime import datetime
from pathlib import Path
import uuid
import aiofiles

from app.models import FileUploadResponse
from app.config import settings

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    上传 DXF 文件
    
    - **file**: DXF 文件 (最大 10MB)
    """
    # 验证文件扩展名
    file_ext = Path(file.filename).suffix.lower().lstrip(".")
    if file_ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件格式。仅支持: {', '.join(settings.allowed_extensions)}"
        )
    
    # 生成唯一文件ID
    file_id = str(uuid.uuid4())
    safe_filename = f"{file_id}.{file_ext}"
    file_path = settings.upload_dir / safe_filename
    
    # 读取文件内容并验证大小
    content = await file.read()
    file_size = len(content)
    
    if file_size > settings.max_upload_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"文件过大。最大允许大小: {settings.max_upload_size / (1024*1024):.1f}MB"
        )
    
    # 保存文件
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件保存失败: {str(e)}"
        )
    
    return FileUploadResponse(
        file_id=file_id,
        filename=file.filename,
        size=file_size,
        upload_time=datetime.now()
    )


@router.delete("/upload/{file_id}")
async def delete_file(file_id: str):
    """删除上传的文件"""
    # 查找文件
    file_path = None
    for ext in settings.allowed_extensions:
        path = settings.upload_dir / f"{file_id}.{ext}"
        if path.exists():
            file_path = path
            break
    
    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 删除文件
    try:
        file_path.unlink()
        return {"message": "文件删除成功", "file_id": file_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件删除失败: {str(e)}"
        )
