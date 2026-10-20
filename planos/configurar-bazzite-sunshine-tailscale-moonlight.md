# Plano: host Bazzite com Tailscale + Sunshine para Moonlight

Guia de execução em HTML: [`guias/bazzite-host-tailscale-sunshine.html`](../guias/bazzite-host-tailscale-sunshine.html).
Este arquivo registra as decisões, as medições e o que falta executar. O guia do host Windows
continua em [`configurar-tailscale-sunshine-moonlight.md`](configurar-tailscale-sunshine-moonlight.md).

## Objetivo

Repetir no host Bazzite o que já funciona no `sammysan` (Windows): jogar remotamente por Moonlight,
com o Sunshine alcançável **somente pela tailnet**, sem port forwarding e sem porta pública.

## Topologia

- Host novo: `bazzite` — Bazzite 44.20261012.1 Kinoite, imagem `bazzite-nvidia-open`, KDE Wayland,
  RTX 4070 SUPER (driver 615.78.08), IP de LAN `192.168.0.3`.
- Host antigo: `sammysan` (Windows 11), IP de tailnet `100.78.107.32` — **obsoleto** se a máquina foi
  reinstalada; o nó Bazzite entra na tailnet com IP próprio.
- Cliente: `NOTE-LAT-012` (Windows), já com Tailscale e Moonlight do guia anterior.

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
| 6 | Habilitar `tailscaled` e autenticar | `ujust tailscale enable` + `sudo tailscale up --operator="$USER"` | **Pendente** — exige senha de `sudo` e aprovação no navegador |
| 7 | Instalar o Sunshine e permissões de captura | `ujust setup-sunshine` | **Pendente** — exige senha e interação com o portal do KDE |
| 8 | Credenciais, `wan` e `csrf_allowed_origins` | ver guia, etapas 6 e 7 | **Pendente** |
| 9 | Restringir a LAN | `bash scripts/bazzite-host-firewall-tailnet.sh --apply` | **Pendente** |
| 10 | Autologin, suspensão e linger | ver guia, etapa 9 | **Pendente** |
| 11 | Parear o cliente e validar a sessão | ver guia, etapas 10 e 11 | **Pendente** |

## Regras de segurança do procedimento

- Nenhuma senha, token ou PIN entra neste repositório, em log ou em issue.
- Nenhum port forwarding, nenhuma porta pública, firewall nunca desativado como "solução".
- Backup de `sunshine.conf` antes de qualquer edição.
- Ampliar o acesso dentro da tailnet é decisão explícita (ACL do Tailscale), não efeito colateral.
