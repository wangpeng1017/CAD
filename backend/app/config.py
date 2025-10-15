"""
应用配置管理
"""
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用信息
    app_name: str = "CAD Compliance Checker"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    
    # 文件上传配置
    upload_dir: Path = Path("./uploads")
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: list[str] = ["dxf", "dwg"]  # 支持 DXF 和 DWG
    
    # DWG 转换配置
    oda_converter_path: str = ""  # ODA File Converter 路径（可选）
    temp_dir: Path = Path("./temp")  # 临时转换目录
    
    # 分析配置
    analysis_timeout: int = 30
    
    # 日志配置
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 全局配置实例
settings = Settings()

# 确保目录存在
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.temp_dir.mkdir(parents=True, exist_ok=True)
