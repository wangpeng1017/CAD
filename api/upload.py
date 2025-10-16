"""
文件上传 API - Vercel Serverless Function
"""
from http.server import BaseHTTPRequestHandler
import json
import uuid
import os
import tempfile
from pathlib import Path
from datetime import datetime


class handler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        """处理文件上传"""
        try:
            # 读取请求体
            content_length = int(self.headers['Content-Length'])
            
            # 检查文件大小（10MB 限制）
            max_size = 10 * 1024 * 1024
            if content_length > max_size:
                self.send_response(413)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": "文件过大，最大支持 10MB"
                }).encode())
                return
            
            # 读取文件数据
            body = self.rfile.read(content_length)
            
            # 生成唯一文件ID
            file_id = str(uuid.uuid4())
            
            # 使用 /tmp 目录（Vercel Serverless 可写目录）
            temp_dir = Path('/tmp/cad_uploads')
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # 解析 multipart/form-data
            boundary = self.headers['Content-Type'].split('boundary=')[1].encode()
            parts = body.split(b'--' + boundary)
            
            filename = None
            file_data = None
            
            for part in parts:
                if b'filename=' in part:
                    # 提取文件名
                    filename_start = part.find(b'filename="') + 10
                    filename_end = part.find(b'"', filename_start)
                    filename = part[filename_start:filename_end].decode()
                    
                    # 提取文件数据
                    data_start = part.find(b'\r\n\r\n') + 4
                    file_data = part[data_start:-2]  # 移除末尾的 \r\n
                    break
            
            if not filename or not file_data:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": "未找到有效的文件数据"
                }).encode())
                return
            
            # 验证文件扩展名
            file_ext = Path(filename).suffix.lower()
            if file_ext not in ['.dxf', '.dwg']:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": f"不支持的文件格式: {file_ext}"
                }).encode())
                return
            
            # 保存文件
            file_path = temp_dir / f"{file_id}{file_ext}"
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # 返回成功响应
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "file_id": file_id,
                "filename": filename,
                "size": len(file_data),
                "upload_time": datetime.now().isoformat(),
                "message": "文件上传成功"
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": f"上传失败: {str(e)}"
            }).encode())
    
    def do_OPTIONS(self):
        """处理 CORS 预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
