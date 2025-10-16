"""
文件分析 API - Vercel Serverless Function
"""
import json
import uuid
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from checker import DXFParser, ComplianceChecker


def handler(request):
    """处理分析请求"""
    
    # CORS 预检请求
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': ''
        }
    
    if request.method != 'POST':
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        # 读取请求体
        body = request.body
        if isinstance(body, bytes):
            body = body.decode('utf-8')
        data = json.loads(body)
        
        file_id = data.get('file_id')
        standard = data.get('standard', 'GB/T 14665-2012')
        
        if not file_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': '缺少 file_id 参数'}, ensure_ascii=False)
            }
        
        # 查找上传的文件
        temp_dir = Path('/tmp/cad_uploads')
        file_path = None
        for ext in ['.dxf', '.dwg']:
            path = temp_dir / f"{file_id}{ext}"
            if path.exists():
                file_path = path
                break
        
        if not file_path:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': '文件不存在'}, ensure_ascii=False)
            }
        
        # 生成分析ID
        analysis_id = str(uuid.uuid4())
        
        # 解析 DXF 文件
        parser = DXFParser()
        dxf_data = parser.parse(str(file_path))
        
        # 执行合规性检查
        checker = ComplianceChecker(standard=standard)
        report = checker.check(dxf_data, analysis_id, file_id)
        
        # 将报告保存到临时文件
        report_path = Path('/tmp/cad_reports')
        report_path.mkdir(parents=True, exist_ok=True)
        
        report_file = report_path / f"{analysis_id}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report.model_dump(mode='json'), f, ensure_ascii=False, indent=2)
        
        # 返回响应
        response = {
            'analysis_id': analysis_id,
            'file_id': file_id,
            'status': 'completed',
            'message': '分析完成',
            'report': report.model_dump(mode='json')
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response, ensure_ascii=False)
        }
        
    except ValueError as e:
        # DXF 解析错误
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)}, ensure_ascii=False)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': f'分析失败: {str(e)}'}, ensure_ascii=False)
        }
