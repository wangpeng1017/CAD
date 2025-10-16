# Vercel 部署指南

## 项目概述

这是一个CAD合规检查系统，由Next.js前端和Python FastAPI后端组成。

## Vercel部署配置

### 1. 项目结构
```
CAD/
├── frontend/          # Next.js 前端应用
│   ├── app/          # App Router
│   ├── components/   # React组件
│   └── public/       # 静态资源
├── backend/          # Python FastAPI后端
└── vercel.json       # Vercel配置文件
```

### 2. Vercel项目设置

#### 连接Git仓库
1. 登录 [Vercel](https://vercel.com)
2. 点击 "Add New Project"
3. 选择 GitHub 仓库: `wangpeng1017/CAD`
4. 导入项目

#### 项目配置
在Vercel项目设置中配置：

**Framework Preset**: Next.js

**Root Directory**: `frontend`

**Build Command**: `npm run build`

**Output Directory**: `.next`

**Install Command**: `npm install`

### 3. 环境变量配置

在 Vercel 项目设置 → Environment Variables 中添加：

```bash
# 后端API地址
BACKEND_URL=http://103.109.20.169:10437

# 前端公开API路径
NEXT_PUBLIC_API_URL=/api/v1
```

### 4. 代码调整说明

#### 移除 standalone 模式
Vercel 不需要 Next.js 的 standalone 输出模式，已在 `next.config.ts` 中注释掉：

```typescript
// output: 'standalone',  // Vercel 部署不需要
```

#### 移除 Turbopack
Vercel 构建环境可能不支持 `--turbopack`，已从 `package.json` 中移除：

```json
{
  "scripts": {
    "dev": "next dev",           // 移除 --turbopack
    "build": "next build"        // 移除 --turbopack
  }
}
```

### 5. API路由代理

前端通过 Next.js API Routes 代理后端请求，避免CORS问题：

- `/api/v1/upload` → 后端上传接口
- `/api/v1/analyze` → 后端分析接口

### 6. 部署流程

#### 自动部署
推送代码到 `main` 分支会自动触发 Vercel 部署：

```bash
git add .
git commit -m "适配Vercel部署"
git push origin main
```

#### 手动部署
在 Vercel Dashboard 中点击 "Redeploy" 按钮。

### 7. 验证部署

部署完成后访问：
- Vercel域名: `https://cad-*.vercel.app`
- 自定义域名（如已配置）

测试功能：
1. 访问首页
2. 上传DXF文件
3. 查看分析结果

### 8. 常见问题

#### Q: 构建失败，提示 TypeScript 错误
A: 已在 `next.config.ts` 中配置 `ignoreBuildErrors: true`

#### Q: 上传文件后报错
A: 检查环境变量 `BACKEND_URL` 是否正确配置

#### Q: API请求跨域错误
A: 使用 `/api/v1/*` 路径，通过 Next.js API Routes 代理

#### Q: 页面加载缓慢
A: Vercel 免费套餐有冷启动时间，升级到 Pro 可改善

### 9. 生产环境优化

#### 性能优化
- 启用 Vercel Edge Network CDN
- 配置图片优化（如需要）
- 启用 ISR/SSG（如适用）

#### 监控
- 在 Vercel Analytics 中查看性能指标
- 配置 Error Tracking（Sentry等）

#### 安全
- 配置环境变量为 Production 专用
- 启用 Vercel 防火墙规则
- 定期更新依赖包

### 10. 本地开发

```bash
# 安装依赖
cd frontend
npm install

# 启动开发服务器
npm run dev

# 访问
open http://localhost:3000
```

### 11. 相关链接

- GitHub仓库: https://github.com/wangpeng1017/CAD
- Vercel项目: https://vercel.com/wangpeng10170414-1653s-projects/cad
- 后端API: http://103.109.20.169:10437

### 12. 支持的功能

- ✅ DXF文件上传
- ✅ 合规性检查
- ✅ 检查报告生成
- ✅ 响应式设计
- ✅ 暗色模式支持

### 13. 待优化项

- [ ] 添加后端Serverless部署（Vercel Functions或Railway）
- [ ] 配置自定义域名
- [ ] 添加用户认证
- [ ] 配置数据库持久化
- [ ] 添加文件存储服务（S3/Cloudinary）
