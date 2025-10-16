# 通过Cloudflare API创建Tunnel
# 无需下载MSI安装包

param(
    [Parameter(Mandatory=$true)]
    [string]$AccountId,
    
    [Parameter(Mandatory=$true)]
    [string]$ApiToken,
    
    [Parameter(Mandatory=$false)]
    [string]$TunnelName = "cad-checker-tunnel"
)

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Cloudflare Tunnel API 创建工具" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# API端点
$apiBase = "https://api.cloudflare.com/client/v4"
$headers = @{
    "Authorization" = "Bearer $ApiToken"
    "Content-Type" = "application/json"
}

try {
    Write-Host "📝 创建Tunnel: $TunnelName" -ForegroundColor Yellow
    
    # 创建Tunnel
    $createBody = @{
        name = $TunnelName
        tunnel_secret = [Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
    } | ConvertTo-Json
    
    $createResponse = Invoke-RestMethod -Uri "$apiBase/accounts/$AccountId/cfd_tunnel" `
        -Method Post `
        -Headers $headers `
        -Body $createBody
    
    if ($createResponse.success) {
        $tunnelId = $createResponse.result.id
        $tunnelToken = $createResponse.result.token
        
        Write-Host ""
        Write-Host "✅ Tunnel创建成功!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Tunnel ID: $tunnelId" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "🔑 请将以下Token保存到 .env 文件:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "CLOUDFLARE_TUNNEL_TOKEN=$tunnelToken" -ForegroundColor White
        Write-Host ""
        
        # 自动写入.env文件
        $envContent = Get-Content ".env" -Raw -ErrorAction SilentlyContinue
        if ($envContent) {
            $envContent = $envContent -replace "CLOUDFLARE_TUNNEL_TOKEN=.*", "CLOUDFLARE_TUNNEL_TOKEN=$tunnelToken"
            $envContent | Set-Content ".env" -NoNewline
            Write-Host "✅ Token已自动写入 .env 文件" -ForegroundColor Green
        } else {
            "CLOUDFLARE_TUNNEL_TOKEN=$tunnelToken" | Set-Content ".env"
            Write-Host "✅ 已创建 .env 文件并保存Token" -ForegroundColor Green
        }
        
        Write-Host ""
        Write-Host "📋 接下来请在Cloudflare控制台配置Public Hostname:" -ForegroundColor Cyan
        Write-Host "   1. 访问 https://one.dash.cloudflare.com/" -ForegroundColor White
        Write-Host "   2. Networks → Tunnels → 找到 $TunnelName" -ForegroundColor White
        Write-Host "   3. 点击 Configure → Public Hostname → Add" -ForegroundColor White
        Write-Host "   4. 配置域名指向 frontend:3000" -ForegroundColor White
        
    } else {
        Write-Host "❌ 创建失败: $($createResponse.errors)" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ 错误: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 提示: 请确保:" -ForegroundColor Yellow
    Write-Host "   1. Account ID正确" -ForegroundColor White
    Write-Host "   2. API Token有足够权限(需要Cloudflare Tunnel:Edit权限)" -ForegroundColor White
    Write-Host "   3. 网络连接正常" -ForegroundColor White
}

Write-Host ""
Write-Host "📚 如何获取Account ID和API Token:" -ForegroundColor Cyan
Write-Host "   Account ID: Cloudflare Dashboard右侧边栏" -ForegroundColor White
Write-Host "   API Token: My Profile → API Tokens → Create Token" -ForegroundColor White
Write-Host "              需要 'Cloudflare Tunnel' 权限" -ForegroundColor White
