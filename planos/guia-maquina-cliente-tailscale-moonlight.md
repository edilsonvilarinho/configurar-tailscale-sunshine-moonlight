# Guia da máquina cliente: Tailscale + Moonlight

## Objetivo

Configurar esta máquina como cliente Moonlight para acessar o computador host `sammysan`, que já está configurado com Sunshine.

Esta máquina cliente **não deve instalar Sunshine**. Ela precisa apenas de Tailscale e Moonlight.

## Dados do host já configurado

- Nome Tailscale: `sammysan`
- IP Tailscale: `100.78.107.32`
- Sunshine Web UI: `https://100.78.107.32:47990`
- Usuário do Sunshine: `admin`
- Senha: será fornecida separadamente pelo usuário; não grave, não registre em log e não inclua em arquivos.

O aviso de certificado “Não seguro” no endereço HTTPS do Sunshine é esperado, porque a interface usa certificado local.

## Regras para o agente

1. Execute comandos PowerShell somente quando forem necessários.
2. Preserve uma instalação existente do Tailscale ou Moonlight. Não faça logout, desinstalação ou reset sem autorização.
3. Se o Tailscale estiver em `NeedsLogin`, mostre o link de autenticação e peça ao usuário para aprovar no navegador.
4. Use a mesma conta/mesmo tailnet Tailscale do host. Se a máquina estiver em outra conta, pare e peça ao usuário para corrigir o acesso; não altere ACLs por conta própria.
5. Não faça port forwarding no roteador, não abra portas públicas e não desabilite o firewall do Windows.
6. Não crie novas credenciais no Sunshine. As credenciais do host já existem.
7. Nunca registre a senha do Sunshine, a senha do Tailscale ou o PIN do Moonlight em arquivo, log ou mensagem de diagnóstico.
8. Se a interface do Sunshine mostrar novamente “Welcome to Sunshine” ou pedir para criar credenciais, pare: isso indica que o endereço ou o contexto está incorreto.

## 1. Pré-validação

Abra o PowerShell e execute:

```powershell
$ErrorActionPreference = 'Stop'

Write-Host '--- Windows ---'
Get-CimInstance Win32_OperatingSystem |
    Select-Object Caption,Version,OSArchitecture

Write-Host '--- Winget ---'
winget --version

Write-Host '--- Tailscale instalado ---'
winget list --id Tailscale.Tailscale --exact

Write-Host '--- Moonlight instalado ---'
winget list --id MoonlightGameStreamingProject.Moonlight --exact
```

Se o Winget não existir, informe o erro ao usuário e use os instaladores oficiais, sem baixar executáveis de sites não oficiais.

## 2. Instalar e autenticar o Tailscale

Se o Tailscale ainda não estiver instalado:

```powershell
winget install --id Tailscale.Tailscale --exact --source winget `
    --accept-package-agreements --accept-source-agreements `
    --silent --disable-interactivity
```

Localize o executável e verifique o estado:

```powershell
$tailscale = @(
    'C:\Program Files\Tailscale\tailscale.exe',
    'C:\Program Files (x86)\Tailscale\tailscale.exe'
) | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1

if (-not $tailscale) {
    throw 'tailscale.exe não foi encontrado.'
}

& $tailscale status
& $tailscale ip -4
```

Se o estado for `Logged out` ou `NeedsLogin`, execute:

```powershell
& $tailscale up
```

Se aparecer um link `https://login.tailscale.com/...`, mostre-o ao usuário e aguarde a aprovação. Não tente autenticar usando senha, chave ou token fornecido por terceiros.

Depois da autenticação, valide:

```powershell
& $tailscale status
$clientIp = (& $tailscale ip -4 2>&1 | Select-Object -First 1).ToString().Trim()
Write-Host "CLIENT_TAILSCALE_IP=$clientIp"

if ($clientIp -notmatch '^100\.\d+\.\d+\.\d+$') {
    throw "O cliente não recebeu um IP Tailscale válido: $clientIp"
}
```

