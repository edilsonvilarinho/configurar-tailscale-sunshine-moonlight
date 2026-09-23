param(
    [Parameter(Mandatory = $true)]
    [string]$CapturePath,

    [Parameter(Mandatory = $true)]
    [string]$LogPath
)

$ErrorActionPreference = 'Continue'
$logDirectory = Split-Path -Parent $LogPath
New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
"[$(Get-Date -Format o)] preparando captura PktMon" | Set-Content -LiteralPath $LogPath -Encoding UTF8

try {
    $null = & pktmon stop 2>&1
    $null = & pktmon filter remove 2>&1
    & pktmon filter add -p 47990 2>&1 | Out-String | Add-Content -LiteralPath $LogPath -Encoding UTF8
    & pktmon start --capture --pkt-size 128 --file-name $CapturePath 2>&1 |
        Out-String |
        Add-Content -LiteralPath $LogPath -Encoding UTF8
    "[$(Get-Date -Format o)] captura iniciada para TCP/47990: $CapturePath" | Add-Content -LiteralPath $LogPath -Encoding UTF8
    exit 0
}
catch {
    "[$(Get-Date -Format o)] ERRO: $($_.Exception.Message)" | Add-Content -LiteralPath $LogPath -Encoding UTF8
    exit 1
}
