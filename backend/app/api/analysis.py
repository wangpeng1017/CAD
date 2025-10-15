"""
分析 API 路由
"""
from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from datetime import datetime
from pathlib import Path
import uuid

from app.models import AnalysisRequest, AnalysisResponse, AnalysisStatus
from app.services.dxf_parser import DXFParserService
from app.services.compliance_checker import ComplianceCheckerService
from app.services.dwg_converter import dwg_converter
from app.config import settings

router = APIRouter()

# 内存存储（Phase 1 简化实现，Phase 2 应使用数据库）
analysis_results = {}


@router.post("/analyze", response_model=AnalysisResponse)
async def start_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    启动 CAD 文件分析
    
    - **file_id**: 已上传文件的ID
    - **standard**: 检查标准（默认 GB/T 14665-2012）
    """
    # 验证文件是否存在
    file_path = None
    for ext in settings.allowed_extensions:
        path = settings.upload_dir / f"{request.file_id}.{ext}"
        if path.exists():
            file_path = path
            break
    
    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 生成分析任务ID
    analysis_id = str(uuid.uuid4())
    
    # 初始化分析状态
    analysis_results[analysis_id] = {
        "status": AnalysisStatus.PENDING,
        "file_id": request.file_id,
        "file_path": str(file_path),
        "standard": request.standard,
        "started_at": datetime.now(),
        "report": None,
        "error": None
    }
    
    # 在后台执行分析
    background_tasks.add_task(
        perform_analysis,
        analysis_id,
        str(file_path),
        request.standard
    )
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        file_id=request.file_id,
        status=AnalysisStatus.PENDING,
        message="分析任务已创建，正在处理中"
    )


@router.get("/analyze/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis_status(analysis_id: str):
    """查询分析任务状态"""
    if analysis_id not in analysis_results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分析任务不存在"
        )
    
    result = analysis_results[analysis_id]
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        file_id=result["file_id"],
        status=result["status"],
        message=_get_status_message(result["status"], result.get("error"))
    )


async def perform_analysis(
    analysis_id: str,
    file_path: str,
    standard: str
):
    """执行实际的分析任务（后台任务）"""
    converted_file = None
    try:
        # 更新状态为处理中
        analysis_results[analysis_id]["status"] = AnalysisStatus.PROCESSING
        
        # Step 1: 如果是 DWG 文件，先转换为 DXF
        if file_path.lower().endswith('.dwg'):
            try:
                converted_file = await dwg_converter.convert_to_dxf(file_path)
                file_path = converted_file
            except Exception as e:
                # 提供更友好的错误信息
                error_msg = (
                    f"DWG 文件转换失败。\n\n"
                    f"当前系统不支持直接分析 DWG 格式文件。\n\n"
                    f"解决方案：\n"
                    f"1. 在 AutoCAD 或其他 CAD 软件中打开文件\n"
                    f"2. 使用 '另存为' 功能保存为 DXF 格式\n"
                    f"3. 重新上传 DXF 文件进行分析\n\n"
                    f"技术详情: {str(e)}"
                )
                raise ValueError(error_msg)
        
        # Step 2: 解析 DXF 文件
        parser = DXFParserService()
        dxf_data = await parser.parse(file_path)
        
        # Step 3: 执行合规检查
        checker = ComplianceCheckerService(standard)
        report = await checker.check(dxf_data, analysis_id, file_path)
        
        # 保存结果
        analysis_results[analysis_id]["status"] = AnalysisStatus.COMPLETED
        analysis_results[analysis_id]["report"] = report
        analysis_results[analysis_id]["completed_at"] = datetime.now()
        
    except Exception as e:
        # 记录错误
        analysis_results[analysis_id]["status"] = AnalysisStatus.FAILED
        analysis_results[analysis_id]["error"] = str(e)
        analysis_results[analysis_id]["completed_at"] = datetime.now()
    
    finally:
        # 清理转换后的临时 DXF 文件
        if converted_file and Path(converted_file).exists():
            try:
                Path(converted_file).unlink()
            except:
                pass


def _get_status_message(status: AnalysisStatus, error: str = None) -> str:
    """获取状态消息"""
    messages = {
        AnalysisStatus.PENDING: "分析任务排队中",
        AnalysisStatus.PROCESSING: "正在分析文件...",
        AnalysisStatus.COMPLETED: "分析完成",
        AnalysisStatus.FAILED: f"分析失败: {error}" if error else "分析失败"
    }
    return messages.get(status, "未知状态")


# 导出结果存储供 report.py 使用
def get_analysis_result(analysis_id: str):
    """获取分析结果（内部使用）"""
    return analysis_results.get(analysis_id)
