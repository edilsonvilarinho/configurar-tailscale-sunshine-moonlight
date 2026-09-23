param(
    [Parameter(Mandatory = $true)]
    [string]$LogPath
)

$ErrorActionPreference = 'Stop'
$logDirectory = Split-Path -Parent $LogPath
New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
"[$(Get-Date -Format o)] habilitando log de bloqueios do Firewall" | Set-Content -LiteralPath $LogPath -Encoding UTF8

try {
    Set-NetFirewallProfile -Profile Domain,Private,Public -LogBlocked True -ErrorAction Stop
    Get-NetFirewallProfile |
        Select-Object Name,LogBlocked,LogAllowed,LogFileName,LogMaxSizeKilobytes |
        Format-Table -AutoSize |
        Out-String |
        Add-Content -LiteralPath $LogPath -Encoding UTF8
    "[$(Get-Date -Format o)] log de bloqueios habilitado" | Add-Content -LiteralPath $LogPath -Encoding UTF8
    exit 0
}
catch {
    "[$(Get-Date -Format o)] ERRO: $($_.Exception.Message)" | Add-Content -LiteralPath $LogPath -Encoding UTF8
    exit 1
}
