$ErrorActionPreference = 'Stop'

$expectedHost = 'sammysan'
$configPath = 'C:\Program Files\Sunshine\config\sunshine.conf'
$allowedOrigin = 'https://100.78.107.32:47990'
$logPath = Join-Path $PSScriptRoot 'allow-sunshine-tailscale-origin-elevated.log'

Start-Transcript -Path $logPath -Append | Out-Null
try {
    $actualHost = (hostname).Trim()
    if ($actualHost -ne $expectedHost) {
        throw "Este script só pode ser executado em '$expectedHost'. Máquina atual: '$actualHost'."
    }
    if (-not (Test-Path -LiteralPath $configPath)) {
        throw "Arquivo de configuração não encontrado: $configPath"
    }

    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $backupPath = "$configPath.backup-$stamp"
    Copy-Item -LiteralPath $configPath -Destination $backupPath -Force

    $content = [System.IO.File]::ReadAllText($configPath)
    $line = "csrf_allowed_origins = $allowedOrigin"
    $pattern = '(?im)^\s*csrf_allowed_origins\s*=.*$'

    if ([System.Text.RegularExpressions.Regex]::IsMatch($content, $pattern)) {
        $updated = [System.Text.RegularExpressions.Regex]::Replace($content, $pattern, [System.Text.RegularExpressions.MatchEvaluator]{ param($match) $line }, 1)
    } else {
        $separator = if ($content.EndsWith("`r`n") -or $content.EndsWith("`n")) { '' } else { "`r`n" }
        $updated = $content + $separator + $line + "`r`n"
    }

    $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::WriteAllText($configPath, $updated, $utf8NoBom)

    Write-Host "Origem CSRF configurada: $allowedOrigin"
    Select-String -LiteralPath $configPath -Pattern '^\s*csrf_allowed_origins\s*=' -CaseSensitive:$false |
        ForEach-Object Line
    Write-Host "Backup criado: $backupPath"

    Restart-Service -Name 'SunshineService' -Force
    $service = Get-Service -Name 'SunshineService'
    $service | Select-Object Name,Status,StartType
    Start-Sleep -Seconds 2
    Test-NetConnection 127.0.0.1 -Port 47990 -InformationLevel Quiet
}
finally {
    Stop-Transcript | Out-Null
}
