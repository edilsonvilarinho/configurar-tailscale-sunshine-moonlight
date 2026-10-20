# Instruções para agentes de IA

Este arquivo é lido automaticamente por Claude Code, Codex, Cursor e outros agentes. Ele descreve
como **executar** a configuração deste repositório, em **Linux (Bazzite)** ou **Windows**, não
apenas como explicá-la.

Humano lendo isto: você não precisa deste arquivo. Siga o [`README.md`](README.md)
([English](README.en.md)).

---

## Objetivo

Transformar o host em servidor de streaming de jogos (Sunshine), alcançável **somente** pela rede
privada Tailscale, e parear ao menos um cliente Moonlight.

## Regras inegociáveis (valem nas duas plataformas)

1. **Nunca** abra porta no roteador, não habilite UPnP e **não desative o firewall**, nem
   "só para testar". Se desativar o firewall fizer funcionar, isso é o diagnóstico — não a solução.
2. **Nunca** escreva senha, token ou PIN em arquivo do repositório, log, commit ou na sua resposta.
   Se o usuário informar uma senha no chat, avise que ela ficou exposta ali e recomende trocá-la.
3. **Peça confirmação explícita** antes de: login automático, impedir a suspensão do sistema, e
   restringir o firewall da rede local.
4. Faça **cópia de segurança** de `sunshine.conf` antes de qualquer edição.
5. Verifique cada passo antes de seguir para o próximo. Não presuma sucesso pelo código de saída
   de um comando que não mede o que importa.
6. Se um passo falhar, **pare e relate**. Não contorne com solução mais permissiva.
7. Não invente endereço, nome de máquina nem caminho de instalação: **descubra** em tempo de
   execução. Os valores que aparecem nos documentos deste repositório são de outras máquinas.

---

## Passo 0 · Identifique a plataforma e siga a parte certa

```bash
# Linux
grep -E '^(PRETTY_NAME|VARIANT_ID)=' /etc/os-release
echo $XDG_SESSION_TYPE $XDG_CURRENT_DESKTOP
```
```powershell
# Windows
Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,OSArchitecture
```

