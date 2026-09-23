#!/usr/bin/env pwsh
<#
.SYNOPSIS
  install.ps1 - cai overstack tren may Windows KHONG dung khuon "tai ve roi chay ngay trong
  cung mot lenh" (irm <url> | iex). Khuon do la dung hinh "download cradle" (MITRE T1105+T1059)
  ma nhieu EDR/antivirus/agent-safety-filter gan co, bat ke noi dung ben trong co doc hai hay
  khong - dung nguyen nhan user bao "chay curl qua agent bi harness bao cai ma doc".

  Fix la doi HINH DANG chu khong phai doi noi dung: TAI VE THANH FILE THAT tren dia truoc,
  in duong dan de xem lai duoc, roi moi CHAY o mot buoc rieng. Day chinh la cach cac installer
  that (rustup, nvm, deno) trinh bay cho nguoi dung Windows.

  Script nay la MOT WRAPPER MONG - no khong viet lai 443 dong logic cua install.sh. No chi tim
  mot shell POSIX da co san tren may (Git Bash hoac WSL - hau het may dev da co Git de lam viec
  voi repo nay, nen day khong phai dependency moi), roi giao lai TOAN BO logic cho bootstrap.sh/
  install.sh nhu tren macOS/Linux. Mot nguon logic duy nhat, khong drift.

.PARAMETER Root
  Thu muc du an dich. Mac dinh: thu muc hien tai.
.PARAMETER HarnessOnly
  Chi cai harness (bo skills + llmwiki). Mac dinh cai ca 3 tru.
.PARAMETER Vendor
  Ep danh sach vendor, vd "claude,opencode". Bo qua de tu do.
.PARAMETER Clean
  Cai moi = go ban cu roi cai.
.PARAMETER NoGraph
  Khong keo module orca-graph (repo rieng Rheinmir/orca-graph). Mac dinh: option nay DA TICK -
  co terminal thi hien checklist, Enter la keo du.
.PARAMETER NoVerify
  Bo buoc chay demo.sh + test-broad.sh sau khi cai.
.PARAMETER Base
  Doi nguon/branch (mac dinh: nhanh chinh cua Rheinmir/setup). Hiem khi can dung tay.

.EXAMPLE
  iwr -useb https://raw.githubusercontent.com/Rheinmir/setup/orca/harness/poc-vendor-neutral/install.ps1 -OutFile install.ps1
  # (tuy chon) doc lai truoc khi chay: Get-Content install.ps1
  .\install.ps1
#>
param(
  [string]$Root = ".",
  [switch]$HarnessOnly,
  [string]$Vendor,
  [switch]$Clean,
  [switch]$NoVerify,
  [switch]$NoGraph,
  [string]$Base = "https://raw.githubusercontent.com/Rheinmir/setup/orca/harness/poc-vendor-neutral"
)

function Say($msg) { Write-Host "[install.ps1] $msg" -ForegroundColor Cyan }
function Fail($msg) { Write-Host "[install.ps1] $msg" -ForegroundColor Red; exit 1 }

# Buoc 1 - tim mot shell POSIX da co san tren may. KHONG tu cai them gi (khong ep dependency moi).
# GH#169: `Get-Command bash` hay tra ve C:\Windows\System32\bash.exe = trinh khoi chay WSL -> HOME cua WSL, Claude Code
# ban Windows khong thay skills/hook. Nen tim Git Bash TUONG MINH truoc; bash.exe trong System32 khong bao gio tinh la Git Bash.
$bash = $null
$gitCmd = Get-Command git -ErrorAction SilentlyContinue
$cands = @("$env:ProgramFiles\Git\bin\bash.exe", "${env:ProgramFiles(x86)}\Git\bin\bash.exe", "$env:LOCALAPPDATA\Programs\Git\bin\bash.exe")
if ($gitCmd) { $cands += (Join-Path (Split-Path (Split-Path $gitCmd.Source)) "bin\bash.exe") }
foreach ($c in $cands) { if ($c -and (Test-Path $c)) { $bash = Get-Item $c; break } }
if (-not $bash) {
  $b = Get-Command bash -ErrorAction SilentlyContinue
  if ($b -and $b.Source -notlike "$env:SystemRoot\System32\*") { $bash = $b }
}
if ($bash -and -not $bash.Source) { $bash | Add-Member -NotePropertyName Source -NotePropertyValue $bash.FullName }
$wsl = Get-Command wsl -ErrorAction SilentlyContinue
if (-not $bash -and $wsl) {
  # `wsl` co san khong chac da co MOT distro nao cai - kiem nhanh truoc khi tin no chay duoc.
  $null = & wsl.exe -l -q 2>$null
  if ($LASTEXITCODE -ne 0) { $wsl = $null }
}
if (-not $bash -and -not $wsl) {
  Fail @"
Khong tim thay Git Bash hoac WSL tren may nay - can MOT trong hai de chay overstack.
Hau het may dev da co san Git (de lam viec voi repo nay), va Git for Windows co kem Git Bash:
  https://git-scm.com/download/win
Cai xong, mo lai PowerShell/Terminal roi chay lenh nay lan nua.
"@
}

