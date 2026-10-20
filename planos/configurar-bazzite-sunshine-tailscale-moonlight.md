# Plano: host Bazzite com Tailscale + Sunshine para Moonlight

Guia de execução em HTML: [`guias/bazzite-host-tailscale-sunshine.html`](../guias/bazzite-host-tailscale-sunshine.html).
Este arquivo registra as decisões, as medições e o que falta executar. O guia do host Windows
continua em [`configurar-tailscale-sunshine-moonlight.md`](configurar-tailscale-sunshine-moonlight.md).

## Objetivo

Repetir no host Bazzite o que já funciona no `sammysan` (Windows): jogar remotamente por Moonlight,
com o Sunshine alcançável **somente pela tailnet**, sem port forwarding e sem porta pública.

## Topologia

- Host novo: `bazzite` — Bazzite 44.20261012.1 Kinoite, imagem `bazzite-nvidia-open`, KDE Wayland,
  RTX 4070 SUPER (driver 615.78.08), IP de LAN `192.168.0.3`, **IP de tailnet `100.89.62.103`**.
- Host antigo: `sammysan` (Windows 11), `100.78.107.32` — **continua na tailnet** (visto online há
  poucas horas em 2026-10-20), aparentemente dual boot na mesma máquina. Os dois nós nunca ficam
  online ao mesmo tempo; o IP válido para o Bazzite é o novo.
- Clientes na tailnet: `note-lat-012` (Windows, `100.114.232.6`), `iphone-12-pro-max`
  (`100.120.43.7`), `redmi-pad-se`, `realme-c61`.

## Medição do host em 2026-10-20 (somente leitura)

Comando: `bash scripts/bazzite-host-preflight.sh`.

| Item | Estado medido |
|---|---|
| Sessão | Wayland + KDE |
| Tailscale | binário 1.104.1 na imagem; `tailscaled` **disabled/inactive** |
| Sunshine | **não instalado** (flatpak `dev.lizardbyte.app.Sunshine` 2026.914.233613 disponível no Flathub) |
| Portas 47984/47989/47990/48010 TCP e 47998/47999/48000 UDP | todas fechadas (nada escutando) |
| firewalld | ativo, zona padrão `FedoraWorkstation`, só `enp5s0` ativa |
| Autologin SDDM | não configurado (`/etc/sddm.conf.d` não existe) |
| Linger do usuário | `no` |
| Monitores | DP-2 2560x1440@165, DP-1 3440x1440@165 |

## Decisões

### 1. Flatpak, não brew nem COPR

A imagem é Kinoite de desktop, não Deck. O Flatpak é o caminho suportado pelo Bazzite
(`ujust setup-sunshine` → *Enable (Flatpak)*) e não bloqueia atualização do sistema. A limitação
aceita é não transmitir o Game Mode (gamescope), que exige captura KMS — para isso só o pacote brew
experimental ou camada por COPR. Streaming do Desktop com Steam Big Picture atende o caso de uso.

### 2. O trabalho de firewall é **fechar**, não abrir

Medição decisiva: a zona padrão `FedoraWorkstation` traz
`<port protocol="tcp" port="1025-65535"/>` e o mesmo em UDP. Todas as portas do Sunshine já nascem
abertas em todas as interfaces. É o inverso exato do que ocorreu no Windows, onde o perfil `Private`
com `AllowInboundRules=False` engolia as regras Allow do Sunshine.

Consequência: nenhuma regra precisa ser criada para o Moonlight funcionar pela tailnet. O que o plano
faz é restringir a interface de LAN a uma zona nova (`lan-restrito`), deixando as portas altas
liberadas apenas onde elas realmente são usadas.

### 3. Não trocar a zona do `tailscale0`

