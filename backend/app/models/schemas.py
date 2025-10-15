"""
Pydantic 数据模型定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ViolationType(str, Enum):
    """违规类型枚举"""
    LAYER = "图层错误"
    LINEWEIGHT = "线宽错误"
    COLOR = "颜色错误"
    FONT = "字体错误"
    DIMENSION = "尺寸标注错误"
    TEXT = "文字错误"
    GEOMETRY = "几何错误"


class SeverityLevel(str, Enum):
    """严重程度"""
    CRITICAL = "严重"
    WARNING = "警告"
    INFO = "提示"


class Violation(BaseModel):
    """违规项"""
    id: str = Field(..., description="违规项唯一标识")
    type: ViolationType = Field(..., description="违规类型")
    severity: SeverityLevel = Field(..., description="严重程度")
    rule: str = Field(..., description="违反的规则")
    description: str = Field(..., description="详细描述")
    entity_handle: Optional[str] = Field(None, description="实体句柄")
    layer: Optional[str] = Field(None, description="所在图层")
    location: Optional[dict] = Field(None, description="位置信息")
    suggestion: Optional[str] = Field(None, description="修复建议")


class AnalysisStatus(str, Enum):
    """分析状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FileUploadResponse(BaseModel):
    """文件上传响应"""
    file_id: str = Field(..., description="文件唯一标识")
    filename: str = Field(..., description="文件名")
    size: int = Field(..., description="文件大小(字节)")
    upload_time: datetime = Field(..., description="上传时间")
    message: str = Field(default="文件上传成功")


class AnalysisRequest(BaseModel):
    """分析请求"""
    file_id: str = Field(..., description="文件标识")
    standard: str = Field(default="GB/T 14665-2012", description="检查标准")


class AnalysisResponse(BaseModel):
    """分析响应"""
    analysis_id: str = Field(..., description="分析任务标识")
    file_id: str = Field(..., description="文件标识")
    status: AnalysisStatus = Field(..., description="分析状态")
    message: str = Field(..., description="状态消息")


class ComplianceReport(BaseModel):
    """合规报告"""
    analysis_id: str = Field(..., description="分析任务标识")
    file_id: str = Field(..., description="文件标识")
    filename: str = Field(..., description="文件名")
    standard: str = Field(..., description="检查标准")
    analysis_time: datetime = Field(..., description="分析时间")
    
    # 统计信息
    total_violations: int = Field(..., description="违规总数")
    critical_count: int = Field(0, description="严重错误数量")
    warning_count: int = Field(0, description="警告数量")
    info_count: int = Field(0, description="提示数量")
    
    # 详细违规列表
    violations: List[Violation] = Field(default_factory=list, description="违规详情")
    
    # 整体评估
    is_compliant: bool = Field(..., description="是否合规")
    compliance_score: float = Field(..., ge=0, le=100, description="合规得分")


class ReportExportFormat(str, Enum):
    """报告导出格式"""
    JSON = "json"
    PDF = "pdf"
    HTML = "html"