O host `sammysan` deve aparecer como conectado. Teste a rota Tailscale:

```powershell
& $tailscale ping 100.78.107.32
```

O resultado deve indicar resposta do host. Latência alta pode ser aceitável; ausência total de resposta não é.

## 3. Validar o Sunshine antes de instalar o Moonlight

> Importante: `127.0.0.1` sempre representa a máquina onde o comando é executado. Nesta máquina cliente, não execute o teste contra `127.0.0.1`, pois o Sunshine está no host `sammysan`. O teste correto do cliente para o host usa `100.78.107.32`.

Teste a porta da interface web:

```powershell
Test-NetConnection 100.78.107.32 -Port 47990
```

O campo `TcpTestSucceeded` deve ser `True`.

Abra no navegador:

```text
https://100.78.107.32:47990
```

Aceite o aviso do certificado e use:

- Usuário: `admin`
- Senha: fornecida separadamente pelo usuário

O resultado esperado é a tela autenticada do Sunshine, com menus como `Home`, `PIN`, `Applications` e `Configuration`. Se aparecer a tela de criação de credenciais, pare e informe o usuário.

## 3A. Se a porta só funcionar com o firewall do host desativado

Foi observado que o acesso do `NOTE-LAT-012` passou de `False` para `True` quando o Firewall do Windows do host `sammysan` foi desativado. A correção pertence ao host, não a esta máquina cliente.

No host, o perfil privado do Tailscale estava com `AllowInboundRules=False`, apesar de existirem regras Allow para o Sunshine. Essa configuração fazia o Windows ignorar as regras locais. O host foi corrigido mantendo o firewall ativado, a entrada padrão como `Block` e as regras restritas à origem `100.114.232.6`, ao destino `100.78.107.32`, à interface `Tailscale` e às portas do Sunshine.

No cliente, não desative o firewall nem crie regras amplas. Apenas repita o teste:

```powershell
Test-NetConnection 100.78.107.32 -Port 47990 -InformationLevel Detailed
```

O resultado esperado é `TcpTestSucceeded=True`. Se continuar `False`, envie o resultado completo ao responsável pelo host; não instale Sunshine no cliente e não abra portas públicas.

## 4. Instalar o Moonlight

Se o Moonlight ainda não estiver instalado:

```powershell
winget install --id MoonlightGameStreamingProject.Moonlight --exact --source winget `
    --accept-package-agreements --accept-source-agreements `
    --silent --disable-interactivity
```

Se o Winget não encontrar exatamente esse pacote, não instale um pacote parecido. Informe a falha e use a página oficial de releases:

<https://github.com/moonlight-stream/moonlight-qt/releases>

Abra o Moonlight pelo menu Iniciar.

## 5. Adicionar e parear o host

No Moonlight:

1. Escolha `Add PC` ou o botão `+`.
2. Informe somente o IP `100.78.107.32`.
3. Selecione o host Sunshine encontrado.
4. O Moonlight exibirá um PIN de pareamento.

Enquanto o PIN estiver visível, abra novamente no navegador:

```text
https://100.78.107.32:47990
```

Na interface Sunshine:

1. Abra a aba `PIN`.
2. Informe o PIN mostrado pelo Moonlight.
3. Confirme o pareamento.

Se o agente não conseguir operar a interface web, peça ao usuário para inserir o PIN. Não registre o PIN em arquivo ou log.

## 6. Primeiro teste

Depois do pareamento:

1. No Moonlight, abra o host `sammysan`.
2. Inicie `Desktop` ou o aplicativo disponível.
3. Confirme imagem, áudio e latência.
4. Teste o controle somente se houver um controle conectado.

O aviso `Choose Windows Gamepad Drivers` no Sunshine não impede o streaming de vídeo. A configuração de controle pode ser feita depois, se necessária.

## Critérios de sucesso

Considerar a configuração concluída somente quando todos os itens abaixo forem verdadeiros:

