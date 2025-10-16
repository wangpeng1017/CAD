# CAD 规范符合性检查器 - 部署状态与数据库改进方案

## 📊 当前部署状态

### ✅ 已完成部署

#### 后端 (cad-backend)
- **状态**: ✅ 运行中
- **容器**: `cad-backend-54b56b8b48-hkvn6`
- **服务地址**: http://103.109.20.169:10437
- **资源使用**:
  - CPU: 1m / 500m (0%)
  - 内存: 66Mi / 512Mi (13%)
- **环境变量**: 无
- **存储**: 无持久化存储

#### 前端 (cad-frontend)
- **状态**: ✅ 运行中 (旧版本)
- **容器**: `cad-frontend-7b747f6b75-jfvhd`
- **服务地址**: http://103.109.20.169:10433
- **资源使用**:
  - CPU: 0m / 500m (0%)
  - 内存: 0Mi / 512Mi (0%)
- **环境变量**:
  - `NEXT_PUBLIC_API_URL`: http://103.109.20.169:10437
  - `BACKEND_URL`: http://103.109.20.169:10437

### 🔴 发现的问题

#### 1. **前端镜像未更新**
- GitHub Actions 构建完成 (Commit: f9aa69e)
- Docker Hub 镜像已推送
- **但 Leaflow 尚未拉取最新镜像**
- 当前运行的仍是旧版本容器

**解决方案**:
```bash
# 在 Leaflow 控制台执行"重启"操作，强制拉取最新镜像
# 或者手动更新部署
kubectl rollout restart deployment/cad-frontend -n ns-8-gjhfoulo
```

#### 2. **文件上传功能仍未工作**
- 点击"选择文件"按钮无反应
- 可能原因：
  - 前端镜像未更新（主要原因）
  - React Dropzone 配置问题
  - CORS 或网络连接问题

---

## 🗄️ 当前存储架构分析

### 现有实现

#### 文件存储
```python
# backend/app/config.py
upload_dir: Path = Path("./uploads")  # 本地文件系统
temp_dir: Path = Path("./temp")       # 临时文件
```

#### 数据存储
```python
# backend/app/api/analysis.py
analysis_results = {}  # 内存字典存储
```

### ⚠️ 存在的问题

1. **数据持久化缺失**
   - 重启容器后所有分析记录丢失
   - 无法查看历史报告
   - 无法追踪用户操作

2. **并发问题**
   - 内存字典不支持分布式部署
   - 多个Pod实例无法共享数据
   - 扩容会导致数据不一致

3. **文件管理问题**
   - 上传的文件存储在容器内
   - 容器重启后文件丢失
   - 无法跨Pod访问文件

4. **无用户管理**
   - 无法区分不同用户的文件
   - 无法实施访问控制
   - 无审计日志

---

## 🎯 数据库配置改进方案

### Phase 1: SQLite (快速实施)

适用于小规模部署，无需额外服务。

#### 1.1 安装依赖
```bash
# backend/requirements.txt
sqlalchemy==2.0.23
alembic==1.13.0
aiosqlite==0.19.0
```

#### 1.2 数据库模型
```python
# backend/app/models/database.py
from sqlalchemy import Column, String, DateTime, Integer, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class UploadedFile(Base):
    __tablename__ = "uploaded_files"
    
    id = Column(String(36), primary_key=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    size = Column(Integer, nullable=False)
    file_path = Column(String(512), nullable=False)
    upload_time = Column(DateTime, default=datetime.now)
    content_type = Column(String(100))

class AnalysisRecord(Base):
    __tablename__ = "analysis_records"
    
    id = Column(String(36), primary_key=True)
    file_id = Column(String(36), nullable=False)
    standard = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)
    total_violations = Column(Integer, default=0)
    critical_count = Column(Integer, default=0)
    warning_count = Column(Integer, default=0)
    info_count = Column(Integer, default=0)
    compliance_score = Column(Float)
    is_compliant = Column(Integer)  # 0/1 for boolean
    started_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime)
    error_message = Column(Text)

class Violation(Base):
    __tablename__ = "violations"
    
    id = Column(String(36), primary_key=True)
    analysis_id = Column(String(36), nullable=False)
    type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    rule = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    entity_handle = Column(String(50))
    layer = Column(String(100))
    location = Column(String(255))
    suggestion = Column(Text)
```

#### 1.3 配置更新
```python
# backend/app/config.py
class Settings(BaseSettings):
    # 数据库配置
    database_url: str = "sqlite:///./cad_checker.db"
    
    # 文件存储配置
    use_persistent_storage: bool = False  # Phase 1 先用容器存储
    storage_backend: str = "local"  # local | s3 | minio
```

### Phase 2: PostgreSQL + 对象存储 (生产推荐)

适用于生产环境，支持高可用和横向扩展。

#### 2.1 Leaflow 数据库创建

1. 访问 https://leaflow.net/databases
2. 创建新数据库:
   - 名称: `cad-checker-db`
   - 类型: PostgreSQL 15
   - 规格: 根据需求选择

#### 2.2 更新依赖
```txt
# backend/requirements.txt
sqlalchemy==2.0.23
alembic==1.13.0
asyncpg==0.29.0  # PostgreSQL async driver
psycopg2-binary==2.9.9
```

