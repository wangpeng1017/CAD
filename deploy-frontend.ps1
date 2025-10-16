# CAD Frontend 部署脚本
# 用于快速构建和部署前端到 Leaflow

param(
    [string]$version = "latest",
    [switch]$SkipBuild = $false
)

Write-Host "🚀 开始部署 cad-frontend..." -ForegroundColor Green
Write-Host ""

# 1. 构建镜像
if (-not $SkipBuild) {
    Write-Host "📦 构建 Docker 镜像..." -ForegroundColor Yellow
    
    Set-Location -Path "E:\trae\CAD\frontend"
    
    # 构建生产镜像
    docker build -t wangpeng1017/cad-frontend:$version .
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 镜像构建失败！" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ 镜像构建成功！" -ForegroundColor Green
    Write-Host ""
    
    # 2. 推送到 Docker Hub
    Write-Host "📤 推送镜像到 Docker Hub..." -ForegroundColor Yellow
    docker push wangpeng1017/cad-frontend:$version
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 镜像推送失败！请检查 Docker Hub 登录状态。" -ForegroundColor Red
        Write-Host "提示：运行 'docker login' 进行登录" -ForegroundColor Cyan
        exit 1
    }
    
    Write-Host "✅ 镜像推送成功！" -ForegroundColor Green
    Write-Host ""
}

# 3. 应用 Kubernetes 配置
Write-Host "☸️  应用 Kubernetes 配置..." -ForegroundColor Yellow

Set-Location -Path "E:\trae\CAD"

# 检查是否有 kubectl 配置
$kubectlTest = kubectl get pods 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  kubectl 未配置或无法连接到 Leaflow 集群" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "请手动执行以下步骤：" -ForegroundColor Cyan
    Write-Host "1. 访问 https://leaflow.net/deployments/cad-frontend" -ForegroundColor White
    Write-Host "2. 点击 '删除' 按钮删除旧部署" -ForegroundColor White
    Write-Host "3. 访问 https://leaflow.net/apply" -ForegroundColor White
    Write-Host "4. 粘贴 k8s/leaflow-deploy-complete.yml 的内容" -ForegroundColor White
    Write-Host "5. 点击 '应用' 按钮" -ForegroundColor White
    Write-Host ""
    Write-Host "或者配置 kubectl：" -ForegroundColor Cyan
    Write-Host "从 Leaflow 控制台下载 kubeconfig 并设置环境变量" -ForegroundColor White
    Write-Host '$env:KUBECONFIG = "path\to\kubeconfig.yaml"' -ForegroundColor White
    exit 0
}

# 删除旧部署（如果存在）
Write-Host "🗑️  删除旧部署..." -ForegroundColor Yellow
kubectl delete deployment cad-frontend 2>$null

Start-Sleep -Seconds 3

# 应用新配置
kubectl apply -f k8s/leaflow-deploy-complete.yml

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Kubernetes 配置应用失败！" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Kubernetes 配置已应用！" -ForegroundColor Green
Write-Host ""

# 4. 等待 Pod 就绪
Write-Host "⏳ 等待 Pod 启动..." -ForegroundColor Yellow
Write-Host "（可能需要 30-60 秒）" -ForegroundColor Gray
Write-Host ""

$maxWait = 120
$waited = 0
$ready = $false

while ($waited -lt $maxWait) {
    $pods = kubectl get pods -l app=cad-frontend -o json 2>$null | ConvertFrom-Json
    
    if ($pods.items.Count -gt 0) {
        $pod = $pods.items[0]
        $status = $pod.status.phase
        
        Write-Host "Pod 状态: $status" -ForegroundColor Cyan
        
        if ($status -eq "Running") {
            $conditions = $pod.status.conditions | Where-Object { $_.type -eq "Ready" }
            if ($conditions -and $conditions[0].status -eq "True") {
                $ready = $true
                break
            }
        }
        
        if ($status -eq "Failed" -or $status -eq "CrashLoopBackOff") {
            Write-Host "❌ Pod 启动失败！" -ForegroundColor Red
            Write-Host ""
            Write-Host "查看日志：" -ForegroundColor Yellow
            kubectl logs -l app=cad-frontend --tail=50
            exit 1
        }
    }
    
    Start-Sleep -Seconds 5
    $waited += 5
}

if ($ready) {
    Write-Host ""
    Write-Host "✅ 部署成功！" -ForegroundColor Green
    Write-Host ""
    Write-Host "访问地址：" -ForegroundColor Cyan
    Write-Host "https://cad-wangpeng.leaflow.net" -ForegroundColor White
    Write-Host ""
    Write-Host "检查状态：" -ForegroundColor Cyan
    kubectl get pods -l app=cad-frontend
} else {
    Write-Host ""
    Write-Host "⚠️  Pod 未在预期时间内就绪" -ForegroundColor Yellow
    Write-Host "请手动检查状态：" -ForegroundColor Cyan
    Write-Host "kubectl get pods -l app=cad-frontend" -ForegroundColor White
    Write-Host "kubectl logs -l app=cad-frontend" -ForegroundColor White
}
