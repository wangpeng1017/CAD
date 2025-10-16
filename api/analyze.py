"""
文件分析 API - Vercel Serverless Function
"""
from http.server import BaseHTTPRequestHandler
import json
import uuid
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from checker import DXFParser, ComplianceChecker


class handler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        """处理分析请求"""
        try:
            # 读取请求体
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body.decode())
            
            file_id = data.get('file_id')
            standard = data.get('standard', 'GB/T 14665-2012')
            
            if not file_id:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": "缺少 file_id 参数"
                }).encode())
                return
            
            # 查找上传的文件
            temp_dir = Path('/tmp/cad_uploads')
            file_path = None
            for ext in ['.dxf', '.dwg']:
                path = temp_dir / f"{file_id}{ext}"
                if path.exists():
                    file_path = path
                    break
            
            if not file_path:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": "文件不存在"
                }).encode())
                return
            
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
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "analysis_id": analysis_id,
                "file_id": file_id,
                "status": "completed",
                "message": "分析完成",
                "report": report.model_dump(mode='json')
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except ValueError as e:
            # DXF 解析错误
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": str(e)
            }, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": f"分析失败: {str(e)}"
            }, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        """处理 CORS 预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
