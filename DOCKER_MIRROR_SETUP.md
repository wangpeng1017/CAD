# Docker 镜像加速配置

## 问题说明
当前Docker无法从Docker Hub下载镜像，显示EOF错误。这通常是因为：
1. 网络连接问题
2. Docker Hub访问受限
3. 需要配置镜像加速器

## 解决方案：配置国内镜像加速

### 方法1: 通过Docker Desktop GUI配置（推荐）

1. **打开Docker Desktop**
2. **点击右上角设置图标 (齿轮)**
3. **选择 "Docker Engine"**
4. **在JSON配置中添加镜像源**，修改为：

```json
{
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "experimental": false,
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://mirror.ccs.tencentyun.com"
  ]
}
```

5. **点击 "Apply & Restart"** 按钮
6. **等待Docker Desktop重启完成**（约30秒）

### 方法2: 手动编辑配置文件

如果GUI方式不可行，可以直接编辑配置文件：

**配置文件位置**:
```
C:\Users\你的用户名\.docker\daemon.json
```

**配置内容**:
```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://mirror.ccs.tencentyun.com"
  ]
}
```

保存后，重启Docker Desktop。

### 方法3: 使用其他国内镜像源

可用的国内镜像源（按推荐顺序）：

```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://mirror.ccs.tencentyun.com",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
```

## 配置完成后的验证

1. **重启Docker Desktop**
2. **在PowerShell中执行**:

```powershell
# 进入项目目录
cd E:\trae\CAD

# 测试拉取镜像
docker pull cloudflare/cloudflared:latest

# 如果成功，启动所有服务
docker compose up -d
```

## 如果镜像加速仍然无法工作

### 备选方案1: 使用本地代理

如果你有VPN或代理，可以配置Docker使用代理：

1. 打开Docker Desktop设置
2. 选择 "Resources" → "Proxies"
3. 勾选 "Manual proxy configuration"
4. 配置你的代理地址

### 备选方案2: 手动下载并导入镜像

如果网络实在不行，可以在其他网络环境下载镜像：

```powershell
# 在有网络的环境下载
docker pull cloudflare/cloudflared:latest
docker pull node:18-alpine
docker pull python:3.11-slim

# 导出镜像
docker save cloudflare/cloudflared:latest -o cloudflared.tar
docker save node:18-alpine -o node.tar
docker save python:3.11-slim -o python.tar

# 在目标机器上导入
docker load -i cloudflared.tar
docker load -i node.tar
docker load -i python.tar
```

## 重新启动服务

配置完成后：

```powershell
# 清理旧的失败容器（如果有）
docker compose down

# 重新构建并启动
docker compose up -d --build

# 查看状态
docker compose ps

# 查看日志
docker compose logs -f
```

## 常见问题

### Q: 镜像加速配置后还是慢？
A: 可以尝试更换其他镜像源，或者检查本地网络连接。

### Q: EOF错误持续出现？
A: 可能是防火墙或公司网络策略，尝试使用代理或咨询网络管理员。

### Q: 无法访问任何镜像源？
A: 考虑使用VPN，或在其他网络环境下预先下载镜像。
