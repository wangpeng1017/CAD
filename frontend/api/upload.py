"""
文件上传 API - Vercel Serverless Function (Next.js project root)
"""
from http.server import BaseHTTPRequestHandler
import json
import uuid
from pathlib import Path
from datetime import datetime


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

            file_id = str(uuid.uuid4())
            temp_dir = Path('/tmp/cad_uploads')
            temp_dir.mkdir(parents=True, exist_ok=True)

            content_type = self.headers.get('Content-Type', '')
            if 'boundary=' not in content_type:
                return self._json(400, {"error": "无效的 Content-Type"})
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

            file_path = temp_dir / f"{file_id}{file_ext}"
            with open(file_path, 'wb') as f:
                f.write(file_data)

            return self._json(200, {
                "file_id": file_id,
                "filename": filename,
                "size": len(file_data),
                "upload_time": datetime.now().isoformat(),
                "message": "文件上传成功"
            })
        except Exception as e:
            return self._json(500, {"error": f"上传失败: {str(e)}"})

    def _json(self, status, data):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