# Buoc 2 - TAI VE THANH FILE THAT, khong pipe thang tu mang vao trinh thong dich.
$tmp = Join-Path ([System.IO.Path]::GetTempPath()) "overstack-bootstrap-$([guid]::NewGuid().ToString('N')).sh"
Say "tai bootstrap.sh tu $Base"
try {
  Invoke-WebRequest -UseBasicParsing -Uri "$Base/bootstrap.sh" -OutFile $tmp
} catch {
  Fail "tai loi: $($_.Exception.Message)"
}
Say "da tai ve: $tmp  (muon xem truoc noi dung: Get-Content '$tmp')"

# Buoc 3 - ghep flag theo dung cu phap bootstrap.sh/install.sh da dung tren macOS/Linux,
# de mot bo huong dan duy nhat dung tren moi he dieu hanh.
$bootstrapArgs = @()
if ($HarnessOnly) { $bootstrapArgs += "--harness-only" }
if ($Vendor)      { $bootstrapArgs += "--vendor", $Vendor }
if ($Clean)       { $bootstrapArgs += "--clean" }
if ($NoVerify)    { $bootstrapArgs += "--no-verify" }
if ($NoGraph)     { $bootstrapArgs += "--no-graph" }

$scriptText = Get-Content -Raw -Path $tmp
if ($Base -ne "https://raw.githubusercontent.com/Rheinmir/setup/orca/harness/poc-vendor-neutral") {
  # HARNESS_BASE la bien moi truong ma bootstrap.sh doc - dat truoc trong CHINH luong stdin nay
  # thay vi $env:HARNESS_BASE cua PowerShell, vi WSL khong tu dong mang bien moi truong Windows
  # qua ranh gioi Linux (can khai WSLENV, de tranh phu thuoc cau hinh do, ghi thang vao script).
  $scriptText = "export HARNESS_BASE='$Base'`n$scriptText"
}

# Buoc 4 - CHAY o mot buoc RIENG (khong con la mot lenh vua-tai-vua-chay). Doc thu muc dich
# TRUOC khi goi shell con, de shell con ke thua dung cwd du dung Git Bash hay WSL.
Push-Location $Root
try {
  Say "chay qua $(if ($bash) { 'Git Bash' } else { 'WSL' }) ..."
  if ($bash) {
    $scriptText | & $bash.Source -s -- @bootstrapArgs
  } else {
    Write-Host "[install.ps1] CANH BAO: khong thay Git Bash, dang dung WSL - phan global (skills/hook) vao HOME cua WSL; Claude Code ban Windows se KHONG thay. Nen cai Git for Windows roi chay lai." -ForegroundColor Yellow
    $scriptText = "export OVERSTACK_WSL_OK=1`n$scriptText"   # da canh bao o day, khoi canh bao lan hai trong bootstrap
    $scriptText | & wsl.exe bash -s -- @bootstrapArgs
  }
  $code = $LASTEXITCODE
} finally {
  Pop-Location
  Remove-Item -Path $tmp -ErrorAction SilentlyContinue
}
if ($code -ne 0) { Fail "cai loi (thoat $code) - xem log ben tren" }
Say "xong."
exit 0
