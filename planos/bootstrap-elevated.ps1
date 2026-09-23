param(
    [Parameter(Mandatory = $true)]
    [string]$LogPath
)

$ErrorActionPreference = 'Continue'
$logDirectory = Split-Path -Parent $LogPath
New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
"[$(Get-Date -Format o)] bootstrap iniciado" | Set-Content -Path $LogPath -Encoding UTF8

function Invoke-WingetInstall {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Id
    )

    "[$(Get-Date -Format o)] winget install $Id" | Tee-Object -FilePath $LogPath -Append
    $wingetOutput = & winget install --id $Id --exact --source winget `
        --accept-package-agreements --accept-source-agreements `
        --silent --disable-interactivity 2>&1
    $wingetOutput | Tee-Object -FilePath $LogPath -Append | Out-Host
    $exitCode = $LASTEXITCODE
    "[$(Get-Date -Format o)] exit code: $exitCode" | Tee-Object -FilePath $LogPath -Append
    return $exitCode
}

$exitCodes = @()
$exitCodes += Invoke-WingetInstall -Id 'Tailscale.Tailscale'
$exitCodes += Invoke-WingetInstall -Id 'LizardByte.Sunshine'

"[$(Get-Date -Format o)] serviços Sunshine" | Tee-Object -FilePath $LogPath -Append
Get-Service *Sunshine* 2>&1 | Out-String | Tee-Object -FilePath $LogPath -Append

"[$(Get-Date -Format o)] caminhos dos executáveis" | Tee-Object -FilePath $LogPath -Append
Get-ChildItem 'C:\Program Files\Tailscale\tailscale.exe','C:\Program Files (x86)\Tailscale\tailscale.exe','C:\Program Files\Sunshine\sunshine.exe','C:\Program Files (x86)\Sunshine\sunshine.exe' -File 2>&1 |
    Select-Object FullName,Length,LastWriteTime |
    Format-List |
    Out-String |
    Tee-Object -FilePath $LogPath -Append

"[$(Get-Date -Format o)] bootstrap concluído" | Tee-Object -FilePath $LogPath -Append
if (($exitCodes | Where-Object { $_ -ne 0 }).Count -gt 0) {
    exit 1
}
exit 0
