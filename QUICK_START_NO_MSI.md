# 快速开始 - 无需下载MSI

## 🎯 推荐方式: 网页直接创建(最简单)

### 步骤1: 网页创建Tunnel

1. 访问 https://one.dash.cloudflare.com/
2. 左侧菜单: **Networks** → **Tunnels**
3. 点击 **Create a tunnel**
4. 选择 **Cloudflared** 类型
5. 输入名称: `cad-checker`
6. 点击 **Save tunnel**

### 步骤2: 获取Token

在安装环境选择界面:

1. 选择 **Docker** 标签页
2. 你会看到类似下面的命令:
   ```bash
   docker run cloudflare/cloudflared:latest tunnel --no-autoupdate run --token eyJh...
   ```
3. **复制 `--token` 后面的整个token字符串**
4. **直接点击 "Next" 按钮,不用管MSI下载!**

### 步骤3: 保存Token

编辑项目中的 `.env` 文件:

```bash
CLOUDFLARE_TUNNEL_TOKEN=你复制的token
```

### 步骤4: 配置域名路由

在Public Hostname配置页面:

| 字段 | 值 |
|------|------|
| Subdomain | `cad` (或你想要的名称) |
| Domain | 选择你的域名 |
| Type | `HTTP` |
| URL | `frontend:3000` |

点击 **Save hostname**

### 步骤5: 启动服务

```powershell
# 在项目目录执行
.\start-with-tunnel.ps1

# 或者直接用docker-compose
docker-compose up -d
```

### 步骤6: 验证

1. 查看Tunnel状态:
   ```powershell
   docker logs cad-cloudflared -f
   ```
   
2. 在Cloudflare控制台检查Tunnel状态应为 **HEALTHY**

3. 访问你配置的域名: `https://cad.你的域名.com`

---

## 🔧 备选方式: API创建(高级用户)

如果你想通过API创建,可以使用我提供的脚本:

### 获取API凭据

1. **Account ID**: 
   - 登录Cloudflare Dashboard
   - 右侧边栏可以看到 Account ID

2. **API Token**:
   - 访问: https://dash.cloudflare.com/profile/api-tokens
   - 点击 **Create Token**
   - 使用 "Create Custom Token" 模板
   - 权限设置:
     - Account → Cloudflare Tunnel → Edit
   - 点击 **Continue to summary** → **Create Token**
   - **复制生成的Token**

### 运行脚本

```powershell
.\create-tunnel-via-api.ps1 -AccountId "你的AccountID" -ApiToken "你的APIToken"
```

脚本会自动:
- 创建Tunnel
- 生成Token
- 保存到 `.env` 文件

之后再去网页配置域名路由即可。

---

## ❓ 常见问题

### Q: 为什么不需要下载MSI?

A: MSI是Windows本地安装cloudflared客户端用的。我们使用Docker方式,cloudflared运行在容器中,不需要在Windows上安装。

### Q: Token在哪里?

A: 在网页创建Tunnel的"Install connector"步骤中,选择Docker标签页,命令中 `--token` 后面的就是。

### Q: 防火墙阻止怎么办?

A: 网页方式不需要下载任何文件,只需要复制Token。如果API方式也被阻止,可以:
1. 在其他网络环境下创建
2. 使用手机热点
3. 请IT部门临时开放cloudflare.com访问

### Q: 如何验证配置正确?

A: 
```powershell
# 查看cloudflared日志
docker logs cad-cloudflared -f

# 正常应该看到:
# "Connection established" 
# "Registered tunnel connection"
```

### Q: 域名无法访问?

A: 检查清单:
- [ ] Tunnel状态是否为HEALTHY
- [ ] Public Hostname是否配置正确
- [ ] 服务URL是否为 `frontend:3000` (不是localhost)
- [ ] DNS是否已生效(可能需要几分钟)

---

## 🎉 完成!

配置完成后,你可以通过 `https://你的域名` 访问应用,无需公网IP、端口映射或VPN!
