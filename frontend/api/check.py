"""
合并的文件上传+分析 API - Vercel Serverless Function
"""
from http.server import BaseHTTPRequestHandler
import json
import uuid
import sys
from pathlib import Path
from datetime import datetime
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from checker import DXFParser, ComplianceChecker
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from checker import DXFParser, ComplianceChecker


class handler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            max_size = 10 * 1024 * 1024
            if content_length > max_size:
                return self._json(413, {"error": "文件过大，最大支持 10MB"})
            
            body = self.rfile.read(content_length)
            content_type = self.headers.get('Content-Type', '')
            
            if 'boundary=' not in content_type:
                return self._json(400, {"error": "无效的 Content-Type"})
            
            # 解析文件
            boundary = content_type.split('boundary=')[1].encode()
            parts = body.split(b'--' + boundary)
            
            filename = None
            file_data = None
            for part in parts:
                if b'filename=' in part:
                    fname_start = part.find(b'filename="') + 10
                    fname_end = part.find(b'"', fname_start)
                    filename = part[fname_start:fname_end].decode('utf-8', errors='ignore')
                    data_start = part.find(b'\r\n\r\n') + 4
                    file_data = part[data_start:-2]
                    break
            
            if not filename or not file_data:
                return self._json(400, {"error": "未找到有效的文件数据"})
            
            file_ext = Path(filename).suffix.lower()
            if file_ext not in ['.dxf', '.dwg']:
                return self._json(400, {"error": f"不支持的文件格式: {file_ext}"})
            
            # 写入临时文件
            with tempfile.NamedTemporaryFile(mode='wb', suffix=file_ext, delete=False) as tmp:
                tmp.write(file_data)
                temp_path = tmp.name
            
            try:
                # 立即解析和分析
                file_id = str(uuid.uuid4())
                analysis_id = str(uuid.uuid4())
                
                parser = DXFParser()
                dxf_data = parser.parse(temp_path)
                
                checker = ComplianceChecker(standard='GB/T 14665-2012')
                report = checker.check(dxf_data, analysis_id, file_id)
                
                # 清理临时文件
                Path(temp_path).unlink(missing_ok=True)
                
                return self._json(200, {
                    "analysis_id": analysis_id,
                    "file_id": file_id,
                    "filename": filename,
                    "size": len(file_data),
                    "status": "completed",
                    "message": "分析完成",
                    "report": report.model_dump(mode='json')
                })
                
            except Exception as e:
                Path(temp_path).unlink(missing_ok=True)
                raise
                
        except ValueError as e:
            return self._json(400, {"error": f"DXF 解析错误: {str(e)}"})
        except Exception as e:
            return self._json(500, {"error": f"处理失败: {str(e)}"})
    
    def _json(self, status, data):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
