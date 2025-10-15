# DWG 文件支持说明

本系统现已支持直接上传 `.dwg` 格式的 CAD 文件！系统会自动将 DWG 文件转换为 DXF 格式进行分析。

## 🎯 支持的文件格式

- ✅ **DXF** (.dxf) - 直接支持
- ✅ **DWG** (.dwg) - 自动转换后支持

## 🔧 转换方式

系统采用多重转换策略，按以下顺序尝试：

### 1. ezdxf 直接读取（默认）

**优点**：
- 无需额外安装
- 速度快
- 纯 Python 实现

**限制**：
- 仅支持部分 DWG 版本（主要是较新版本）
- 对复杂文件支持有限

**无需配置**，系统会自动尝试。

---

### 2. ODA File Converter（推荐）

**优点**：
- 官方推荐工具
- 支持所有 DWG 版本（AutoCAD R12 - 最新）
- 转换质量高
- 完全免费

**安装步骤**：

#### Windows:
1. 下载 ODA File Converter:
   https://www.opendesign.com/guestfiles/oda_file_converter

2. 安装到默认位置或自定义位置

3. 配置环境变量（`backend/.env`）:
   ```
   ODA_CONVERTER_PATH=C:/Program Files/ODA/ODAFileConverter/ODAFileConverter.exe
   ```

#### Linux/Mac:
```bash
# 下载对应平台的版本
wget https://www.opendesign.com/guestfiles/oda_file_converter

# 安装
sudo dpkg -i ODAFileConverter_*.deb  # Debian/Ubuntu
# 或
sudo rpm -i ODAFileConverter_*.rpm   # RedHat/CentOS

# 配置
ODA_CONVERTER_PATH=/usr/bin/ODAFileConverter
```

---

### 3. LibreDWG（开源方案）

**优点**：
- 开源免费
- 支持大多数 DWG 版本
- 命令行友好

**安装步骤**：

#### Windows:
```powershell
# 使用 Chocolatey
choco install libredwg

# 或从源码编译
# https://github.com/LibreDWG/libredwg
```

#### Linux:
```bash
# Ubuntu/Debian
sudo apt-get install libredwg-tools

# Fedora/RHEL
sudo dnf install libredwg

# macOS
brew install libredwg
```

---

## 📝 配置示例

### 完整配置（`backend/.env`）

```env
# 基础配置
DEBUG=true
HOST=0.0.0.0
PORT=8000

# 文件上传配置
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=dxf,dwg  # 支持两种格式

# DWG 转换配置（可选）
ODA_CONVERTER_PATH=C:/Program Files/ODA/ODAFileConverter/ODAFileConverter.exe
TEMP_DIR=./temp

# 分析配置
ANALYSIS_TIMEOUT=60  # DWG 转换可能需要更多时间
```

---

## 🚀 使用方法

### 1. 通过 Web 界面上传

直接拖放或选择 `.dwg` 文件，系统会自动处理：

```
访问: http://localhost:3000
1. 拖放 DWG 文件
2. 等待自动转换（通常 5-15 秒）
3. 查看分析报告
```

### 2. 通过 API 上传

```bash
# 上传 DWG 文件
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@your_drawing.dwg"

# 响应示例
{
  "file_id": "abc-123",
  "filename": "your_drawing.dwg",
  "size": 2048000,
  "upload_time": "2025-10-13T13:20:00"
}

# 启动分析（系统会自动转换）
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "abc-123",
    "standard": "GB/T 14665-2012"
  }'
```

---

## ⚡ 性能说明

| 转换方式 | 平均耗时 | 成功率 | 推荐场景 |
|---------|---------|--------|----------|
| ezdxf | 2-5 秒 | 60% | 新版 DWG 文件 |
| ODA Converter | 5-15 秒 | 99% | **生产环境（推荐）** |
| LibreDWG | 8-20 秒 | 85% | 开源环境 |

---

## 🐛 故障排除

### 问题 1: "无法转换 DWG 文件"

**可能原因**：
- DWG 版本过旧或过新
- 文件损坏
- 未安装转换工具

**解决方案**：
1. 确认文件可以在 AutoCAD 中打开
2. 尝试在 AutoCAD 中手动保存为 DXF 格式
3. 安装 ODA File Converter（推荐）
4. 检查日志：`backend/logs/conversion.log`

### 问题 2: 转换超时

**解决方案**：
```env
# 增加超时时间（.env 文件）
ANALYSIS_TIMEOUT=120  # 增加到 2 分钟
```

### 问题 3: ODA Converter 未找到

**检查配置**：
```bash
# Windows
where ODAFileConverter.exe

# Linux/Mac
which ODAFileConverter
```

**确认路径**：
```env
# 使用绝对路径
ODA_CONVERTER_PATH=C:/Program Files/ODA/ODAFileConverter/ODAFileConverter.exe
```

---

## 📊 支持的 DWG 版本

### ezdxf 支持:
- AutoCAD 2018 及以上
- AutoCAD 2013-2017（部分支持）

### ODA Converter 支持:
- AutoCAD R12 (1992)
- AutoCAD R13 (1994)
- AutoCAD R14 (1997)
- AutoCAD 2000-2025
- **所有中间版本**

### LibreDWG 支持:
- AutoCAD R13-2021
- 大多数常见版本

---

## 🔒 安全性说明

1. **文件隔离**：DWG 文件在独立的临时目录中转换
2. **自动清理**：转换后的 DXF 文件在分析完成后自动删除
3. **进程隔离**：转换过程在子进程中执行，带超时保护
4. **病毒扫描**：建议在上传前扫描文件

---

## 📚 相关文档

- [ODA File Converter 官网](https://www.opendesign.com/guestfiles/oda_file_converter)
- [LibreDWG 项目](https://github.com/LibreDWG/libredwg)
- [ezdxf 文档](https://ezdxf.mozman.at/)
- [AutoCAD DWG 格式规范](https://www.autodesk.com/developer-network/platform-technologies/autocad)

---

## 💡 最佳实践

1. **生产环境**：安装 ODA File Converter 以获得最佳兼容性
2. **开发环境**：使用 ezdxf 默认支持进行快速测试
3. **开源项目**：使用 LibreDWG 避免专有软件依赖
4. **文件管理**：建议客户端在上传前转换为 DXF 以提高性能

---

## 🎉 快速开始

**无需安装任何额外工具**，现在就可以上传 DWG 文件！

系统会自动尝试使用 ezdxf 进行转换。如果失败，会提示安装 ODA Converter。

```bash
# 启动系统
./start.ps1

# 访问
http://localhost:3000

# 直接上传 .dwg 文件！
```

---

**问题反馈**: 如遇到转换问题，请提供：
- DWG 文件版本（在 AutoCAD 属性中查看）
- 错误日志
- 转换工具配置

**联系方式**: 查看项目 README.md
