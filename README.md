# CAD 规范符合性检查器

AI 驱动的 CAD 图纸自动检查系统，支持 GB/T 14665-2012 机械工程 CAD 制图规则标准。

## 项目结构

```
CAD/
├── api/                    # Vercel Serverless Functions
│   ├── upload.py          # 文件上传 API
│   └── analyze.py         # 文件分析 API
├── checker/               # 核心检查模块
│   ├── __init__.py
│   ├── models.py          # 数据模型
│   ├── parser.py          # DXF 解析器
│   └── checker.py         # 合规性检查器
├── config/                # 配置文件
│   └── rules_gbt14665.yaml # GB/T 14665-2012 规则
├── frontend/              # Next.js 前端应用
│   ├── app/
│   │   ├── page.tsx       # 首页
│   │   ├── result/[id]/   # 报告页面
│   │   └── layout.tsx
│   ├── components/        # React 组件
│   └── types/             # TypeScript 类型定义
├── requirements.txt       # Python 依赖
├── vercel.json           # Vercel 配置
└── prd.md                # 产品需求文档
```

## 功能特点

### ✅ 第一阶段（MVP）- 已完成

- **文件上传与解析** (P1-F01)
  - 支持 DXF 文件格式
  - 最大文件大小：10MB
  - 快速解析和结构化数据提取

- **基础规则检查** (P1-F02)
  - ✓ 图层规范检查（GB/T 14665-2012 表6）
  - ✓ 线宽规范检查（GB/T 14665-2012 表1）
  - ✓ 颜色规范检查（GB/T 14665-2012 表2）
  - ✓ 字体规范检查（GB/T 14665-2012 表3）
  - ✓ 尺寸标注检查（GB/T 14665-2012 6.3节）

- **合规性报告** (P1-F03)
  - 详细的违规项列表
  - 合规得分计算
  - 修复建议
  - 支持复制到剪贴板
  - 支持下载 JSON 格式报告

## 技术架构

### 前端
- **框架**: Next.js 14 (App Router)
- **语言**: TypeScript
- **样式**: Tailwind CSS
- **部署**: Vercel

### 后端
- **语言**: Python 3.9+
- **核心库**: 
  - `ezdxf` - DXF 文件解析
  - `pydantic` - 数据验证
  - `PyYAML` - 配置管理
- **API**: Vercel Serverless Functions
- **部署**: Vercel

## 本地开发

### 前置要求

- Node.js 18+
- Python 3.9+
- npm 或 yarn

### 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装前端依赖
cd frontend
npm install
```

### 启动开发服务器

```bash
# 在项目根目录
cd frontend
npm run dev
```

访问 http://localhost:3000

### 使用 Vercel CLI 本地测试

```bash
# 安装 Vercel CLI
npm install -g vercel

# 在项目根目录运行
vercel dev
```

## 部署到 Vercel

### 一键部署

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/cad-checker)

### 手动部署

```bash
# 登录 Vercel
vercel login

# 部署
vercel --prod
```

### 环境配置

在 Vercel 项目设置中配置以下环境变量（如需要）：

- `PYTHON_VERSION`: `3.9`

## API 文档

### POST /api/upload

上传 DXF 文件

**请求**:
- Content-Type: `multipart/form-data`
- Body: file (DXF 文件)

**响应**:
```json
{
  "file_id": "uuid",
  "filename": "example.dxf",
  "size": 1024000,
  "upload_time": "2025-10-16T14:00:00",
  "message": "文件上传成功"
}
```

### POST /api/analyze

分析上传的文件

**请求**:
```json
{
  "file_id": "uuid",
  "standard": "GB/T 14665-2012"
}
```

**响应**:
```json
{
  "analysis_id": "uuid",
  "file_id": "uuid",
  "status": "completed",
  "message": "分析完成",
  "report": {
    "analysis_id": "uuid",
    "filename": "example.dxf",
    "standard": "GB/T 14665-2012",
    "analysis_time": "2025-10-16T14:00:00",
    "total_violations": 5,
    "critical_count": 0,
    "warning_count": 3,
    "info_count": 2,
    "is_compliant": true,
    "compliance_score": 85.0,
    "violations": [...]
  }
}
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
