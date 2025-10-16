# 部署指南

## 前置准备

1. **GitHub 账号**
2. **Vercel 账号**（可用 GitHub 登录）
3. **项目代码推送到 GitHub**

## 快速部署到 Vercel

### 方式一：通过 Vercel Dashboard

1. 访问 [https://vercel.com](https://vercel.com)
2. 点击 "New Project"
3. 导入你的 GitHub 仓库
4. Vercel 会自动检测 Next.js 项目和配置
5. 点击 "Deploy"

### 方式二：通过 Vercel CLI

```bash
# 安装 Vercel CLI
npm install -g vercel

# 登录
vercel login

# 在项目根目录运行
vercel

# 生产部署
vercel --prod
```

## 环境变量配置

在 Vercel 项目设置中配置：

- **必需变量**：无（当前版本无需额外配置）
- **可选变量**：
  - `PYTHON_VERSION`: `3.9` （已在 vercel.json 中配置）

## 部署检查清单

### 1. 文件结构确认

```
✓ api/upload.py
✓ api/analyze.py
✓ checker/ 模块
✓ config/rules_gbt14665.yaml
✓ frontend/ 目录
✓ requirements.txt
✓ vercel.json
```

### 2. 依赖检查

前端依赖：
```bash
cd frontend
npm install
npm run build  # 确保构建成功
```

Python 依赖：
```bash
pip install -r requirements.txt  # 确保所有依赖可安装
```

### 3. 本地测试

```bash
# 使用 Vercel CLI 本地测试
vercel dev
```

访问 http://localhost:3000 测试：
- ✓ 文件上传功能
- ✓ DXF 解析功能
- ✓ 报告生成功能
- ✓ 报告导出功能

### 4. 核心功能测试

```bash
python test_checker.py
```

确保所有测试通过。

## 部署后验证

### 1. 基本功能测试

1. 访问你的 Vercel 域名（如：`https://your-app.vercel.app`）
2. 上传一个测试 DXF 文件（建议 < 5MB）
3. 等待分析完成
4. 检查报告页面显示是否正常
5. 测试报告复制和下载功能

### 2. API 端点测试

使用 curl 或 Postman 测试：

```bash
# 测试上传 API
curl -X POST https://your-app.vercel.app/api/upload \
  -F "file=@test.dxf"

# 测试分析 API
curl -X POST https://your-app.vercel.app/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"file_id": "your-file-id", "standard": "GB/T 14665-2012"}'
```

### 3. 性能验证

- **响应时间**：首页加载 < 2s
- **文件上传**：1MB 文件 < 5s
- **文件分析**：标准 DXF 文件 < 30s
- **报告加载**：< 1s

## 常见问题

### Q1: Python 依赖安装失败

**解决方案**：
- 检查 `requirements.txt` 格式
- 确保使用兼容的版本号
- 查看 Vercel 构建日志

### Q2: API 端点 404 错误

**解决方案**：
- 检查 `vercel.json` 中的 `functions` 配置
- 确保 `api/` 目录结构正确
- 重新部署项目

### Q3: 文件上传后分析失败

**解决方案**：
- 检查文件大小是否超过 10MB
- 确认文件格式为 DXF
- 查看 Serverless Function 日志

### Q4: Serverless Function 超时

**解决方案**：
- 在 `vercel.json` 中增加 `maxDuration`（Pro 计划）
- 优化解析和检查逻辑
- 考虑使用后台任务队列

## 性能优化建议

### 1. 前端优化

- 启用 Next.js 静态优化
- 使用图片优化（Next.js Image）
- 实现代码分割

### 2. 后端优化

- 缓存规则配置文件
- 优化 DXF 解析逻辑
- 使用流式处理大文件

### 3. Vercel 配置优化

```json
{
  "functions": {
    "api/**/*.py": {
      "maxDuration": 60,
      "memory": 1024
    }
  },
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=0, must-revalidate"
        }
      ]
    }
  ]
}
```

## 监控和日志

### Vercel Analytics

在 Vercel Dashboard 中启用：
- **Analytics**：监控页面性能
- **Speed Insights**：追踪加载速度
- **Log Drain**：导出日志到外部服务

### 错误追踪

推荐集成：
- **Sentry**：前端和 API 错误追踪
- **LogRocket**：用户会话回放

## 扩展部署

### 自定义域名

1. 在 Vercel 项目设置中添加域名
2. 配置 DNS CNAME 记录
3. 等待 SSL 证书自动配置

### 环境分离

- **Production**：主分支自动部署
- **Preview**：PR 自动生成预览环境
- **Development**：本地 `vercel dev`

## 回滚策略

如果部署出现问题：

1. 在 Vercel Dashboard 找到之前的部署
2. 点击 "..." 菜单
3. 选择 "Promote to Production"

或使用 CLI：

```bash
vercel rollback
```

## 支持和帮助

- **Vercel 文档**：https://vercel.com/docs
- **Next.js 文档**：https://nextjs.org/docs
- **项目 Issues**：https://github.com/your-repo/issues

---

部署完成后，记得在 README.md 中更新实际的部署 URL！
