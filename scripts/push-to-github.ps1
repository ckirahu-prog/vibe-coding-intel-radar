# GitHub 推送脚本（完成 gh 登录后运行）

# 1. 若尚未登录 GitHub CLI，先在终端运行：
#    gh auth login
#    选择：GitHub.com → HTTPS → Login with a web browser

param(
    [string]$RepoName = "vibe-coding-intel-radar"
)

$git = "C:\Program Files\Git\cmd\git.exe"
$gh = "C:\Program Files\GitHub CLI\gh.exe"

Write-Host "Checking GitHub auth..."
& $gh auth status
if ($LASTEXITCODE -ne 0) {
    Write-Host "Please run: gh auth login" -ForegroundColor Yellow
    exit 1
}

Write-Host "Creating GitHub repo: $RepoName ..."
& $gh repo create $RepoName --public --source=. --remote=origin --push --description "AI game dev & Vibe Coding intel radar"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Done! Repo URL:" -ForegroundColor Green
    & $gh repo view --web
} else {
    Write-Host "If repo already exists, try:" -ForegroundColor Yellow
    Write-Host "  gh repo create $RepoName --public"
    Write-Host "  git remote add origin https://github.com/YOUR_USER/$RepoName.git"
    Write-Host "  git push -u origin main"
}