| Sistema encontrado | Vá para |
|---|---|
| Bazzite (Fedora atômico, KDE/Wayland) | **[Parte A](#parte-a--host-bazzite-linux)** |
| Windows 10 / 11 | **[Parte B](#parte-b--host-windows)** |
| Outro Linux | Parte A serve de base, mas `ujust` não existe: instale o Sunshine pelo Flatpak e avise o usuário das diferenças |

Se o host é só para **receber** a transmissão, pule para a **[Parte C](#parte-c--cliente-qualquer-plataforma)**.

---

# Parte A · Host Bazzite (Linux)

Guia humano correspondente: [`guias/bazzite-host-tailscale-sunshine.html`](guias/bazzite-host-tailscale-sunshine.html).
Decisões e registro da execução: [`planos/configurar-bazzite-sunshine-tailscale-moonlight.md`](planos/configurar-bazzite-sunshine-tailscale-moonlight.md).

## Como obter privilégio (leia antes)

`sudo` vai pedir senha e **você não consegue digitá-la**. Duas saídas, nesta ordem:

1. **Peça ao usuário** que rode o comando, dizendo exatamente qual é.
2. **Abra um terminal na sessão gráfica dele** e deixe o `sudo` pedir a senha lá:
   ```bash
   setsid konsole -e bash /caminho/do/script.sh          # KDE
   setsid gnome-terminal -- bash /caminho/do/script.sh   # GNOME
   ```

**Não use `pkexec`.** A partir de um shell automatizado o polkit responde `Not authorized` sem
abrir diálogo, porque não há agente de autenticação atrelado ao seu processo. Já foi testado aqui.

## A1 · Inventário (não altera nada)

```bash
bash scripts/bazzite-host-preflight.sh
```
Relate o estado encontrado antes de modificar qualquer coisa.

## A2 · Tailscale

```bash
ujust tailscale enable                 # precisa de sudo
sudo tailscale up --operator=$USER     # imprime link de login
```
O link `https://login.tailscale.com/a/…` precisa ser aberto **pelo usuário**. Entregue e aguarde.

**Verificação:** `tailscale ip -4` devolve `100.x.y.z`. Guarde; os passos seguintes usam esse valor.

## A3 · Sunshine

```bash
ujust setup-sunshine        # opção: Enable (Flatpak)
```
Equivale a `flatpak install --system`, depois `additional-install.sh` (permissões de `uinput`) e
`systemctl --user enable --now app-dev.lizardbyte.app.Sunshine`.

**Verificação:** `ss -ltn | grep -E ':(47984|47989|47990|48010) '` lista as quatro portas.

## A4 · Permissão de captura (Wayland/KDE)

Não existe no Windows e é onde mais gente trava. O KDE pede autorização na primeira captura;
em *Configurações → Aplicativos → Permissões*, o Sunshine precisa de **Controle remoto**.

Se der erro 503 / `Failed to find display`:
```bash
mkdir -p ~/.config/environment.d
echo 'KWIN_WAYLAND_NO_PERMISSION_CHECKS=1' > ~/.config/environment.d/98-kwin-no-permission-checks.conf
```
Só vale em sessão nova: o usuário precisa sair e entrar.

## A5 · Interface web pela tailnet

```bash
CONF=~/.var/app/dev.lizardbyte.app.Sunshine/config/sunshine/sunshine.conf
cp -a "$CONF" "$CONF.backup-$(date +%Y%m%d-%H%M%S)"
printf 'origin_web_ui_allowed = wan\nupnp = disabled\n' >> "$CONF"
printf 'csrf_allowed_origins = https://%s:47990\n' "$(tailscale ip -4)" >> "$CONF"
systemctl --user restart app-dev.lizardbyte.app.Sunshine
```
Se a chave já existir, **edite a linha** em vez de acrescentar outra.

**Verificação:** `curl -sk -o /dev/null -w '%{http_code}\n' https://$(tailscale ip -4):47990/`
responde `401` — e não falha de conexão.

## A6 · Credenciais

A senha é do usuário. **Não a invente nem a peça no chat.**
```bash
xdg-open https://localhost:47990
```
Oriente: senha forte, diferente da do sistema. Certificado autoassinado é normal.

**Verificação:** `grep -o '"username"[^,]*' ~/.var/app/dev.lizardbyte.app.Sunshine/config/sunshine/sunshine_state.json`

## A7 · Firewall (confirme antes)

No Bazzite a zona padrão já libera TCP/UDP 1025-65535 em **todas** as interfaces. O trabalho é
**fechar** para a rede local, mantendo a tailnet.

```bash
bash scripts/bazzite-host-firewall-tailnet.sh            # simulação: mostre a saída ao usuário
bash scripts/bazzite-host-firewall-tailnet.sh --apply    # só após confirmação
```
Avise que isso bloqueia entrada da LAN em portas altas (KDE Connect, Steam Remote Play local).
Desfazer: `--revert`.

> **Não troque a zona de `tailscale0`**: derruba o link
> ([tailscale#15968](https://github.com/tailscale/tailscale/issues/15968), versões ≥ 1.84).

**Verificação:** `firewall-cmd --get-zone-of-interface=tailscale0` diz `no zone`, e
`tailscale ip -4` continua respondendo.

## A8 · Monitor capturado

Com mais de um monitor o erro é silencioso: sem `output_name`, captura-se o primeiro fluxo.
```bash
grep '\[wayland\] Name' ~/.var/app/dev.lizardbyte.app.Sunshine/config/sunshine/sunshine.log | tail -4
echo 'output_name = DP-1' >> "$CONF"      # use o nome correto
systemctl --user restart app-dev.lizardbyte.app.Sunshine
```
Pergunte ao usuário **qual** monitor transmitir.

**Verificação:** linha `Streaming display '<nome>'` no log após o reinício.

## A9 · Host sempre pronto (confirme cada item)

O Sunshine é serviço de usuário: sem sessão gráfica aberta, não há captura.
```bash
sudo tee /etc/sddm.conf.d/10-autologin.conf    # RISCO: acesso físico entra sem senha
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
loginctl enable-linger $USER
```

Siga para a **[Parte C](#parte-c--cliente-qualquer-plataforma)**.

---

# Parte B · Host Windows

Registro da execução que originou este procedimento:
[`planos/configurar-tailscale-sunshine-moonlight.md`](planos/configurar-tailscale-sunshine-moonlight.md).

> [!WARNING]
> Os scripts `planos/*.ps1` **validam o hostname** (`sammysan`) e se recusam a rodar em outra
> máquina. São o registro daquela execução, não ferramenta reutilizável. Use-os como referência e
> execute os comandos equivalentes com os valores **da máquina atual**.

## Como obter privilégio (leia antes)

Quase tudo aqui exige **PowerShell como Administrador**, e o UAC não pode ser respondido por você.
Peça ao usuário que abra um PowerShell elevado e rode os comandos, ou que confirme o UAC quando
você disparar um. Não tente contornar o UAC.

## B1 · Pré-validação (elevado, não altera nada)

```powershell
$ErrorActionPreference = 'Continue'
Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,OSArchitecture
winget --version
winget list --id Tailscale.Tailscale --exact
winget list --id LizardByte.Sunshine --exact
Get-Service SunshineService -ErrorAction SilentlyContinue
Get-NetFirewallProfile -PolicyStore ActiveStore |
    Select-Object Name,Enabled,DefaultInboundAction,AllowInboundRules,AllowLocalFirewallRules
Get-CimInstance Win32_VideoController | Select-Object Name,DriverVersion
```
Guarde essa saída. É com ela que você compara depois.

## B2 · Tailscale

```powershell
winget install --id Tailscale.Tailscale --exact --source winget `
    --accept-package-agreements --accept-source-agreements --silent --disable-interactivity
```

Localize o executável em vez de presumir o caminho:
```powershell
$tailscale = @(
    'C:\Program Files\Tailscale\tailscale.exe',
    'C:\Program Files (x86)\Tailscale\tailscale.exe'
) | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $tailscale) { throw 'tailscale.exe não encontrado.' }

& $tailscale up            # mostra o link de login; o USUÁRIO aprova no navegador
& $tailscale status
& $tailscale ip -4
```

**Verificação:** `ip -4` devolve `100.x.y.z`. Se o estado for `Logged out` ou `NeedsLogin`,
entregue o link ao usuário e aguarde — não tente autenticar com chave de terceiros.

## B3 · Sunshine

```powershell
winget install --id LizardByte.Sunshine --exact --source winget `
    --accept-package-agreements --accept-source-agreements --silent --disable-interactivity
```

**Descubra** o caminho real, não presuma `C:\Program Files\Sunshine`:
```powershell
$svc = Get-CimInstance Win32_Service -Filter "Name='SunshineService'"
$sunshineExe = ($svc.PathName -replace '^"|"$', '')
$sunshineDir = Split-Path -Parent $sunshineExe
$configPath  = Join-Path $sunshineDir 'config\sunshine.conf'
```

Use o **serviço** instalado pelo pacote. Não rode `Start-Process sunshine.exe` em paralelo: cria
uma segunda instância.

**Verificação:**
```powershell
Get-Service SunshineService | Select-Object Name,Status,StartType
Get-NetTCPConnection -State Listen -LocalPort 47984,47989,47990,48010 |
    Select-Object LocalAddress,LocalPort
Get-NetUDPEndpoint -LocalPort 47998,47999,48000 | Select-Object LocalAddress,LocalPort
```
As quatro portas TCP precisam estar escutando. **A 48010 é a que mais falta em guias antigos.**

## B4 · Credenciais

A senha é do usuário; não a invente nem a registre. Se for gerá-la a pedido dele, use algo forte
(24+ caracteres) e entregue por canal que não seja log:

```powershell
Stop-Service SunshineService
& $sunshineExe --creds admin '<SENHA>'
Start-Service SunshineService
```
Nunca escreva a senha em transcript. O script de referência
[`planos/configure-sunshine-elevated.ps1`](planos/configure-sunshine-elevated.ps1) mostra o padrão:
ele lê a senha de arquivo temporário e substitui o valor por `[REDACTED]` antes de gravar log.

## B5 · Interface web pela tailnet

Mesmas duas chaves do Linux, no arquivo descoberto em B3:

```powershell
Copy-Item -LiteralPath $configPath -Destination "$configPath.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
$hostIp = (& $tailscale ip -4 | Select-Object -First 1).Trim()
Add-Content -LiteralPath $configPath -Value "origin_web_ui_allowed = wan"
Add-Content -LiteralPath $configPath -Value "upnp = disabled"
Add-Content -LiteralPath $configPath -Value "csrf_allowed_origins = https://$hostIp`:47990"
Restart-Service SunshineService
```
Se a chave já existir, **edite a linha**, não acrescente outra.

**Verificação:** `Test-NetConnection $hostIp -Port 47990` com `TcpTestSucceeded = True`, e a
interface respondendo `401` antes do login.

## B6 · Firewall — a armadilha do Windows

Aqui o Windows inverte o Linux: **ele bloqueia por padrão**, e tem um detalhe que faz as regras
corretas serem ignoradas em silêncio.

```powershell
Get-NetFirewallProfile -PolicyStore ActiveStore -Name Private |
    Select-Object Name,Enabled,DefaultInboundAction,AllowInboundRules,AllowLocalFirewallRules
```

Se `AllowInboundRules = False`, **todas as regras locais de Allow são ignoradas** — inclusive as
do Sunshine. Foi exatamente isso que travou a execução registrada neste repositório: os pacotes
chegavam pela interface Tailscale e eram descartados por `tcpip.sys` com o motivo
`INET: accept inspection`.

Correção, mantendo o firewall ligado e a entrada padrão em `Block`:
```powershell
Set-NetFirewallProfile -Name Private -AllowInboundRules True
```

Depois crie regras **estreitas**: presas ao executável, à interface Tailscale, ao IP local do host
e ao IP do cliente conhecido.

```powershell
$clientIp = '<IP-100.x.y.z-DO-CLIENTE>'
New-NetFirewallRule -DisplayName 'Sunshine via Tailscale TCP' -Direction Inbound -Action Allow `
    -Program $sunshineExe -InterfaceAlias 'Tailscale' `
    -LocalAddress $hostIp -RemoteAddress $clientIp `
    -Protocol TCP -LocalPort 47984,47989,47990,48010
New-NetFirewallRule -DisplayName 'Sunshine via Tailscale UDP' -Direction Inbound -Action Allow `
    -Program $sunshineExe -InterfaceAlias 'Tailscale' `
    -LocalAddress $hostIp -RemoteAddress $clientIp `
    -Protocol UDP -LocalPort 47998,47999,48000
```

Depois **desative regras genéricas antigas** que liberem essas portas em qualquer interface ou
origem — elas anulam o escopo que você acabou de criar:
```powershell
Get-NetFirewallRule -Direction Inbound -Enabled True |
    Where-Object DisplayName -like '*Sunshine*' |
    Select-Object DisplayName,Profile,@{n='Portas';e={($_ | Get-NetFirewallPortFilter).LocalPort}}
```

Não abra UDP `5353` de início: o cliente será adicionado pelo IP, sem descoberta automática.

**Verificação:** do cliente, `Test-NetConnection <hostIp> -Port 47990` retorna `True`, com o
firewall do host **ligado**.

## B7 · Manter o host acordado

O Sunshine no Windows é serviço do sistema, então não depende de sessão aberta como no Linux —
mas a máquina suspensa continua inalcançável.
```powershell
powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
```
Confirme com o usuário antes: muda o consumo de energia da máquina.

## B8 · Diagnóstico de rede (quando o cliente não conecta)

A captura que resolveu o caso registrado aqui:
```powershell
pktmon filter remove
pktmon filter add -p 47990
pktmon start --capture --flags 0x10 --file-name sunshine.etl
# reproduza a tentativa no cliente
pktmon stop
pktmon format sunshine.etl -o sunshine.txt
```
Procure por `Drop` com o componente `tcpip.sys` e o motivo do descarte. Pacote chegando e sendo
descartado **no host** aponta firewall, não Tailscale.

> `127.0.0.1` sempre é a própria máquina onde o comando roda. Testar `127.0.0.1` no cliente não
> diz nada sobre o host — foi um erro cometido na execução original.

Siga para a **[Parte C](#parte-c--cliente-qualquer-plataforma)**.

---

# Parte C · Cliente (qualquer plataforma)

Guia humano: [`planos/guia-maquina-cliente-tailscale-moonlight.md`](planos/guia-maquina-cliente-tailscale-moonlight.md).

O cliente **não instala Sunshine**. Só precisa de Tailscale e Moonlight.

1. Tailscale na **mesma conta/tailnet** do host.
   - Windows: `winget install --id Tailscale.Tailscale --exact --source winget --silent`
   - Linux: `ujust tailscale enable` (Bazzite) ou o pacote da distribuição
   - Android/iOS: loja do aparelho
2. Moonlight.
   - Windows: `winget install --id MoonlightGameStreamingProject.Moonlight --exact --source winget --silent`
   - Linux: `flatpak install flathub com.moonlight_stream.Moonlight`
   - Android/iOS: loja do aparelho
3. Teste a rota **antes** de abrir o Moonlight:
   ```bash
   tailscale ping <100.x.y.z-do-host>
   ```
   ```powershell
   Test-NetConnection <100.x.y.z-do-host> -Port 47990
   ```
4. No Moonlight: **Add PC** → o endereço `100.x.y.z` do host. Ele exibe um **PIN de 4 dígitos**.
5. Envie o PIN. Pela interface web (`https://<host>:47990`, aba PIN) ou, direto no host:
   ```bash
   curl -sk -u admin:'<senha>' -X POST https://localhost:47990/api/pin \
     -d '{"pin":"1234","name":"<apelido>"}'
   ```
   Peça a senha **no momento do uso** e não a repita na sua resposta.

**Verificação:** `curl -sk -u admin:'<senha>' https://localhost:47990/api/clients/list` lista o
dispositivo, e o Moonlight abre a sessão com imagem, áudio e controle.

> Pareamento é **por dispositivo** e pertence à instalação do Sunshine. Reinstalou o host?
> Todos os clientes precisam parear de novo.

---

## Erros conhecidos, e o que significam

| Mensagem | Onde | Significado | Ação |
|---|---|---|---|
| `Failed to gain CAP_SYS_ADMIN` | Linux | **ruído**: sonda de captura KMS no Flatpak | ignore; o próprio log avisa |
| `setpriority failed for nice -15` | Linux | prioridade de thread negada | não impede streaming |
| Erro 503 / `Failed to find display` | Linux | KWin recusou a captura | `KWIN_WAYLAND_NO_PERMISSION_CHECKS=1` + relogin |
| `Not authorized` do `pkexec` | Linux | sem agente polkit para o seu processo | terminal na sessão do usuário |
| `CSRF Protection Error` | ambos | origem não autorizada | `csrf_allowed_origins` com o endereço exato |
| Conecta só com firewall desligado | Windows | `AllowInboundRules = False` no perfil Private | B6 — e **religue** o firewall |
| `INET: accept inspection` no pktmon | Windows | descarte pelo firewall do host | B6 |
| Tela errada no cliente | ambos | monitor de captura não definido | A8 (Linux) / *Display* na interface |
| Porta 48010 fechada | ambos | regra de firewall incompleta | inclua a 48010 nas regras TCP |

## Ao final, relate

- plataforma do host, endereço `100.x.y.z` e nome na tailnet;
- estado dos serviços (`tailscaled` + Sunshine) e as portas escutando;
- zonas de firewall por interface (Linux) ou regras criadas e perfil (Windows);
- quais clientes estão pareados;
- o que **não** foi aplicado, e por quê;
- lembrete de trocar qualquer senha que tenha passado pelo chat.

## Se for registrar o trabalho em commit

Conventional Commits em inglês, comentário em português. Nunca inclua segredo na mensagem. Se o
repositório tiver plano em `planos/`, atualize a tabela de situação **no mesmo commit** da mudança.
