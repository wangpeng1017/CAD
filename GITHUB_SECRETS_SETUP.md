# GitHub Secrets 配置指南

## 📌 当前状态

✅ 代码已成功推送到 GitHub  
✅ GitHub Actions 工作流已就绪  
❌ 缺少 Docker Hub 认证信息（导致构建失败）

---

## 🔐 步骤 1：创建 Docker Hub 账号

1. **访问** [Docker Hub](https://hub.docker.com/)
2. **注册账号**（如果还没有）
3. **登录**

---

## 🔑 步骤 2：创建 Docker Hub Access Token

1. 登录 Docker Hub 后，点击右上角头像
2. 选择 **Account Settings**
3. 进入左侧菜单的 **Security**
4. 点击 **New Access Token**
5. 配置：
   - **Description**: `leaflow-cad-deployment`
   - **Access permissions**: `Read, Write, Delete`
6. 点击 **Generate**
7. **⚠️ 重要**：立即复制生成的 token（只显示一次！）

示例 token 格式：`dckr_pat_xxxxxxxxxxxxxxxxxxxxxx`

---

## 🔧 步骤 3：配置 GitHub Secrets

### 方法 A：通过网页配置（推荐）

1. **访问仓库设置页面**：
   ```
   https://github.com/wangpeng1017/CAD/settings/secrets/actions
   ```

2. **添加第一个 Secret**：
   - 点击 **New repository secret**
   - **Name**: `DOCKER_USERNAME`
   - **Secret**: 您的 Docker Hub 用户名
   - 点击 **Add secret**

3. **添加第二个 Secret**：
   - 再次点击 **New repository secret**
   - **Name**: `DOCKER_PASSWORD`
   - **Secret**: 刚才复制的 Access Token
   - 点击 **Add secret**

### 方法 B：通过 GitHub CLI（可选）

```powershell
# 安装 GitHub CLI: https://cli.github.com/

# 设置 Secrets
gh secret set DOCKER_USERNAME --body "你的Docker Hub用户名"
gh secret set DOCKER_PASSWORD --body "你的Access Token"
```

---

## ▶️ 步骤 4：触发构建

配置完 Secrets 后，有两种方式触发构建：

### 方式 A：重新运行失败的任务

1. 访问 [Actions 页面](https://github.com/wangpeng1017/CAD/actions)
2. 点击失败的工作流
3. 点击 **Re-run jobs** → **Re-run all jobs**

### 方式 B：推送新代码

```powershell
# 任何推送都会触发
git commit --allow-empty -m "Trigger build"
git push
```

---

## ✅ 步骤 5：验证构建

1. **查看构建状态**：
   - 访问 https://github.com/wangpeng1017/CAD/actions
   - 等待工作流完成（约 5-10 分钟）

2. **构建成功后，您的Docker镜像地址将是**：
   ```
   你的用户名/cad-backend:latest
   你的用户名/cad-frontend:latest
   ```

3. **验证镜像已推送**：
   - 访问 https://hub.docker.com/repositories/你的用户名
   - 查看是否有 `cad-backend` 和 `cad-frontend` 镜像

---

## 🚀 步骤 6：在 Leaflow 部署

构建成功后，按以下步骤部署：

### 1. 访问 Leaflow 部署清单页面

https://leaflow.net/apply

### 2. 复制并修改部署配置

使用 `k8s/` 文件夹中的配置文件，替换以下内容：

```yaml
# 在所有配置中，将以下内容替换：
${DOCKER_USERNAME}  →  你的Docker Hub用户名
```

完整文件路径：
- `E:\trae\CAD\k8s\backend-deployment.yml`
- `E:\trae\CAD\k8s\frontend-deployment.yml`
- `E:\trae\CAD\k8s\ingress.yml`

### 3. 粘贴到 Leaflow

1. 打开各个 YAML 文件
2. 复制全部内容
3. 粘贴到 Leaflow 的"部署清单"编辑器
4. 点击"应用/更新"

---

## 📊 完整部署流程图

```
1. 配置 Docker Hub Secrets
   ↓
2. GitHub Actions 自动构建镜像
   ↓
3. 镜像推送到 Docker Hub
   ↓
4. 在 Leaflow 使用 K8s 配置部署
   ↓
5. 访问您的应用！
```

---

## ❓ 常见问题

### Q1: Secret 配置错误怎么办？
**A**: 在 GitHub Secrets 页面删除旧的 Secret，重新添加正确的值。

### Q2: 构建超时怎么办？
**A**: 这是正常的，Docker 镜像构建需要时间。如果超过 1 小时，检查 Actions 日志。

### Q3: 如何查看构建日志？
**A**: 访问 Actions → 点击工作流 → 点击具体的 job → 查看详细步骤。

### Q4: 镜像太大怎么办？
**A**: 
- 优化 Dockerfile（使用多阶段构建）
- 清理不必要的依赖
- 使用 `.dockerignore` 排除大文件

### Q5: 如何更新部署？
**A**: 
1. 修改代码并推送到 GitHub
2. GitHub Actions 自动构建新镜像
3. 在 Leaflow 中重启 Deployment 或更新镜像标签

---

## 🎯 下一步

配置完成后：

1. ✅ 确认 GitHub Actions 构建成功
2. ✅ 确认镜像已推送到 Docker Hub
3. ✅ 在 Leaflow 部署应用
4. ✅ 访问 Leaflow 分配的域名测试

---

## 📞 需要帮助？

如遇问题：
1. 查看 [LEAFLOW_DEPLOY.md](./LEAFLOW_DEPLOY.md) 完整部署文档
2. 查看 GitHub Actions 日志
3. 查看 Leaflow Pod 日志
4. 提交 GitHub Issue

---

**祝部署顺利！** 🎉
