# CAD 规范符合性检查器

AI 驱动的Web应用，自动化检查CAD图纸是否符合既定的工程标准（专注于GB/T 14665-2012）。

## 项目结构

```
CAD/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── api/         # API 路由
│   │   ├── models/      # 数据模型
│   │   ├── services/    # 业务逻辑服务
│   │   └── utils/       # 工具函数
│   ├── config/          # 规则配置文件
│   ├── tests/           # 测试
│   └── uploads/         # 临时文件存储
├── frontend/            # Next.js 前端
│   ├── app/             # 页面
│   ├── components/      # 组件
│   ├── lib/             # API 库
│   └── types/           # TypeScript 类型
├── docker-compose.yml
└── prd.md              # 产品需求文档
```

## Phase 1 MVP 功能

✅ 已实现的功能：

### 后端
- **文件上传与解析**：支持 DXF 和 **DWG** 文件上传，使用 ezdxf 解析，自动 DWG 转换
- **规则检查引擎**：
  - 图层检查（GB/T 14665-2012 表6）
  - 线宽检查（表1）
  - 颜色检查（表2）
  - 字体检查（表3）
  - 尺寸标注检查（6.3节）
- **合规报告生成**：JSON/HTML 格式导出
- **RESTful API**：完整的 CRUD 接口

### 前端
- **文件上传界面**：拖放式上传，支持 DXF 格式
- **实时分析状态**：轮询获取分析进度
- **报告展示页面**：
  - 合规性总结卡片
  - 违规项详细列表
  - 修复建议
  - 报告导出功能

## 技术栈

### 后端
- **语言**: Python 3.11+
- **框架**: FastAPI
- **CAD 解析**: ezdxf
- **几何计算**: shapely (Phase 2)
- **数据验证**: Pydantic
- **配置管理**: YAML

### 前端
- **框架**: Next.js 15 (App Router)
- **语言**: TypeScript
- **样式**: Tailwind CSS
- **组件**: React Dropzone

### 部署
- **容器化**: Docker & Docker Compose
- **前端托管**: Vercel-ready
- **后端托管**: 任何支持 Docker 的平台

## 快速开始

### 前提条件
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (可选)

### 本地开发

#### 1. 后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 复制环境变量
copy .env.example .env

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看 API 文档

#### 2. 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:3000

### Docker 部署

```bash
# 构建并启动所有服务
docker-compose up --build

# 后台运行
docker-compose up -d

# 停止服务
docker-compose down
```

## API 文档

### 上传文件
```
POST /api/v1/upload
Content-Type: multipart/form-data

Response:
{
  "file_id": "uuid",
  "filename": "example.dxf",
  "size": 1024,
  "upload_time": "2025-10-13T..."
}
```

### 启动分析
```
POST /api/v1/analyze
Content-Type: application/json

{
  "file_id": "uuid",
  "standard": "GB/T 14665-2012"
}

Response:
{
  "analysis_id": "uuid",
  "file_id": "uuid",
  "status": "pending"
}
```

### 获取报告
```
GET /api/v1/report/{analysis_id}

Response:
{
  "analysis_id": "uuid",
  "filename": "example.dxf",
  "standard": "GB/T 14665-2012",
  "total_violations": 5,
  "is_compliant": false,
  "compliance_score": 75.0,
  "violations": [...]
}
```

### 导出报告
```
GET /api/v1/report/{analysis_id}/export?format=json|html|pdf
```

## DWG 文件支持 🆕

系统现已支持 **DWG 文件**！无需手动转换，直接上传 .dwg 文件即可。

### 快速使用

1. **无需额外配置**：系统默认使用 ezdxf 尝试读取 DWG
2. **推荐配置**：安装 [ODA File Converter](https://www.opendesign.com/guestfiles/oda_file_converter) 获得最佳兼容性
3. **详细文档**：查看 `DWG_SUPPORT.md`

### 转换策略

系统按以下顺序尝试转换：
1. **ezdxf** - 直接读取（默认，支持较新版本）
2. **ODA Converter** - 官方工具（支持所有版本，需安装）
3. **LibreDWG** - 开源方案（可选）

### 配置 ODA Converter（可选）

```env
# .env 文件
ODA_CONVERTER_PATH=C:/Program Files/ODA/ODAFileConverter/ODAFileConverter.exe
```

---

## 配置

### 后端环境变量 (`.env`)
```
DEBUG=true
HOST=0.0.0.0
PORT=8000
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760
ALLOWED_EXTENSIONS=dxf,dwg  # 支持 DXF 和 DWG
ANALYSIS_TIMEOUT=60  # DWG 转换需要更多时间

# DWG 转换配置（可选）
# ODA_CONVERTER_PATH=C:/Program Files/ODA/ODAFileConverter/ODAFileConverter.exe
TEMP_DIR=./temp
```

### 前端环境变量 (`.env.local`)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 规则配置

规则配置位于 `backend/config/rules_gbt14665.yaml`，可根据需求调整：

```yaml
layers:
  尺寸层:
    expected_names: ["尺寸", "DIMENSION", "DIM"]
    lineweight: 0.25
    
lineweights:
  thick_line: 0.5
  thin_line: 0.25
  tolerance: 0.05
```

## 测试

```bash
# 后端测试
cd backend
pytest tests/

# 前端测试
cd frontend
npm test
```

## 开发路线图

### ✅ Phase 1: MVP - 基础规则引擎 (当前)
- 文件上传与解析
- 基础属性检查（图层、线宽、字体、尺寸）
- 简单合规报告

### 🔄 Phase 2: 高级空间与视觉分析 (计划中)
- 几何关系引擎（Shapely）
- 计算机视觉子系统（PyTorch/TensorFlow）
- 交互式可视化报告

### 📅 Phase 3: 语义与上下文智能 (未来)
- LLM 驱动的文本分析（Gemini API）
- 生成式错误解释
- Human-in-the-Loop 反馈系统

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

如有问题，请提交 Issue 或联系项目维护者。