Defeito conhecido [tailscale/tailscale#15968](https://github.com/tailscale/tailscale/issues/15968):
a partir da 1.84, mudar a zona do `tailscale0` no firewalld derruba a interface. A máquina roda
1.104.1. Por isso a restrição é aplicada na interface cabeada (`enp5s0`), pela propriedade
`connection.zone` do NetworkManager — que sobrevive a reboot —, e o `tailscale0` permanece caindo na
zona padrão.

### 4. `origin_web_ui_allowed = wan` continua necessário

Igual ao Windows, e pelo mesmo motivo: a tailnet usa `100.64.0.0/10` (CGNAT), que o Sunshine não
considera LAN. `wan` não publica nada na internet — quem limita o alcance é a ausência de port
forwarding e a etapa de firewall. `upnp = disabled` impede o roteador de abrir as portas sozinho.

### 5. `csrf_allowed_origins` com a origem exata

Mesma falha vista no `sammysan` ao enviar o PIN. A origem é `https://<ip-tailnet>:47990`, agora com
o IP do host Bazzite. Backup de `sunshine.conf` antes de editar.

### 6. Etapas que não existiam no Windows

- **Permissão de captura no Wayland**: portal/KWin Screencast, permissão "Controle remoto" no KDE e,
  se houver erro 503, `KWIN_WAYLAND_NO_PERMISSION_CHECKS=1` em `~/.config/environment.d/`.
- **Entrada remota**: `additional-install.sh` do flatpak instala as regras de `uinput`; sem ele há
  vídeo, mas não teclado/mouse/controle.
- **Serviço de usuário**: `app-dev.lizardbyte.app.Sunshine` depende de sessão gráfica aberta. Para
  ligar o PC e jogar de longe é preciso autologin no SDDM e suspensão desligada — compromisso de
  segurança física registrado no guia.
- **Multi-monitor**: o Sunshine captura uma saída; com duas telas é obrigatório fixar o *Display* ou
  usar o monitor virtual (`ujust setup-sunshine virtual-monitor`, só KWin).

### 7. Pareamento recomeça do zero

Os certificados de pareamento pertencem à instalação do Sunshine. Instalação nova, pareamento novo —
todo cliente precisa refazer o PIN, inclusive o `NOTE-LAT-012`.

## Pontos de situação

| # | Atividade | Comando | Resultado |
|---|---|---|---|
| 1 | Clonar o repositório do Windows e ler o procedimento existente | `git clone https://github.com/edilsonvilarinho/configurar-tailscale-sunshine-moonlight.git` | Feito em 2026-10-20; base dos itens reaproveitados (portas, CSRF, `origin_web_ui_allowed`) |
| 2 | Medir o host Bazzite sem alterá-lo | `bash scripts/bazzite-host-preflight.sh` | Feito; resultados na tabela acima |
| 3 | Pesquisar a documentação oficial de Bazzite, Sunshine e Tailscale | leitura de `docs.bazzite.gg`, `docs.lizardbyte.dev`, issues do Tailscale e das receitas `ujust` locais (`/usr/share/ublue-os/just/82-bazzite-sunshine.just`, `80-bazzite.just`) | Feito; decisões 1 a 7 |
| 4 | Escrever o guia HTML de instalação | — | Feito: `guias/bazzite-host-tailscale-sunshine.html` |
| 5 | Escrever os scripts de apoio | `bash -n` nos dois; dry-run do script de firewall | Feito; o dry-run detectou `enp5s0` / conexão `Conexão cabeada 1` e listou as mudanças sem aplicar |
| 6 | Habilitar `tailscaled` e autenticar | serviço ligado pelo Bazzite Portal (*Manage Bazzite → Enable Tailscale*); `sudo tailscale up --operator=edi` | Feito em 2026-10-20: host recebeu `100.89.62.103` |
| 7 | Instalar o Sunshine | `flatpak install --system flathub dev.lizardbyte.app.Sunshine` + `additional-install.sh` + `systemctl --user enable --now app-dev.lizardbyte.app.Sunshine` | Feito: versão 2026.914.233613, serviço `enabled/active`, TCP 47984/47989/47990/48010 escutando |
| 8 | `origin_web_ui_allowed`, `upnp`, `csrf_allowed_origins` | `scripts/etapa3` (ver guia, etapa 7), com backup de `sunshine.conf` | Feito: `wan`, `disabled`, `https://100.89.62.103:47990` |
| 9 | Restringir a LAN | `bash scripts/bazzite-host-firewall-tailnet.sh --apply` | Feito: zona `lan-restrito` em `enp5s0` (só `dhcpv6-client` e `mdns`); `tailscale0` ficou *no zone* ⇒ zona padrão; interface seguiu de pé |
| 10 | Credenciais da Web UI | `flatpak run --command=sunshine dev.lizardbyte.app.Sunshine --creds admin '<senha>'` | Feito: usuário `admin`. **A senha escolhida é fraca e igual à do sistema — trocar** |
| 11 | Monitor capturado | `output_name = DP-1` em `sunshine.conf` | Feito: antes pegava o primeiro stream (DP-2, 2560x1440); agora `Streaming display 'DP-1' resolution: 3440x1440` |
| 12 | Aplicações | entrada "Steam Big Picture" em `apps.json` com `flatpak-spawn --host setsid steam steam://open/bigpicture` | Feito: API lista `Desktop` e `Steam Big Picture` |
| 13 | Suspensão e linger | `systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target`; `loginctl enable-linger edi` | Feito |
| 14 | Autologin | `/etc/sddm.conf.d/10-autologin.conf` com `User=edi`, `Session=plasma.desktop` | Feito a pedido do usuário; compromisso de segurança física aceito |
| 15 | Validar a Web UI pelo IP da tailnet | `curl -sk https://100.89.62.103:47990/` e com `-u admin:<senha>` | Feito: `401` sem credencial, `200` com credencial, API lista as duas aplicações |
| 16 | Parear um cliente e validar a sessão | pareamento pelo Moonlight do iPhone (`iphone-12-pro-max`, `100.120.43.7`) | Feito em 2026-10-20 14:46: certificado `iphone` registrado, `CLIENT CONNECTED`, `Streaming display 'DP-1' 3440x1440`, `hevc_nvenc`, bitrate 14.988 Mbps, Opus 48 kHz 2 canais; conexão Tailscale **direta** (sem DERP). Sessão encerrada pelo usuário após 6 s |

## Regras de segurança do procedimento

- Nenhuma senha, token ou PIN entra neste repositório, em log ou em issue.
- Nenhum port forwarding, nenhuma porta pública, firewall nunca desativado como "solução".
- Backup de `sunshine.conf` antes de qualquer edição.
- Ampliar o acesso dentro da tailnet é decisão explícita (ACL do Tailscale), não efeito colateral.

## Pendências conhecidas

- **Senhas a trocar**: a senha do sistema foi digitada em um canal de conversa durante a execução, e
  a credencial da Web UI do Sunshine (`admin`) foi definida com o mesmo valor, de 6 dígitos. Trocar
  as duas, com valores diferentes entre si.
- **Prioridade de thread**: o log repete `setpriority failed for nice -15: Permissão negada` e
  `EGL: context priority set to HIGH but CAP_SYS_NICE capability is missing`. Não impede o
  streaming; sob carga pode custar frames. Correção seria elevar o limite de `nice` do usuário
  (`/etc/security/limits.d/`), ainda não avaliada.
- **Teste longo**: a validação durou 6 s, encerrada pelo usuário. Falta uma sessão real de jogo para
  julgar estabilidade, latência e reconexão.
- **Clientes restantes**: `note-lat-012`, `redmi-pad-se` e `realme-c61` ainda não foram pareados com
  esta instalação — o pareamento é por dispositivo.

## Observações da execução (2026-10-20)

- **`pkexec` não serve para este fluxo.** Rodado a partir do shell do agente, o polkit responde
  `Not authorized` sem abrir diálogo, porque o processo não está atrelado ao agente de autenticação
  da sessão KDE. O que funcionou foi abrir um `konsole` na sessão do usuário (`setsid konsole -e bash <script>`)
  e deixar o `sudo` pedir a senha lá, numa janela de verdade.
- **O log do Sunshine mente sobre a gravidade.** `Failed to gain CAP_SYS_ADMIN` aparece quatro vezes
  no arranque e é inofensivo — é a sonda de captura KMS falhando no Flatpak; o próprio log encerra o
  bloco com `// Ignore any errors mentioned above, they are not relevant. //`. A captura real sai por
  PipeWire/portal e os encoders NVENC (H.264, HEVC, AV1) foram todos encontrados.
- **Sem `output_name`, o Sunshine pega "o primeiro stream disponível"**, não o monitor principal.
  Em máquina com duas telas isso é silencioso: nada falha, só chega a tela errada no cliente.
- **A Web UI não precisou ser aberta no cliente para parear**: o PIN pode ser enviado por
  `POST /api/pin` com as credenciais, o que evita o passo mais frágil do procedimento do Windows
  (o erro de CSRF). A configuração de `csrf_allowed_origins` foi mantida porque a Web UI pelo
  navegador continua sendo o caminho normal.
