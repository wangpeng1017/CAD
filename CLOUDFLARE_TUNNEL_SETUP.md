# Cloudflare Tunnel 配置指南

## 前置要求
1. 一个Cloudflare账号
2. 域名已托管到Cloudflare
3. Docker环境已安装

## 配置步骤

### 1. 登录Cloudflare Zero Trust

访问: https://one.dash.cloudflare.com/

### 2. 创建Tunnel

1. 进入 **Networks** > **Tunnels**
2. 点击 **Create a tunnel**
3. 选择 **Cloudflared** 类型
4. 输入tunnel名称，例如: `cad-checker-tunnel`
5. 选择环境: **Docker**
6. **复制生成的token** (非常重要!)

### 3. 配置环境变量

将复制的token填入 `.env` 文件:

```bash
CLOUDFLARE_TUNNEL_TOKEN=eyJhIjoixxxx...你的token...xxxx"
```

### 4. 配置Public Hostname (域名路由)

在Cloudflare Zero Trust的Tunnel配置中:

#### 前端服务路由
- **Subdomain**: `cad` (或你想要的子域名)
- **Domain**: 选择你的域名，例如: `yourdomain.com`
- **Type**: `HTTP`
- **URL**: `frontend:3000`

完整访问地址: `https://cad.yourdomain.com`

#### 后端API路由 (可选)
如果需要独立的API域名:
- **Subdomain**: `cad-api`
- **Domain**: `yourdomain.com`
- **Type**: `HTTP`
- **URL**: `backend:8000`

完整访问地址: `https://cad-api.yourdomain.com`

### 5. 启动服务

```bash
# 启动所有服务(包括cloudflared)
docker-compose up -d

# 查看cloudflared日志
docker logs cad-cloudflared -f

# 查看所有服务状态
docker-compose ps
```

### 6. 验证连接

1. 查看Cloudflare Zero Trust控制台，tunnel状态应显示为 **HEALTHY**
2. 访问配置的域名: `https://cad.yourdomain.com`
3. 检查cloudflared日志确认连接正常

## 服务架构

```
Internet
    ↓
Cloudflare Edge (全球CDN)
    ↓
Cloudflare Tunnel (加密隧道)
    ↓
cloudflared (Docker容器)
    ↓
    ├─→ frontend:3000 (Next.js前端)
    └─→ backend:8000 (FastAPI后端)
```

## 优势

✅ **无需公网IP**: 不需要端口转发或公网IP  
✅ **自动HTTPS**: Cloudflare自动提供SSL证书  
✅ **全球CDN**: 利用Cloudflare全球网络加速  
✅ **DDoS防护**: 免费的DDoS防护  
✅ **零信任安全**: 可配置访问策略和认证  

## 故障排查

### Tunnel连接失败
```bash
# 检查cloudflared日志
docker logs cad-cloudflared

# 常见问题:
# 1. Token错误 - 检查.env文件中的token是否正确
# 2. 网络问题 - 确认能访问Cloudflare服务
# 3. 服务未启动 - 确认frontend和backend容器运行正常
```

### 域名无法访问
1. 确认Tunnel状态为HEALTHY
2. 检查Public Hostname配置是否正确
3. 确认域名DNS已生效(可能需要几分钟)
4. 检查内部服务URL: `frontend:3000` 和 `backend:8000` 是否正确

### 修改配置后
```bash
# 重启cloudflared服务
docker-compose restart cloudflared

# 或重启所有服务
docker-compose restart
```

## 安全建议

1. **不要提交token**: 将 `.env` 添加到 `.gitignore`
2. **访问控制**: 在Cloudflare Zero Trust中配置访问策略
3. **定期轮换**: 定期更新tunnel token
4. **监控日志**: 定期检查访问日志和异常

## 参考链接

- [Cloudflare Tunnel文档](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [Zero Trust Dashboard](https://one.dash.cloudflare.com/)
