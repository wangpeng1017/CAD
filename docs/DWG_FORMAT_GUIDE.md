# DWG 格式使用指南

## 当前状态

CAD 规范符合性检查器 **主要支持 DXF 格式**。DWG 格式支持有限且可能导致分析失败。

## 为什么 DXF 更好？

1. **DXF 是开放格式** - 易于解析和处理
2. **广泛兼容** - 所有 CAD 软件都支持
3. **稳定可靠** - 不会有版本兼容问题
4. **分析准确** - 100% 支持所有检查规则

## 如何将 DWG 转换为 DXF

### 方法 1: AutoCAD

1. 在 AutoCAD 中打开 DWG 文件
2. 点击 **文件 → 另存为**
3. 在"文件类型"下拉菜单中选择 **"AutoCAD DXF (*.dxf)"**
4. 选择 DXF 版本（推荐：**AutoCAD 2018 DXF**）
5. 点击保存

### 方法 2: BricsCAD

1. 打开 DWG 文件
2. **文件 → 导出 → DXF**
3. 选择版本和保存位置
4. 点击导出

### 方法 3: FreeCAD (免费开源)

1. 下载 FreeCAD: https://www.freecadweb.org/
2. **文件 → 打开** DWG 文件
3. **文件 → 导出**
4. 选择 DXF 格式

### 方法 4: ODA File Converter (免费)

1. 下载 ODA File Converter:
   https://www.opendesign.com/guestfiles/oda_file_converter
2. 安装后运行
3. 选择输入文件夹和输出文件夹
4. 选择输出格式：**DXF**
5. 选择输出版本：**ACAD 2018**
6. 点击转换

## DWG 格式的技术限制

### 当前尝试的转换方法

系统尝试以下方法转换 DWG：

1. **ODA File Converter** - 需要预先安装
2. **ezdxf 直接读取** - 仅支持部分 DWG 版本
3. **LibreDWG** - 需要系统依赖

### 为什么会失败？

- DWG 是 Autodesk 的专有格式
- 格式规范不公开
- 版本众多（R14, 2000, 2004, 2007, 2010, 2013, 2018 等）
- 需要特殊的解析库或商业许可

## 解决方案

### 推荐方案（✅ 最佳）

**使用 DXF 格式**
- 在源 CAD 软件中导出为 DXF
- 上传 DXF 文件进行分析
- 获得最准确的检查结果

### 临时方案（⚠️ 不推荐）

如果必须使用 DWG：
1. 在系统上安装 ODA File Converter
2. 配置后端 `config.py` 中的 ODA 路径：
   ```python
   ODA_CONVERTER_PATH = "C:/Program Files/ODA/ODAFileConverter/ODAFileConverter.exe"
   ```
3. 重启后端服务
4. 系统会自动尝试转换 DWG 文件

## 未来计划

在后续版本中，我们计划：

1. ✅ Phase 1 (当前): DXF 完全支持
2. 🚧 Phase 2: 集成商业 DWG SDK
3. 🚧 Phase 3: 云端 DWG 转换服务
4. 🚧 Phase 4: 原生 DWG 支持

## 常见问题

### Q: 为什么不能直接支持 DWG？

A: DWG 是专有格式，需要：
- 购买商业许可证
- 集成复杂的 SDK
- 处理大量版本兼容性问题

当前阶段优先确保 DXF 格式的完美支持。

### Q: 上传 DWG 后分析失败怎么办？

A: 请按照以下步骤：
1. 在 CAD 软件中打开文件
2. 另存为 DXF 格式
3. 重新上传 DXF 文件

### Q: DXF 文件会丢失信息吗？

A: 不会。DXF 是 AutoCAD 的原生格式之一，包含完整的图形信息。对于规范符合性检查，DXF 格式完全足够。

### Q: 转换后的 DXF 文件能在 CAD 软件中打开吗？

A: 可以。DXF 文件可以在所有 CAD 软件中打开和编辑，与 DWG 功能完全相同。

## 技术支持

如需帮助，请参考：

1. **系统文档**: `README.md`
2. **开发指南**: `docs/DEVELOPMENT_PLAN.md`
3. **API 文档**: http://localhost:8000/docs

## 总结

✅ **使用 DXF 格式** = 稳定、快速、准确
❌ **使用 DWG 格式** = 可能失败、需要额外配置

**建议：在源 CAD 软件中导出 DXF，确保最佳体验。**
