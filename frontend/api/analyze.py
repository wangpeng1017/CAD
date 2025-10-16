"""
文件分析 API - Vercel Serverless Function (Next.js project root)
"""
from http.server import BaseHTTPRequestHandler
import json
import uuid
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from checker import DXFParser, ComplianceChecker
except ImportError:
    # Fallback: 从上级目录导入
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
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))

            file_id = data.get('file_id')
            standard = data.get('standard', 'GB/T 14665-2012')
            if not file_id:
                return self._json(400, {"error": "缺少 file_id 参数"})

            temp_dir = Path('/tmp/cad_uploads')
            file_path = None
            for ext in ['.dxf', '.dwg']:
                path = temp_dir / f"{file_id}{ext}"
                if path.exists():
                    file_path = path
                    break
            if not file_path:
                return self._json(404, {"error": "文件不存在"})

            analysis_id = str(uuid.uuid4())
            parser = DXFParser()
            dxf_data = parser.parse(str(file_path))

            checker = ComplianceChecker(standard=standard)
            report = checker.check(dxf_data, analysis_id, file_id)

            report_path = Path('/tmp/cad_reports')
            report_path.mkdir(parents=True, exist_ok=True)
            with open(report_path / f"{analysis_id}.json", 'w', encoding='utf-8') as f:
                json.dump(report.model_dump(mode='json'), f, ensure_ascii=False, indent=2)

            return self._json(200, {
                "analysis_id": analysis_id,
                "file_id": file_id,
                "status": "completed",
                "message": "分析完成",
                "report": report.model_dump(mode='json')
            })
        except ValueError as e:
            return self._json(400, {"error": str(e)})
        except Exception as e:
            return self._json(500, {"error": f"分析失败: {str(e)}"})

    def _json(self, status, data):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
