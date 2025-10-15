# 快速启动指南

## 🚀 5 分钟快速上手

### 前提条件
- ✅ Python 3.11 已安装
- ✅ Node.js 已安装
- ✅ 后端和前端依赖已安装

### 启动系统

#### 方法 1: 使用启动脚本 (推荐)
```powershell
.\start.ps1
```

#### 方法 2: 手动启动

**终端 1 - 后端**:
```powershell
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**终端 2 - 前端**:
```powershell
cd frontend
npm run dev
```

### 访问系统
- 🌐 **前端**: http://localhost:3000
- 🔌 **后端 API**: http://localhost:8000
- 📚 **API 文档**: http://localhost:8000/docs

---

## 📝 测试系统

### 步骤 1: 创建测试文件
```powershell
python create_test_dxf.py
```

这会在 `backend/uploads/` 创建 `test_sample.dxf`

### 步骤 2: 上传并分析

1. 访问 http://localhost:3000
2. 拖放或选择 `test_sample.dxf` 文件
3. 等待分析完成（约 5 秒）
4. 查看合规性报告

### 预期结果
- ✅ 合规得分: 81.0
- ✅ 检测到 5 个违规项
- ✅ 提供详细的修复建议

---

## 🔍 健康检查

```powershell
.\check_system.ps1
```

这会检查：
- 后端和前端服务状态
- 端口占用情况
- API 端点可用性
- 文件结构完整性

---

## 🛠️ 调试工具

### 调试分析流程
```powershell
python debug_analysis.py <DXF文件路径>
```

示例:
```powershell
python debug_analysis.py backend/uploads/test_sample.dxf
```

---

## 📄 使用自己的 CAD 文件

### ✅ DXF 格式 (推荐)

1. 访问 http://localhost:3000
2. 上传 DXF 文件
3. 等待分析完成
4. 查看报告

### ⚠️ DWG 格式

**不推荐**，因为转换支持有限。

**推荐做法**：
1. 在 AutoCAD 中打开 DWG 文件
2. **文件 → 另存为 → AutoCAD DXF (*.dxf)**
3. 上传转换后的 DXF 文件

详细信息请参考 `docs/DWG_FORMAT_GUIDE.md`

---

## 🎯 常见操作

### 上传文件 (API)
```powershell
$file = "path/to/your/file.dxf"
curl -X POST http://localhost:8000/api/v1/upload `
  -F "file=@$file"
```

### 启动分析 (API)
```powershell
$body = @{
  file_id = "your-file-id"
  standard = "GB/T 14665-2012"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "http://localhost:8000/api/v1/analyze" `
  -Method Post `
  -Body $body `
  -ContentType "application/json"
```

### 获取报告 (API)
```powershell
Invoke-RestMethod `
  -Uri "http://localhost:8000/api/v1/report/<analysis-id>" `
  -Method Get
```

---

## 📚 更多文档

- **项目介绍**: `README.md`
- **产品需求**: `prd.md`
- **开发计划**: `docs/DEVELOPMENT_PLAN.md`
- **DWG 格式**: `docs/DWG_FORMAT_GUIDE.md`
- **问题解决**: `UPLOAD_ISSUE_SOLVED.md`
- **测试报告**: `TEST_RESULTS.md`

---

## 💡 提示

### 获得最佳结果
1. ✅ 使用 DXF 格式
2. ✅ 确保文件 < 10MB
3. ✅ 确保图纸遵循 GB/T 14665-2012 标准

### 如果遇到问题
1. 运行 `.\check_system.ps1` 检查系统状态
2. 查看后端控制台的错误日志
3. 使用 `debug_analysis.py` 调试具体文件
4. 参考 `UPLOAD_ISSUE_SOLVED.md`

---

## ⭐ 系统特性

- ⚡ **快速**: 30 秒内完成分析
- 🎯 **准确**: 100% 基于 GB/T 14665-2012 标准
- 📊 **详细**: 提供完整的违规分析和建议
- 🖥️ **友好**: 现代化的 Web 界面
- 🔧 **可扩展**: 易于添加新规则和标准

---

**准备好了吗？立即开始！** 🚀

```powershell
.\start.ps1
```

然后访问 http://localhost:3000
