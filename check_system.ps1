# CAD 规范符合性检查器 - 系统健康检查脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CAD 系统健康检查" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 检查后端服务
Write-Host "1. 检查后端服务..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ 后端运行正常 (端口 8000)" -ForegroundColor Green
        Write-Host "   响应: $($response.Content)" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ❌ 后端未运行或无法访问" -ForegroundColor Red
    Write-Host "   错误: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "   解决方案:" -ForegroundColor Yellow
    Write-Host "   cd backend" -ForegroundColor White
    Write-Host "   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
}

Write-Host ""

# 2. 检查前端服务
Write-Host "2. 检查前端服务..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ 前端运行正常 (端口 3000)" -ForegroundColor Green
    }
} catch {
    Write-Host "   ❌ 前端未运行或无法访问" -ForegroundColor Red
    Write-Host "   错误: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "   解决方案:" -ForegroundColor Yellow
    Write-Host "   cd frontend" -ForegroundColor White
    Write-Host "   npm run dev" -ForegroundColor White
}

Write-Host ""

# 3. 检查端口占用
Write-Host "3. 检查端口占用..." -ForegroundColor Yellow

# 检查 8000 端口
$port8000 = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($port8000) {
    Write-Host "   ✅ 端口 8000 (后端) 正在监听" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  端口 8000 (后端) 未监听" -ForegroundColor Yellow
}

# 检查 3000 端口
$port3000 = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue
if ($port3000) {
    Write-Host "   ✅ 端口 3000 (前端) 正在监听" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  端口 3000 (前端) 未监听" -ForegroundColor Yellow
}

Write-Host ""

# 4. 检查进程
Write-Host "4. 检查进程..." -ForegroundColor Yellow

$pythonProcesses = Get-Process -Name python -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    Write-Host "   ✅ Python 进程运行中: $($pythonProcesses.Count) 个" -ForegroundColor Green
} else {
    Write-Host "   ❌ 未找到 Python 进程" -ForegroundColor Red
}

$nodeProcesses = Get-Process -Name node -ErrorAction SilentlyContinue
if ($nodeProcesses) {
    Write-Host "   ✅ Node 进程运行中: $($nodeProcesses.Count) 个" -ForegroundColor Green
} else {
    Write-Host "   ❌ 未找到 Node 进程" -ForegroundColor Red
}

Write-Host ""

# 5. 测试 API 端点
Write-Host "5. 测试 API 端点..." -ForegroundColor Yellow

# 测试根路径
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/" -UseBasicParsing -TimeoutSec 5
    $json = $response.Content | ConvertFrom-Json
    Write-Host "   ✅ API 根路径: $($json.service) v$($json.version)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ API 根路径访问失败" -ForegroundColor Red
}

# 测试 API 文档
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -UseBasicParsing -TimeoutSec 5
    Write-Host "   ✅ API 文档可访问: http://localhost:8000/docs" -ForegroundColor Green
} catch {
    Write-Host "   ❌ API 文档访问失败" -ForegroundColor Red
}

Write-Host ""

# 6. 检查文件结构
Write-Host "6. 检查关键文件..." -ForegroundColor Yellow

$files = @(
    "backend\app\main.py",
    "backend\requirements.txt",
    "backend\app\config.py",
    "frontend\package.json",
    "frontend\app\page.tsx"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "   ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $file (缺失)" -ForegroundColor Red
    }
}

Write-Host ""

# 7. 总结
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  系统状态总结" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 判断系统是否正常
$backendOk = $false
$frontendOk = $false

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 3
    $backendOk = ($response.StatusCode -eq 200)
} catch {}

try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 3
    $frontendOk = ($response.StatusCode -eq 200)
} catch {}

Write-Host ""
if ($backendOk -and $frontendOk) {
    Write-Host "✅ 系统运行正常！" -ForegroundColor Green
    Write-Host ""
    Write-Host "访问地址:" -ForegroundColor Cyan
    Write-Host "  - 前端应用: http://localhost:3000" -ForegroundColor White
    Write-Host "  - 后端 API: http://localhost:8000" -ForegroundColor White
    Write-Host "  - API 文档: http://localhost:8000/docs" -ForegroundColor White
} elseif ($backendOk) {
    Write-Host "⚠️  后端正常，但前端可能有问题" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "尝试重启前端:" -ForegroundColor Yellow
    Write-Host "  cd frontend" -ForegroundColor White
    Write-Host "  npm run dev" -ForegroundColor White
} elseif ($frontendOk) {
    Write-Host "⚠️  前端正常，但后端可能有问题" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "尝试重启后端:" -ForegroundColor Yellow
    Write-Host "  cd backend" -ForegroundColor White
    Write-Host "  python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
} else {
    Write-Host "❌ 系统未正常运行" -ForegroundColor Red
    Write-Host ""
    Write-Host "使用启动脚本重启:" -ForegroundColor Yellow
    Write-Host "  .\start.ps1" -ForegroundColor White
}

Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
