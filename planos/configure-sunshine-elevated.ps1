param(
    [Parameter(Mandatory = $true)]
    [string]$LogPath,

    [Parameter(Mandatory = $true)]
    [string]$PasswordFilePath
)

$ErrorActionPreference = 'Stop'
$logDirectory = Split-Path -Parent $LogPath
New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
"[$(Get-Date -Format o)] configuração elevada iniciada" | Set-Content -LiteralPath $LogPath -Encoding UTF8

function Write-Log {
    param([Parameter(Mandatory = $true)][string]$Message)
    "[$(Get-Date -Format o)] $Message" | Add-Content -LiteralPath $LogPath -Encoding UTF8
}

$serviceWasRunning = $false

try {
    $sunshinePath = 'C:\Program Files\Sunshine\sunshine.exe'
    $configPath = 'C:\Program Files\Sunshine\config\sunshine.conf'
    if (-not (Test-Path -LiteralPath $PasswordFilePath -PathType Leaf)) {
        throw "Arquivo temporário de senha não encontrado: $PasswordFilePath"
    }
    $password = [System.IO.File]::ReadAllText($PasswordFilePath).Trim()

    if (-not (Test-Path -LiteralPath $sunshinePath -PathType Leaf)) {
        throw "Executável do Sunshine não encontrado: $sunshinePath"
    }
    if ([string]::IsNullOrWhiteSpace($password)) {
        throw 'A senha temporária não foi recebida pelo processo elevado.'
    }

    $adapter = @(Get-NetAdapter -ErrorAction Stop |
        Where-Object {
            $_.Status -eq 'Up' -and
            ($_.Name -match 'Tailscale' -or $_.InterfaceDescription -match 'Tailscale')
        } |
        Sort-Object ifIndex)[0]
    if ($null -eq $adapter) {
        throw 'Adaptador Tailscale ativo não encontrado.'
    }
    Write-Log ("adaptador Tailscale: Name={0}; ifIndex={1}; Description={2}" -f $adapter.Name, $adapter.ifIndex, $adapter.InterfaceDescription)

    $service = Get-Service -Name 'SunshineService' -ErrorAction Stop
    if ($service.Status -eq 'Running') {
        $serviceWasRunning = $true
        Stop-Service -Name 'SunshineService' -Force -ErrorAction Stop
        (Get-Service -Name 'SunshineService' -ErrorAction Stop).WaitForStatus('Stopped', [TimeSpan]::FromSeconds(15))
        Write-Log 'SunshineService parado temporariamente para atualizar credenciais'
    }

    $credentialOutput = & $sunshinePath --creds 'admin' $password 2>&1
    $credentialExitCode = $LASTEXITCODE
    $safeCredentialOutput = (($credentialOutput | Out-String).Trim()).Replace($password, '[REDACTED]')
    if (-not [string]::IsNullOrWhiteSpace($safeCredentialOutput)) {
        Write-Log $safeCredentialOutput
    }
    Write-Log ("sunshine --creds exit code: {0}" -f $credentialExitCode)
    if ($credentialExitCode -ne 0) {
        throw "sunshine --creds falhou com código $credentialExitCode."
    }

    $configLines = @()
    if (Test-Path -LiteralPath $configPath -PathType Leaf) {
        $configLines = @(Get-Content -LiteralPath $configPath -ErrorAction Stop)
    }
    $options = [ordered]@{
        'origin_web_ui_allowed' = 'wan'
        'upnp' = 'disabled'
    }
    $writtenKeys = @{}
    $newConfigLines = @(
        foreach ($line in $configLines) {
        if ($line -match '^\s*(origin_web_ui_allowed|upnp)\s*=') {
            $key = $Matches[1]
            if (-not $writtenKeys.ContainsKey($key)) {
                $writtenKeys[$key] = $true
                "$key = $($options[$key])"
            }
        } else {
            $line
        }
        }
    )
    foreach ($key in $options.Keys) {
        if (-not $writtenKeys.ContainsKey($key)) {
            $newConfigLines += "$key = $($options[$key])"
        }
    }
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllLines($configPath, [string[]]$newConfigLines, $utf8NoBom)
    Write-Log 'sunshine.conf atualizado: origin_web_ui_allowed=wan; upnp=disabled'

    $defaultRules = @(Get-NetFirewallRule -DisplayName 'Sunshine' -ErrorAction SilentlyContinue)
    foreach ($rule in $defaultRules) {
        Set-NetFirewallRule -Name $rule.Name -Enabled False -ErrorAction Stop
    }
    Write-Log ("regras padrão Sunshine desabilitadas: {0}" -f $defaultRules.Count)

    function Ensure-TailscaleRule {
        param(
            [Parameter(Mandatory = $true)][string]$DisplayName,
            [Parameter(Mandatory = $true)][string]$Protocol,
            [Parameter(Mandatory = $true)][int[]]$LocalPort
        )

        $existing = @(Get-NetFirewallRule -DisplayName $DisplayName -ErrorAction SilentlyContinue)
        foreach ($rule in $existing) {
            Remove-NetFirewallRule -Name $rule.Name -ErrorAction Stop
        }
        New-NetFirewallRule -DisplayName $DisplayName `
            -Direction Inbound -InterfaceAlias $adapter.Name -Action Allow `
            -Protocol $Protocol -LocalPort $LocalPort -Profile Any `
            -Enabled True -EdgeTraversalPolicy Block -ErrorAction Stop | Out-Null
        Write-Log ("regra criada: {0}; protocolo={1}; portas={2}; interface={3}" -f $DisplayName, $Protocol, ($LocalPort -join ','), $adapter.Name)
    }

    Ensure-TailscaleRule -DisplayName 'Sunshine via Tailscale TCP' -Protocol TCP -LocalPort @(47984, 47989, 47990, 48010)
    Ensure-TailscaleRule -DisplayName 'Sunshine via Tailscale UDP' -Protocol UDP -LocalPort @(47998, 47999, 48000)

    Start-Service -Name 'SunshineService' -ErrorAction Stop
    $service = Get-Service -Name 'SunshineService' -ErrorAction Stop
    if ($service.Status -ne 'Running') {
        throw "SunshineService não iniciou; status atual: $($service.Status)"
    }
    Write-Log 'SunshineService reiniciado e está Running'
    Write-Log 'configuração elevada concluída; senha não foi gravada no log'
    exit 0
}
catch {
    if ($serviceWasRunning) {
        try {
            Start-Service -Name 'SunshineService' -ErrorAction SilentlyContinue
        } catch {
        }
    }
    Write-Log ("ERRO: {0}" -f $_.Exception.Message)
    exit 1
}
