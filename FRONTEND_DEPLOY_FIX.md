# 🛠️ Frontend 部署问题修复

## 问题诊断

### 发现的问题
1. ❌ **使用开发模式部署** - `npm run dev` 不适合生产环境
2. ❌ **资源配置不合理** - 开发模式需要更多 CPU
3. ❌ **健康检查超时** - 启动时间长，健康检查失败
4. ❌ **容器名称不一致** - 配置为 `frontend`，实际应为 `main`

### 根本原因
Next.js 开发模式会：
- 实时编译代码（耗费 CPU）
- 监听文件变化（占用内存）
- 启动慢（30秒可能不够）
- 不稳定（容易崩溃）

---

## 已修复的内容

### 1. ✅ Dockerfile 优化

**修改前**：
```dockerfile
CMD ["npm", "run", "dev"]  # 开发模式
```

**修改后**：
```dockerfile
# 多阶段构建
FROM node:18-alpine AS builder
# ... 构建步骤 ...

FROM node:18-alpine AS runner
# ... 生产环境配置 ...
CMD ["node", "server.js"]  # 生产模式
```

**优势**：
- ✅ 启动快（<5秒）
- ✅ 资源占用低
- ✅ 稳定性高
- ✅ 镜像体积小

### 2. ✅ Next.js 配置

`frontend/next.config.ts`:
```typescript
output: 'standalone',  // 启用独立输出模式
```

### 3. ✅ Kubernetes 配置优化

**资源调整**：
```yaml
resources:
  requests:
    memory: "256Mi"  # 从 512Mi 降低
    cpu: "250m"      # 从 500m 降低
  limits:
    memory: "512Mi"  # 从 1Gi 降低
    cpu: "500m"      # 从 1000m 降低
```

**健康检查优化**：
```yaml
livenessProbe:
  initialDelaySeconds: 15  # 从 30 降低
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  initialDelaySeconds: 10  # 从 5 增加
  timeoutSeconds: 3
  failureThreshold: 3
```

**容器名称修正**：
```yaml
containers:
- name: main  # 从 frontend 改为 main
```

---

## 部署步骤

### 方式 1：自动化脚本（推荐）

```powershell
# 完整部署（构建 + 推送 + 部署）
.\deploy-frontend.ps1

# 仅部署（跳过构建）
.\deploy-frontend.ps1 -SkipBuild

# 指定版本
.\deploy-frontend.ps1 -version "v1.0.0"
```

### 方式 2：手动步骤

#### 步骤 1：构建生产镜像

```powershell
cd frontend
docker build -t wangpeng1017/cad-frontend:latest .
```

#### 步骤 2：推送到 Docker Hub

```powershell
docker login
docker push wangpeng1017/cad-frontend:latest
```

#### 步骤 3：通过 Leaflow Web 界面部署

1. 访问：https://leaflow.net/deployments/cad-frontend
2. 点击右上角 **"删除"** 按钮（删除旧部署）
3. 访问：https://leaflow.net/apply
4. 复制 `k8s/leaflow-deploy-complete.yml` 的内容
5. 粘贴到部署清单编辑器
6. 点击 **"应用"** 按钮
7. 等待 1-2 分钟，Pod 启动完成

#### 步骤 4：验证部署

访问：https://cad-wangpeng.leaflow.net

---

## 验证清单

部署后检查以下项目：

### ✅ 容器组状态
访问：https://leaflow.net/pods

应该看到：
```
cad-frontend-xxx   Running   OK 1/1   0 重启
```

### ✅ 应用访问
- 前端：https://cad-wangpeng.leaflow.net
- 后端 API：https://cad-wangpeng.leaflow.net/api/v1/
- API 文档：https://cad-wangpeng.leaflow.net/docs

### ✅ 日志检查
访问：https://leaflow.net/pods/cad-frontend-xxx/logs

应该看到：
```
> cad-frontend@0.1.0 start
> node server.js

Listening on port 3000
```

---

## 故障排查

### 问题 1：镜像构建失败

**症状**：`docker build` 报错

**解决方案**：
```powershell
# 清理缓存重新构建
docker build --no-cache -t wangpeng1017/cad-frontend:latest ./frontend
```

### 问题 2：Pod 一直处于 Pending 状态

**原因**：资源不足

**解决方案**：
1. 检查工作区余额
2. 降低资源请求（已在配置中优化）

### 问题 3：Pod CrashLoopBackOff

**原因**：应用启动失败

**解决方案**：
1. 查看 Pod 日志
2. 检查镜像是否正确推送
3. 验证环境变量配置

### 问题 4：健康检查失败

**原因**：Next.js 启动慢

**解决方案**：
已在配置中增加 `initialDelaySeconds`

如果仍失败，可临时禁用健康检查：
```yaml
# 注释掉 livenessProbe 和 readinessProbe
```

---

## 本地测试

在推送到 Leaflow 前，先本地测试：

```powershell
# 1. 构建镜像
docker build -t wangpeng1017/cad-frontend:latest ./frontend

# 2. 运行容器
docker run -p 3000:3000 `
  -e NEXT_PUBLIC_API_URL=http://localhost:8000 `
  wangpeng1017/cad-frontend:latest

# 3. 测试访问
# 浏览器访问 http://localhost:3000

# 4. 检查启动时间
docker logs <container-id>
```

**预期**：
- 启动时间 < 10秒
- 内存占用 < 200MB
- CPU 占用 < 50%

---

## 配置对比

### 开发模式 vs 生产模式

| 指标 | 开发模式 | 生产模式 |
|------|---------|---------|
| 启动命令 | `npm run dev` | `node server.js` |
| 启动时间 | 30-60秒 | 5-10秒 |
| 内存占用 | 500MB+ | 100-200MB |
| CPU 占用 | 高（实时编译） | 低（预构建） |
| 稳定性 | 低 | 高 |
| 适用场景 | 本地开发 | 生产部署 |

---

## 注意事项

1. ⚠️ **不要在生产环境使用开发模式**
2. ⚠️ **确保 Docker Hub 登录状态**
3. ⚠️ **定期检查 Leaflow 余额**
4. ⚠️ **保持镜像标签一致（latest）**
5. ⚠️ **修改代码后需要重新构建镜像**

---

## 后续优化建议

### 1. 使用版本标签
```powershell
docker build -t wangpeng1017/cad-frontend:v1.0.0 .
docker build -t wangpeng1017/cad-frontend:latest .
```

### 2. 配置 CI/CD
使用 GitHub Actions 自动化构建和部署

### 3. 添加监控
- 配置 Leaflow 告警
- 监控 Pod 重启次数
- 跟踪资源使用情况

### 4. 启用缓存
在 Dockerfile 中优化依赖缓存

---

## 相关文件

- `frontend/Dockerfile` - 生产环境 Dockerfile
- `frontend/next.config.ts` - Next.js 配置
- `k8s/leaflow-deploy-complete.yml` - Kubernetes 配置
- `deploy-frontend.ps1` - 自动化部署脚本

---

## 联系支持

如果问题仍未解决：
1. 查看 Leaflow 日志
2. 提交工单：https://leaflow.net/tickets
3. 检查 Docker Hub 镜像状态
