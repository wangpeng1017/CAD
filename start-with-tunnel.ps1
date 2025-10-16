# Cloudflare Tunnel 启动脚本

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "CAD Checker with Cloudflare Tunnel" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# 检查.env文件是否存在
if (-not (Test-Path ".env")) {
    Write-Host "❌ 错误: .env 文件不存在!" -ForegroundColor Red
    Write-Host "请先创建 .env 文件并配置 CLOUDFLARE_TUNNEL_TOKEN" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "参考 CLOUDFLARE_TUNNEL_SETUP.md 进行配置" -ForegroundColor Yellow
    exit 1
}

# 检查token是否配置
$envContent = Get-Content ".env" -Raw
if ($envContent -match "your_tunnel_token_here") {
    Write-Host "⚠️  警告: 请先配置Cloudflare Tunnel Token!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "步骤:" -ForegroundColor Cyan
    Write-Host "1. 访问 https://one.dash.cloudflare.com/" -ForegroundColor White
    Write-Host "2. 创建一个新的Tunnel" -ForegroundColor White
    Write-Host "3. 复制生成的token" -ForegroundColor White
    Write-Host "4. 编辑 .env 文件，替换 CLOUDFLARE_TUNNEL_TOKEN 的值" -ForegroundColor White
    Write-Host ""
    $continue = Read-Host "是否继续启动? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 0
    }
}

Write-Host "🚀 启动服务..." -ForegroundColor Green
docker-compose up -d

Write-Host ""
Write-Host "✅ 服务已启动!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 查看服务状态:" -ForegroundColor Cyan
docker-compose ps

Write-Host ""
Write-Host "📝 有用的命令:" -ForegroundColor Cyan
Write-Host "  查看cloudflared日志: docker logs cad-cloudflared -f" -ForegroundColor White
Write-Host "  查看所有日志:        docker-compose logs -f" -ForegroundColor White
Write-Host "  停止服务:            docker-compose down" -ForegroundColor White
Write-Host ""
Write-Host "🌐 配置完成后访问你的域名即可使用!" -ForegroundColor Green
Write-Host "   详细配置步骤请查看: CLOUDFLARE_TUNNEL_SETUP.md" -ForegroundColor Yellow
