# CAD 规范符合性检查器 - 启动脚本

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  CAD 规范符合性检查器 - 启动中..." -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Python
Write-Host "检查 Python 环境..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 未找到 Python，请安装 Python 3.11+" -ForegroundColor Red
    exit 1
}

# 检查 Node.js
Write-Host "检查 Node.js 环境..." -ForegroundColor Yellow
node --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 未找到 Node.js，请安装 Node.js 18+" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "选择启动方式:" -ForegroundColor Green
Write-Host "1. 本地开发模式 (推荐)" -ForegroundColor White
Write-Host "2. Docker 模式" -ForegroundColor White
Write-Host ""

$choice = Read-Host "请输入选项 (1 或 2)"

if ($choice -eq "1") {
    Write-Host ""
    Write-Host "====== 本地开发模式 ======" -ForegroundColor Cyan
    
    # 启动后端
    Write-Host ""
    Write-Host "启动后端服务..." -ForegroundColor Yellow
    Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd backend; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    
    Start-Sleep -Seconds 3
    
    # 启动前端
    Write-Host "启动前端服务..." -ForegroundColor Yellow
    Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"
    
    Write-Host ""
    Write-Host "✓ 服务启动成功！" -ForegroundColor Green
    Write-Host ""
    Write-Host "访问地址:" -ForegroundColor Cyan
    Write-Host "  前端: http://localhost:3000" -ForegroundColor White
    Write-Host "  后端 API: http://localhost:8000" -ForegroundColor White
    Write-Host "  API 文档: http://localhost:8000/docs" -ForegroundColor White
    Write-Host ""
    Write-Host "按任意键退出..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    
} elseif ($choice -eq "2") {
    Write-Host ""
    Write-Host "====== Docker 模式 ======" -ForegroundColor Cyan
    
    # 检查 Docker
    docker --version
    if ($LASTEXITCODE -ne 0) {
        Write-Host "错误: 未找到 Docker，请安装 Docker Desktop" -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
    Write-Host "构建并启动 Docker 容器..." -ForegroundColor Yellow
    docker-compose up --build
    
} else {
    Write-Host "无效选项！" -ForegroundColor Red
    exit 1
}
