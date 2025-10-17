"""
报告 API 路由
"""
from fastapi import APIRouter, HTTPException, status, Response
from fastapi.responses import JSONResponse
import json

from app.models import ComplianceReport, ReportExportFormat, AnalysisStatus
from app.api.analysis import get_analysis_result

router = APIRouter()


@router.get("/report/{analysis_id}", response_model=ComplianceReport)
async def get_report(analysis_id: str):
    """
    获取分析报告
    
    - **analysis_id**: 分析任务ID
    """
    result = get_analysis_result(analysis_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分析任务不存在"
        )
    
    if result["status"] == AnalysisStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="分析任务尚未开始"
        )
    
    if result["status"] == AnalysisStatus.PROCESSING:
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="分析正在进行中，请稍后再试"
        )
    
    if result["status"] == AnalysisStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分析失败: {result.get('error', '未知错误')}"
        )
    
    # 返回报告
    report = result.get("report")
    if not report:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="报告生成失败"
        )
    
    return report


@router.get("/report/{analysis_id}/export")
async def export_report(
    analysis_id: str,
    format: ReportExportFormat = ReportExportFormat.JSON
):
    """
    导出报告
    
    - **analysis_id**: 分析任务ID
    - **format**: 导出格式 (json/pdf/html)
    """
    # 获取报告
    result = get_analysis_result(analysis_id)
    
    if not result or result["status"] != AnalysisStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="报告尚未完成或不存在"
        )
    
    report = result.get("report")
    
    if format == ReportExportFormat.JSON:
        # JSON 导出
        content = json.dumps(
            report.model_dump(),
            ensure_ascii=False,
            indent=2,
            default=str
        )
        return Response(
            content=content,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=report_{analysis_id}.json"
            }
        )
    
    elif format == ReportExportFormat.HTML:
        # HTML 导出（简化版）
        html_content = _generate_html_report(report)
        return Response(
            content=html_content,
            media_type="text/html",
            headers={
                "Content-Disposition": f"attachment; filename=report_{analysis_id}.html"
            }
        )
    
    elif format == ReportExportFormat.PDF:
        # PDF 导出（Phase 2 实现）
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="PDF 导出功能将在 Phase 2 实现"
        )


def _generate_html_report(report: ComplianceReport) -> str:
    """生成 HTML 报告（简化版）"""
    violations_html = ""
    for v in report.violations:
        details_html = ""
        if getattr(v, 'entity_details', None):
            items = ''.join([f"<li><strong>{k}:</strong> {v_}</li>" for k, v_ in v.entity_details.items()])
            details_html = f"<ul style=\"margin:8px 0 0 16px;color:#555;\">{items}</ul>"
        violations_html += f"""
        <tr>
            <td>{v.type.value}</td>
            <td>{v.severity.value}</td>
            <td>{v.rule}</td>
            <td>
                <div>{v.description}</div>
                {details_html}
            </td>
        </tr>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>CAD 合规检查报告</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #333; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #4CAF50; color: white; }}
            .summary {{ background-color: #f9f9f9; padding: 20px; margin: 20px 0; }}
            .compliant {{ color: green; }}
            .non-compliant {{ color: red; }}
        </style>
    </head>
    <body>
        <h1>CAD 合规检查报告</h1>
        <div class="summary">
            <p><strong>文件名:</strong> {report.filename}</p>
            <p><strong>检查标准:</strong> {report.standard}</p>
            <p><strong>分析时间:</strong> {report.analysis_time}</p>
            <p><strong>合规状态:</strong> 
                <span class="{'compliant' if report.is_compliant else 'non-compliant'}">
                    {'合规' if report.is_compliant else '不合规'}
                </span>
            </p>
            <p><strong>合规得分:</strong> {report.compliance_score:.1f}/100</p>
            <p><strong>违规总数:</strong> {report.total_violations} 
                (严重: {report.critical_count}, 警告: {report.warning_count}, 提示: {report.info_count})
            </p>
        </div>
        
        <h2>违规详情</h2>
        <table>
            <thead>
                <tr>
                    <th>类型</th>
                    <th>严重程度</th>
                    <th>规则</th>
                    <th>描述</th>
                </tr>
            </thead>
            <tbody>
                {violations_html}
            </tbody>
        </table>
    </body>
    </html>
    """
    return html
