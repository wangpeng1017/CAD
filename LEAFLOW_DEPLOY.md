# CAD 项目 Leaflow 部署指南

本指南将帮助您将 CAD 规范符合性检查器部署到 Leaflow 平台。

## 📋 部署概览

- **前端**: Next.js 应用 (端口 3000)
- **后端**: FastAPI 应用 (端口 8000)
- **部署方式**: GitHub Actions 自动构建 → Docker Hub → Leaflow Kubernetes

---

## 🚀 快速开始（5 步完成）

### 步骤 1：准备 Docker Hub 账号

1. 访问 [Docker Hub](https://hub.docker.com/) 注册账号（如果还没有）
2. 创建 Access Token：
   - 登录 Docker Hub
   - 点击右上角头像 → Account Settings
   - Security → New Access Token
   - 命名为 `leaflow-cad` 并复制生成的 token（只显示一次！）

### 步骤 2：配置 GitHub Secrets

1. 访问您的 GitHub 仓库：https://github.com/wangpeng1017/CAD
2. 进入 Settings → Secrets and variables → Actions
3. 点击 "New repository secret"，添加以下两个密钥：

   **DOCKER_USERNAME**
   ```
   你的 Docker Hub 用户名
   ```

   **DOCKER_PASSWORD**
   ```
   刚才创建的 Access Token
   ```

### 步骤 3：推送代码触发构建

```powershell
# 在当前目录执行
git add .
git commit -m "Add Leaflow deployment configuration"
git push origin main
```

推送后，GitHub Actions 会自动：
1. 构建前端和后端 Docker 镜像
2. 推送到 Docker Hub
3. 镜像地址格式：`你的用户名/cad-backend:latest` 和 `你的用户名/cad-frontend:latest`

**查看构建进度**：
- 访问 https://github.com/wangpeng1017/CAD/actions
- 查看 "Build and Push Docker Images" 工作流

### 步骤 4：在 Leaflow 部署

#### 方式 A：使用部署清单（推荐）

1. 打开 [Leaflow 部署清单](https://leaflow.net/apply)

2. 复制以下完整 YAML 配置到编辑器（**替换 `YOUR_DOCKER_USERNAME`**）：

```yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cad-backend
  labels:
    app: cad-backend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cad-backend
  template:
    metadata:
      labels:
        app: cad-backend
    spec:
      containers:
      - name: backend
        image: YOUR_DOCKER_USERNAME/cad-backend:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: DEBUG
          value: "false"
        - name: HOST
          value: "0.0.0.0"
        - name: PORT
          value: "8000"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: cad-backend
  labels:
    app: cad-backend
spec:
  type: ClusterIP
  ports:
  - port: 8000
    targetPort: 8000
    protocol: TCP
    name: http
  selector:
    app: cad-backend
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cad-frontend
  labels:
    app: cad-frontend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cad-frontend
  template:
    metadata:
      labels:
        app: cad-frontend
    spec:
      containers:
      - name: frontend
        image: YOUR_DOCKER_USERNAME/cad-frontend:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 3000
          name: http
        env:
        - name: NEXT_PUBLIC_API_URL
          value: "http://cad-backend:8000"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: cad-frontend
  labels:
    app: cad-frontend
spec:
  type: ClusterIP
  ports:
  - port: 3000
    targetPort: 3000
    protocol: TCP
    name: http
  selector:
    app: cad-frontend
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: cad-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - cad.leaflow.net
    secretName: cad-tls
  rules:
  - host: cad.leaflow.net
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: cad-backend
            port:
              number: 8000
      - path: /docs
        pathType: Prefix
        backend:
          service:
            name: cad-backend
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: cad-frontend
            port:
              number: 3000
```

3. 点击 "应用/更新" 按钮

#### 方式 B：手动创建（分步操作）

1. **创建后端应用**
   - 访问 [创建应用](https://leaflow.net/applications/create)
   - 名称：`cad-backend`
   - 镜像：`你的用户名/cad-backend:latest`
   - 端口：`8000`
   - CPU: 500m, 内存: 512Mi

2. **创建前端应用**
   - 名称：`cad-frontend`
   - 镜像：`你的用户名/cad-frontend:latest`
   - 端口：`3000`
   - 环境变量：`NEXT_PUBLIC_API_URL=http://cad-backend:8000`
   - CPU: 500m, 内存: 512Mi

3. **创建网站（Ingress）**
   - 访问 [网站管理](https://leaflow.net/ingresses)
   - 添加规则：
     - `/api` → cad-backend:8000
     - `/docs` → cad-backend:8000
     - `/` → cad-frontend:3000

### 步骤 5：验证部署

1. **查看部署状态**
   - 访问 [容器组](https://leaflow.net/pods)
   - 确认 `cad-backend` 和 `cad-frontend` 状态为 "运行中"

2. **获取访问地址**
   - 访问 [网站管理](https://leaflow.net/ingresses)
   - 查看 Ingress 分配的域名

3. **测试访问**
   - 前端：https://你的域名/
   - 后端 API 文档：https://你的域名/docs

---

## 🔧 常见问题

### Q1: GitHub Actions 构建失败？
**检查**：
- GitHub Secrets 是否正确配置
- Docker Hub 用户名和 Token 是否有效
- 查看 Actions 日志获取详细错误信息

### Q2: 容器启动失败？
**检查**：
- 镜像是否成功推送到 Docker Hub（访问 hub.docker.com）
- 在 Leaflow 中查看 Pod 日志
- 检查资源限制是否足够

### Q3: 无法访问网站？
**检查**：
- Ingress 规则是否正确配置
- 域名 DNS 是否正确解析
- 查看 Service 是否正常运行

### Q4: 前端无法连接后端？
**检查**：
- 前端环境变量 `NEXT_PUBLIC_API_URL` 是否正确
- 后端服务名称是否为 `cad-backend`
- 两个服务是否在同一工作区

### Q5: 如何查看日志？
1. 访问 [容器组](https://leaflow.net/pods)
2. 点击对应的 Pod
3. 查看 "日志" 标签

---

## 📊 资源预估

**每月成本**（基于配置）：
- 后端：512Mi 内存 + 500m CPU
- 前端：512Mi 内存 + 500m CPU
- **总计**：约 1Gi 内存 + 1000m CPU

**建议优化**：
- 生产环境可以调整副本数实现高可用
- 根据实际使用调整资源限制
- 启用自动扩缩（HPA）应对流量波动

---

## 🔄 更新部署

修改代码后：

```powershell
git add .
git commit -m "Update features"
git push origin main
```

GitHub Actions 会自动构建新镜像，然后：

**方式 A：手动更新**
1. 在 Leaflow 应用管理中
2. 点击 "重启" 或 "更新镜像"

**方式 B：自动更新**
- 在 Deployment 配置中使用特定版本标签而非 `latest`
- 或使用 Webhook 自动触发更新

---

## 📚 相关文档

- [Leaflow 文档](https://docs.leaflow.net/)
- [Kubernetes 文档](https://kubernetes.io/docs/)
- [Docker Hub](https://hub.docker.com/)
- [GitHub Actions](https://docs.github.com/actions)

---

## 💡 提示

1. **使用特定版本标签**：生产环境建议使用 Git SHA 作为镜像标签，而非 `latest`
2. **配置持久化存储**：如果需要保存上传的文件，配置 PersistentVolumeClaim
3. **监控和告警**：使用 Leaflow 提供的监控功能追踪应用状态
4. **备份配置**：保存好 YAML 配置文件，便于快速恢复

---

## 🎉 完成！

按照以上步骤，您的 CAD 项目将成功部署到 Leaflow 平台！

如有问题，请通过 [Leaflow 工单系统](https://leaflow.net/tickets) 获取支持。