#### 2.3 环境变量配置
```yaml
# Leaflow 部署配置
env:
  - name: DATABASE_URL
    value: "postgresql+asyncpg://user:password@postgres-service:5432/cad_checker"
  - name: STORAGE_BACKEND
    value: "s3"  # 或 minio
  - name: S3_BUCKET
    value: "cad-checker-uploads"
  - name: S3_ENDPOINT
    value: "https://s3.amazonaws.com"
  - name: S3_ACCESS_KEY
    valueFrom:
      secretKeyRef:
        name: s3-credentials
        key: access-key
  - name: S3_SECRET_KEY
    valueFrom:
      secretKeyRef:
        name: s3-credentials
        key: secret-key
```

#### 2.4 持久化存储卷
```yaml
# Leaflow 存储配置
volumes:
  - name: uploads
    persistentVolumeClaim:
      claimName: cad-uploads-pvc

volumeMounts:
  - name: uploads
    mountPath: /app/uploads
```

#### 2.5 对象存储服务
```python
# backend/app/services/storage.py
from abc import ABC, abstractmethod
import boto3
from pathlib import Path

class StorageBackend(ABC):
    @abstractmethod
    async def upload_file(self, file_path: str, object_name: str) -> str:
        pass
    
    @abstractmethod
    async def download_file(self, object_name: str, dest_path: str):
        pass

class S3Storage(StorageBackend):
    def __init__(self, bucket: str, endpoint: str, access_key: str, secret_key: str):
        self.s3 = boto3.client(
            's3',
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        self.bucket = bucket
    
    async def upload_file(self, file_path: str, object_name: str) -> str:
        self.s3.upload_file(file_path, self.bucket, object_name)
        return f"s3://{self.bucket}/{object_name}"
    
    async def download_file(self, object_name: str, dest_path: str):
        self.s3.download_file(self.bucket, object_name, dest_path)
```

---

## 📝 实施步骤

### 立即执行 (Phase 1 - 基础数据库)

1. **更新前端镜像**
   ```bash
   # 在 Leaflow 控制台重启 cad-frontend
   # 或在 Kubernetes 中执行:
   kubectl rollout restart deployment/cad-frontend -n ns-8-gjhfoulo
   ```

2. **添加 SQLite 数据库**
   ```bash
   cd backend
   
   # 安装依赖
   pip install sqlalchemy alembic aiosqlite
   
   # 创建数据库迁移
   alembic init alembic
   alembic revision --autogenerate -m "Initial tables"
   alembic upgrade head
   ```

3. **更新 API 使用数据库**
   ```python
   # backend/app/api/analysis.py
   # 替换内存字典为数据库查询
   from app.database import get_db
   from app.models.database import AnalysisRecord
   
   @router.post("/analyze")
   async def start_analysis(request: AnalysisRequest, db = Depends(get_db)):
       # 创建数据库记录而非内存字典
       record = AnalysisRecord(
           id=analysis_id,
           file_id=request.file_id,
           standard=request.standard,
           status="pending"
       )
       db.add(record)
       await db.commit()
   ```

4. **测试验证**
   - 重启后数据仍然存在
   - 可以查看历史记录
   - 分析状态持久化

### 短期优化 (1-2周)

5. **添加持久化存储卷**
   - 在 Leaflow 创建 PVC
   - 挂载到 backend 容器
   - 迁移文件到持久化存储

6. **添加用户认证**
   - JWT 令牌
   - 用户表
   - 权限控制

### 中期改进 (1个月)

7. **迁移到 PostgreSQL**
   - 在 Leaflow 创建 PostgreSQL 数据库
   - 配置连接字符串
   - 迁移数据

8. **集成对象存储**
   - 配置 MinIO 或 S3
   - 文件上传到对象存储
   - 数据库仅存储元数据

---

## 🔧 配置文件示例

### backend/.env
```env
# 应用配置
DEBUG=false
APP_NAME=CAD Compliance Checker
APP_VERSION=1.0.0

# 数据库
DATABASE_URL=sqlite:///./cad_checker.db
# DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname

# 文件存储
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760
STORAGE_BACKEND=local
# STORAGE_BACKEND=s3

# S3/MinIO (如果使用)
# S3_ENDPOINT=https://s3.amazonaws.com
# S3_BUCKET=cad-uploads
# S3_ACCESS_KEY=your-access-key
# S3_SECRET_KEY=your-secret-key

# 分析配置
ANALYSIS_TIMEOUT=300
```

### Leaflow Kubernetes 配置
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cad-backend
spec:
  replicas: 2  # 支持横向扩展
  template:
    spec:
      containers:
      - name: main
        image: your-registry/cad-backend:latest
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: connection-string
        - name: STORAGE_BACKEND
          value: "s3"
        volumeMounts:
        - name: uploads
          mountPath: /app/uploads
      volumes:
      - name: uploads
        persistentVolumeClaim:
          claimName: cad-uploads-pvc
```

---

## ✅ 验证检查清单

- [ ] GitHub Actions 构建成功
- [ ] Docker 镜像已推送
- [ ] Leaflow 前端容器已更新
- [ ] 文件上传功能正常
- [ ] 数据库表已创建
- [ ] 分析记录持久化
- [ ] 容器重启后数据保留
- [ ] 多Pod实例数据一致
- [ ] 文件存储到持久化卷
- [ ] API 响应正常

---

## 📚 相关文档

- [Leaflow 数据库文档](https://leaflow.net/docs/databases)
- [Leaflow 存储管理](https://leaflow.net/docs/storage)
- [SQLAlchemy 异步文档](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Alembic 迁移指南](https://alembic.sqlalchemy.org/)

---

**生成时间**: 2025-10-16 12:46 CST  
**状态**: 部署完成，待前端镜像更新和数据库实施
