"""
CAD 规范符合性检查器 - FastAPI 主应用
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import upload, analysis, report

app = FastAPI(
    title="CAD Compliance Checker API",
    description="AI驱动的CAD图纸规范符合性检查系统",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",        # Next.js 开发服务器
        "https://cad.aifly.me",         # 生产环境前端（HTTPS）
        "http://cad.aifly.me",          # 生产环境前端（HTTP）
        "http://103.109.20.169:10433",  # LoadBalancer IP
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(upload.router, prefix="/api/v1", tags=["上传"])
app.include_router(analysis.router, prefix="/api/v1", tags=["分析"])
app.include_router(report.router, prefix="/api/v1", tags=["报告"])


@app.get("/")
async def root():
    """健康检查端点"""
    return {
        "status": "ok",
        "service": "CAD Compliance Checker",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """详细健康检查"""
    return {
        "status": "healthy",
        "services": {
            "api": "running",
            "parser": "ready"
        }
    }
