"""
文件上传 API - Vercel Serverless Function
"""
import json
import uuid
from pathlib import Path
from datetime import datetime
from urllib.parse import parse_qs


def handler(request):
    """处理文件上传请求"""
    
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
        if isinstance(body, str):
            body = body.encode()
        
        # 检查文件大小（10MB 限制）
        max_size = 10 * 1024 * 1024
        if len(body) > max_size:
            return {
                'statusCode': 413,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': '文件过大，最大支持 10MB'})
            }
        
        # 生成唯一文件ID
        file_id = str(uuid.uuid4())
        
        # 使用 /tmp 目录（Vercel Serverless 可写目录）
        temp_dir = Path('/tmp/cad_uploads')
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # 解析 multipart/form-data
        content_type = request.headers.get('content-type', '')
        if 'boundary=' not in content_type:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': '无效的 Content-Type'})
            }
        
        boundary = content_type.split('boundary=')[1].encode()
        parts = body.split(b'--' + boundary)
        
        filename = None
        file_data = None
        
        for part in parts:
            if b'filename=' in part:
                # 提取文件名
                filename_start = part.find(b'filename="') + 10
                filename_end = part.find(b'"', filename_start)
                filename = part[filename_start:filename_end].decode('utf-8', errors='ignore')
                
                # 提取文件数据
                data_start = part.find(b'\r\n\r\n') + 4
                file_data = part[data_start:-2]  # 移除末尾的 \r\n
                break
        
        if not filename or not file_data:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': '未找到有效的文件数据'})
            }
        
        # 验证文件扩展名
        file_ext = Path(filename).suffix.lower()
        if file_ext not in ['.dxf', '.dwg']:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': f'不支持的文件格式: {file_ext}'})
            }
        
        # 保存文件
        file_path = temp_dir / f"{file_id}{file_ext}"
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        # 返回成功响应
        response = {
            'file_id': file_id,
            'filename': filename,
            'size': len(file_data),
            'upload_time': datetime.now().isoformat(),
            'message': '文件上传成功'
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response, ensure_ascii=False)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': f'上传失败: {str(e)}'}, ensure_ascii=False)
        }
