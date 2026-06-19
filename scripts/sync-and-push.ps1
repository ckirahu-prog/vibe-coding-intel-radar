# 一键同步到 GitHub（网络正常时在 Cursor 终端运行）

$git = "C:\Program Files\Git\cmd\git.exe"
Set-Location $PSScriptRoot\..

Write-Host "Fetching and rebasing on origin/main..." -ForegroundColor Cyan
& $git pull --rebase origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "Pull failed. Check network / VPN, then retry." -ForegroundColor Red
    exit 1
}

Write-Host "Pushing to origin/main..." -ForegroundColor Cyan
& $git push origin main
if ($LASTEXITCODE -eq 0) {
    Write-Host "Done! Now run Cursor Automation 'Run now' to regenerate beginner weekly report." -ForegroundColor Green
} else {
    Write-Host "Push failed." -ForegroundColor Red
    exit 1
}
