param(
    [Parameter(Mandatory = $true)]
    [string]$CapturePath,

    [Parameter(Mandatory = $true)]
    [string]$TextPath,

    [Parameter(Mandatory = $true)]
    [string]$LogPath
)

$ErrorActionPreference = 'Continue'
$logDirectory = Split-Path -Parent $LogPath
New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
"[$(Get-Date -Format o)] parando captura PktMon" | Set-Content -LiteralPath $LogPath -Encoding UTF8

$stopOutput = & pktmon stop 2>&1
$stopOutput | Out-String | Add-Content -LiteralPath $LogPath -Encoding UTF8

if (Test-Path -LiteralPath $CapturePath) {
    & pktmon etl2txt $CapturePath --out $TextPath --brief 2>&1 |
        Out-String |
        Add-Content -LiteralPath $LogPath -Encoding UTF8
    "[$(Get-Date -Format o)] conversão concluída: $TextPath" | Add-Content -LiteralPath $LogPath -Encoding UTF8
} else {
    "[$(Get-Date -Format o)] ERRO: arquivo de captura não encontrado: $CapturePath" | Add-Content -LiteralPath $LogPath -Encoding UTF8
    exit 1
}

exit 0