- Tailscale do cliente está conectado à mesma conta/tailnet.
- O cliente recebeu um IP `100.x.x.x`.
- `tailscale ping 100.78.107.32` responde.
- `Test-NetConnection 100.78.107.32 -Port 47990` retorna `True`.
- A interface Sunshine abre e exige login, sem exibir a tela de criação inicial.
- O PIN foi aceito pelo Sunshine.
- O Moonlight inicia uma sessão do host.

## Diagnóstico seguro

### Host não aparece no Moonlight

Confirme primeiro o Tailscale:

```powershell
& $tailscale status
& $tailscale ping 100.78.107.32
```

Não use descoberta automática como único método; adicione o IP manualmente.

### Interface Sunshine não abre

Execute:

```powershell
Test-NetConnection 100.78.107.32 -Port 47990
```

Se retornar `False`, confirme que o host está ligado, o Tailscale está conectado e o Sunshine está em execução. Não abra portas no roteador.

Se o teste for executado no cliente e continuar retornando `False`, não instale Sunshine no cliente. Cole o diagnóstico abaixo e envie o resultado:

```powershell
$tailscale = @(
    'C:\Program Files\Tailscale\tailscale.exe',
    'C:\Program Files (x86)\Tailscale\tailscale.exe'
) | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1

hostname
& $tailscale status
& $tailscale netcheck
& $tailscale ping --tsmp 100.78.107.32
& $tailscale ping --icmp --c=1 100.78.107.32

Get-NetFirewallProfile -PolicyStore ActiveStore |
    Select-Object Name,Enabled,DefaultOutboundAction,AllowLocalFirewallRules

Get-NetFirewallRule -Direction Outbound -Enabled True -Action Block |
    Select-Object DisplayName,Profile,Program,ServiceName,PolicyStoreSourceType

Get-CimInstance -Namespace 'root/SecurityCenter2' -ClassName FirewallProduct |
    Select-Object displayName,pathToSignedProductExe,productState
```

Interpretação mínima:

- `tailscale ping --tsmp` com falha: problema de transporte/rota do Tailscale.
- `--tsmp` funciona, mas `--icmp` e TCP falham: investigar política de acesso ou filtragem entre a pilha do cliente e o host.
- Regra de saída `Block` ou `DefaultOutboundAction=Block`: não altere sem registrar a regra; crie uma exceção somente depois de confirmar o escopo.
- Não desabilite o Firewall nem crie uma permissão ampla para todos os programas.

### PIN não conclui o pareamento

Verifique se o PIN foi digitado na aba `PIN` do Sunshine dentro do prazo exibido pelo Moonlight. Gere um novo PIN e tente novamente.

### Erro `CSRF Protection Error` ao enviar o PIN

Esse erro aparece quando o Web UI é acessado pelo endereço Tailscale, mas essa origem ainda não foi autorizada no host. A correção deve ser feita no `sammysan`, não no cliente, adicionando ao `sunshine.conf` a origem exata:

```text
csrf_allowed_origins = https://100.78.107.32:47990
```

Depois de reiniciar o serviço Sunshine, atualize a página `/pin` no cliente e reenvie o PIN que continua aguardando no Moonlight. Se o PIN tiver expirado, cancele o pareamento no Moonlight, gere outro e envie o novo código.

### O Moonlight conecta, mas não transmite

Não altere firewall ou portas públicas sem autorização. Informe o resultado de:

```powershell
& $tailscale status
& $tailscale ping 100.78.107.32
Test-NetConnection 100.78.107.32 -Port 47990
```

## Referências oficiais

- Tailscale no Windows: <https://tailscale.com/docs/install/windows>
- Tailscale CLI: <https://tailscale.com/docs/reference/tailscale-cli>
- Guia de configuração do Moonlight: <https://github.com/moonlight-stream/moonlight-docs/wiki/Setup-Guide>
- Releases oficiais do Moonlight: <https://github.com/moonlight-stream/moonlight-qt/releases>
