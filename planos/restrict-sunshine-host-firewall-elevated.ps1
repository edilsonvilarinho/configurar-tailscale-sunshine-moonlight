$ErrorActionPreference = 'Stop'

$expectedHost = 'sammysan'
$hostIp = '100.78.107.32'
$clientIp = '100.114.232.6'
$interfaceAlias = 'Tailscale'
$logPath = Join-Path $PSScriptRoot 'restrict-sunshine-host-firewall-elevated.log'

Start-Transcript -Path $logPath -Append | Out-Null
try {
    $actualHost = (hostname).Trim()
    if ($actualHost -ne $expectedHost) {
        throw "Este script só pode ser executado em '$expectedHost'. Máquina atual: '$actualHost'."
    }

    $tsProfile = Get-NetConnectionProfile -InterfaceAlias $interfaceAlias -ErrorAction Stop
    if ($tsProfile.NetworkCategory -ne 'Private') {
        throw "O perfil atual do Tailscale não é Private: $($tsProfile.NetworkCategory)"
    }

    Write-Host 'Estado anterior do perfil Private:'
    Get-NetFirewallProfile -PolicyStore ActiveStore -Name Private |
        Select-Object Name,Enabled,DefaultInboundAction,AllowInboundRules,AllowLocalFirewallRules

    # Permite que regras locais sejam consideradas no perfil Private.
    # O padrão de entrada permanece Block; somente as regras abaixo serão aceitas.
    Set-NetFirewallProfile -Profile Private -AllowInboundRules True

    # Evita manter regras genéricas que aceitariam qualquer origem no Tailscale.
    Set-NetFirewallRule -DisplayName 'Sunshine via Tailscale TCP' -Enabled False
    Set-NetFirewallRule -DisplayName 'Sunshine via Tailscale UDP' -Enabled False

    $restrictedRules = @(
        'Sunshine via Tailscale NOTE-LAT-012 TCP',
        'Sunshine via Tailscale NOTE-LAT-012 UDP'
    )

    foreach ($name in $restrictedRules) {
        $rule = Get-NetFirewallRule -DisplayName $name -ErrorAction Stop
        if (@($rule).Count -ne 1) {
            throw "Quantidade inesperada de regras para '$name': $(@($rule).Count)"
        }

        Set-NetFirewallRule -DisplayName $name `
            -Enabled True -Direction Inbound -Action Allow -Profile Private `
            -LocalAddress $hostIp -RemoteAddress $clientIp `
            -InterfaceAlias $interfaceAlias
    }

    Write-Host 'Estado final do perfil Private:'
    Get-NetFirewallProfile -PolicyStore ActiveStore -Name Private |
        Select-Object Name,Enabled,DefaultInboundAction,AllowInboundRules,AllowLocalFirewallRules

    Write-Host 'Regras finais:'
    foreach ($name in $restrictedRules) {
        $rule = Get-NetFirewallRule -DisplayName $name
        $rule | Select-Object DisplayName,Enabled,Direction,Action,Profile,PolicyStoreSourceType
        $rule | Get-NetFirewallPortFilter | Select-Object Protocol,LocalPort,RemotePort
        $rule | Get-NetFirewallAddressFilter | Select-Object LocalAddress,RemoteAddress
        $rule | Get-NetFirewallInterfaceFilter | Select-Object InterfaceAlias
    }

    Write-Host 'Validação local do Sunshine:'
    Test-NetConnection 127.0.0.1 -Port 47990 -InformationLevel Quiet
    Test-NetConnection $hostIp -Port 47990 -InformationLevel Quiet
}
finally {
    Stop-Transcript | Out-Null
}
