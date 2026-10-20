# -*- coding: utf-8 -*-
"""Roteiro do vídeo-tutorial: Tailscale + Sunshine no Bazzite.

Fonte única de verdade. O renderizador (gerar_video.py) lê estas listas.

Cada cena tem:
  id      identificador curto, vira nome de pasta intermediária
  kind    title | bullets | terminal | compare | table
  titulo  texto grande na tela
  sub     linha de apoio (opcional)
  fala    narração, escrita para ser LIDA EM VOZ ALTA: número por extenso,
          sem ler comando longo literalmente, frase curta
  corpo   conteúdo visual; o formato depende de kind:
            bullets  -> lista de strings
            terminal -> lista de ("cmd" | "out" | "note", texto)
            compare  -> (título_esq, [linhas], título_dir, [linhas])
            table    -> lista de (rótulo, valor)
  hold    segundos de respiro no fim da cena, além da narração
"""


def S(id, kind, titulo, fala, sub="", corpo=None, hold=1.2):
    return {
        "id": id, "kind": kind, "titulo": titulo, "sub": sub,
        "fala": " ".join(fala.split()), "corpo": corpo or [], "hold": hold,
    }


# ---------------------------------------------------------------------------
# CORTE LONGO — YouTube (16:9)
# ---------------------------------------------------------------------------

LONGO = [
    S("01-abertura", "title",
      "Seu PC de casa, jogando longe de casa",
      """Imagina sair de casa, abrir o celular ou o notebook, e continuar jogando os jogos que
         estão instalados no seu computador. Não é nuvem paga, não é assinatura: é o seu próprio
         PC, com a sua própria placa de vídeo. Neste tutorial a gente monta isso do zero no
         Bazzite, passo a passo, com todos os comandos na tela. E o mais importante: sem abrir
         uma única porta para a internet.""",
      sub="Tailscale + Sunshine + Moonlight · tutorial completo",
      hold=1.6),

    S("02-bazzite", "bullets",
      "Primeiro: que sistema é esse",
      """O Bazzite é uma distribuição Linux feita para jogos, construída em cima do Fedora.
         A diferença grande é que ele é um sistema atômico: a base é uma imagem somente leitura,
         que atualiza inteira de uma vez. Isso deixa o sistema difícil de quebrar, mas também
         muda a forma de instalar programas. Aqui a gente está na versão quarenta e quatro,
         variante Kinoite, que é a com KDE Plasma, e na imagem com drivers NVIDIA abertos.""",
      sub="Bazzite 44 · Kinoite · bazzite-nvidia-open",
      corpo=[
          "Base Fedora 44, sistema atômico (imagem somente leitura)",
          "Kinoite = ambiente KDE Plasma, sessão Wayland",
          "Imagem bazzite-nvidia-open: driver NVIDIA já incluso",
          "Programas entram por Flatpak, não por instalador avulso",
          "ujust = receitas de configuração que o Bazzite já traz prontas",
      ],
      hold=1.6),

    S("03-pecas", "bullets",
      "As três peças e o papel de cada uma",
      """São três programas, e é importante não confundir. O Sunshine fica no computador que tem
         os jogos: ele captura a tela, comprime usando a placa de vídeo, e envia. O Moonlight fica
         no aparelho que você leva na mão: celular, tablet ou notebook. E a Tailscale é a rede
         privada que liga os dois, como se estivessem na mesma sala, mesmo que um esteja a mil
         quilômetros do outro.""",
      sub="Quem faz o quê",
      corpo=[
          "SUNSHINE  »  no PC com os jogos: captura, codifica e envia",
          "MOONLIGHT  »  no aparelho que recebe: celular, tablet, notebook",
          "TAILSCALE  »  a rede privada que liga os dois com segurança",
      ],
      hold=1.6),

    S("04-seguranca", "compare",
      "Por que Tailscale, e não abrir porta no roteador",
      """Muito tutorial de streaming manda abrir porta no roteador. Não faça isso. Uma porta aberta
         fica exposta para o mundo inteiro, e qualquer um pode bater nela o dia todo. A Tailscale
         cria uma rede privada criptografada entre os seus aparelhos: de fora, não existe porta
         nenhuma para encontrar. E de quebra o endereço do seu PC passa a ser fixo, mesmo que o
         seu provedor troque o IP da sua casa.""",
      sub="Duas formas de chegar no seu PC",
      corpo=("Abrir porta no roteador", [
                 "Exposto para a internet inteira",
                 "Varredura automática acha em horas",
                 "Depende de IP fixo ou DNS dinâmico",
                 "Quebra se o provedor usar CGNAT",
             ], "Rede privada Tailscale", [
                 "Nada visível de fora da rede",
                 "Tráfego criptografado ponta a ponta",
                 "Endereço fixo, começando com 100.",
                 "Funciona mesmo atrás de CGNAT",
             ]),
      hold=1.8),

    S("05-prevalidacao", "terminal",
      "Passo zero: olhar antes de tocar",
      """Antes de instalar qualquer coisa, vale olhar o terreno. Estes comandos não mudam nada no
         sistema: só mostram o estado. Qual versão do Bazzite, se a sessão é Wayland, qual placa
         de vídeo, e se a Tailscale já está ligada. Guarde essa saída. Se alguma coisa der errado
         lá na frente, é com ela que você compara.""",
      sub="Nenhum destes comandos altera o sistema",
      corpo=[
          ("cmd", "grep -E '^(PRETTY_NAME|VARIANT_ID)=' /etc/os-release"),
          ("out", 'PRETTY_NAME="Bazzite"'),
          ("out", "VARIANT_ID=bazzite-nvidia-open"),
          ("cmd", "echo $XDG_SESSION_TYPE $XDG_CURRENT_DESKTOP"),
          ("out", "wayland KDE"),
          ("cmd", "nvidia-smi --query-gpu=name --format=csv,noheader"),
          ("out", "NVIDIA GeForce RTX 4070 SUPER"),
          ("cmd", "systemctl is-enabled tailscaled"),
          ("out", "disabled"),
      ],
      hold=1.8),

    S("06-tailscale", "terminal",
      "Passo 1: ligar a Tailscale",
      """Boa notícia: no Bazzite a Tailscale já vem instalada, só está desligada. O comando ujust
         tailscale enable liga o serviço. Depois, o tailscale up faz o login. Ele vai imprimir um
         link; você abre esse link no navegador e aprova o computador na sua conta. O parâmetro
         operator é um detalhe que poupa trabalho: ele deixa você consultar a Tailscale depois sem
         pedir senha de administrador toda vez.""",
      sub="O binário já vem na imagem; falta habilitar e autenticar",
      corpo=[
          ("note", "# pela interface: Bazzite Portal > Manage Bazzite > Enable Tailscale"),
          ("cmd", "ujust tailscale enable"),
          ("out", "Created symlink .../tailscaled.service"),
          ("cmd", "sudo tailscale up --operator=$USER"),
          ("out", "To authenticate, visit:"),
          ("out", "    https://login.tailscale.com/a/8f3c21d0e4b7"),
          ("cmd", "tailscale ip -4"),
          ("out", "100.89.62.103"),
          ("note", "# anote esse endereço: é por ele que o celular chega no PC"),
      ],
      hold=2.0),

    S("07-sunshine", "terminal",
      "Passo 2: instalar o Sunshine",
      """Agora o Sunshine. No Bazzite o caminho recomendado é o Flatpak, e existe uma receita
         pronta: ujust setup-sunshine. Escolha a opção Enable Flatpak. Ela faz três coisas:
         instala o programa, roda um script de permissões extras, e liga o serviço. Preste atenção
         nesse script do meio, o additional install. É ele que instala as permissões de teclado,
         mouse e controle. Sem ele você até vê a imagem, mas não consegue clicar em nada.""",
      sub="ujust setup-sunshine » Enable (Flatpak)",
      corpo=[
          ("cmd", "ujust setup-sunshine"),
          ("out", "> Enable (Flatpak)"),
          ("note", "# o que a receita executa por baixo:"),
          ("cmd", "flatpak install --system -y dev.lizardbyte.app.Sunshine"),
          ("cmd", "flatpak run --command=additional-install.sh dev.lizardbyte.app.Sunshine"),
          ("note", "#    ↑ permissões de uinput: teclado, mouse e controle"),
          ("cmd", "systemctl --user enable --now app-dev.lizardbyte.app.Sunshine"),
          ("cmd", "ss -ltn | grep -E ':(47984|47989|47990|48010) '"),
          ("out", "LISTEN  0  4096  0.0.0.0:47990   0.0.0.0:*"),
          ("out", "LISTEN  0  4096  0.0.0.0:48010   0.0.0.0:*"),
      ],
      hold=2.0),

    S("08-wayland", "bullets",
      "Passo 3: a permissão que o Linux exige",
      """Este passo não existe no Windows, e é onde mais gente trava. No Wayland, nenhum programa
         captura a tela sem autorização explícita. Na primeira vez que o Sunshine tentar, o KDE vai
         perguntar: aceite, e marque para lembrar. Depois, confira nas configurações do sistema que
         o Sunshine tem a permissão de controle remoto. Se mesmo assim aparecer o erro quinhentos
         e três, existe uma variável de ambiente que resolve, e ela só vale depois de sair e entrar
         na sessão de novo.""",
      sub="O Wayland não deixa ninguém capturar a tela às escondidas",
      corpo=[
          "1. Aceitar o pedido de compartilhamento de tela do KDE, marcando “lembrar”",
          "2. Configurações » Aplicativos » Permissões: ligar “Controle remoto”",
          "3. Na interface do Sunshine, usar captura KWin Screencast",
          "4. Erro 503? KWIN_WAYLAND_NO_PERMISSION_CHECKS=1",
          "    em ~/.config/environment.d/ — e sair e entrar na sessão",
          "X11 e NvFBC não funcionam no Bazzite. Não perca tempo com eles.",
      ],
      hold=1.8),

    S("09-credenciais", "terminal",
      "Passo 4: criar a senha do Sunshine",
      """Com o serviço no ar, abra a interface web na própria máquina, no endereço local, porta
         quarenta e sete mil novecentos e noventa. O aviso de certificado é normal: o certificado
         é gerado pelo próprio Sunshine. Crie o usuário e uma senha forte. E vai um conselho que
         vale ouro: não use a mesma senha do seu sistema, e não use seis dígitos. Essa senha
         protege o controle total do seu computador.""",
      sub="https://localhost:47990",
      corpo=[
          ("cmd", "xdg-open https://localhost:47990"),
          ("note", "# aviso de certificado: esperado, ele é autoassinado"),
          ("note", "# crie usuário e senha forte na tela que abrir"),
          ("note", ""),
          ("note", "# para redefinir depois, pela linha de comando:"),
          ("cmd", "systemctl --user stop app-dev.lizardbyte.app.Sunshine"),
          ("cmd", "flatpak run --command=sunshine dev.lizardbyte.app.Sunshine \\"),
          ("cmd", "    --creds admin 'SUA-SENHA-FORTE'"),
          ("cmd", "systemctl --user start app-dev.lizardbyte.app.Sunshine"),
      ],
      hold=1.8),

    S("10-webui", "terminal",
      "Passo 5: liberar a interface pela rede privada",
      """Aqui tem duas pegadinhas do próprio Sunshine. A primeira: por padrão ele só aceita a
         interface web vinda da rede local, e o endereço da Tailscale não conta como rede local.
         A segunda: na hora de enviar o código de pareamento, ele recusa origens que não conhece,
         com um erro de CSRF. As duas se resolvem no arquivo de configuração. Repare que a gente
         faz cópia de segurança antes de editar, e reinicia o serviço depois.""",
      sub="origin_web_ui_allowed e csrf_allowed_origins",
      corpo=[
          ("cmd", "CONF=~/.var/app/dev.lizardbyte.app.Sunshine/config/sunshine/sunshine.conf"),
          ("cmd", "cp -a \"$CONF\" \"$CONF.backup-$(date +%Y%m%d-%H%M%S)\""),
          ("cmd", "IP=$(tailscale ip -4)"),
          ("cmd", "printf 'origin_web_ui_allowed = wan\\nupnp = disabled\\n' >> \"$CONF\""),
          ("cmd", "printf 'csrf_allowed_origins = https://%s:47990\\n' \"$IP\" >> \"$CONF\""),
          ("cmd", "systemctl --user restart app-dev.lizardbyte.app.Sunshine"),
          ("note", "# “wan” não publica nada na internet: só desliga o filtro"),
          ("note", "# por faixa de IP. Quem limita o alcance é o firewall."),
      ],
      hold=2.0),

    S("11-firewall-conceito", "compare",
      "Passo 6: o firewall, e a surpresa do Linux",
      """Este passo é o mais interessante do tutorial, porque ele inverte em relação ao Windows.
         No Windows, você briga para abrir as portas do Sunshine. No Bazzite, a zona padrão do
         firewall já deixa todas essas portas abertas, em qualquer interface de rede. Ou seja: não
         falta abrir nada. Falta fechar. O trabalho aqui é tirar o Sunshine da rede de casa e
         deixar ele só na rede privada.""",
      sub="O trabalho não é abrir porta: é fechar",
      corpo=("No Windows", [
                 "Firewall bloqueia por padrão",
                 "Você cria regras para liberar",
                 "Perfil errado engole as regras",
                 "Sintoma: não conecta de jeito nenhum",
             ], "No Bazzite", [
                 "Zona FedoraWorkstation já libera",
                 "TCP e UDP de 1025 até 65535",
                 "Vale para todas as interfaces",
                 "Sintoma: aberto demais, até na LAN",
             ]),
      hold=2.0),

    S("12-firewall-comandos", "terminal",
      "Fechando o Sunshine para a rede de casa",
      """A estratégia é simples. A interface da Tailscale fica na zona padrão, que é permissiva, e
         por isso o streaming funciona. Já a placa de rede de casa vai para uma zona nova,
         restrita, que não abre essas portas. E tem um detalhe que pode te custar uma tarde: não
         mexa na zona da interface da Tailscale. Existe um defeito conhecido em que trocar a zona
         dela derruba a conexão. A gente simplesmente não toca nela.""",
      sub="Zona restrita na placa de casa; a interface da Tailscale não se toca",
      corpo=[
          ("cmd", "sudo firewall-cmd --permanent --new-zone=lan-restrito"),
          ("cmd", "sudo firewall-cmd --permanent --zone=lan-restrito --add-service=mdns"),
          ("cmd", "sudo firewall-cmd --reload"),
          ("note", "# prende a zona na conexão, para sobreviver a reboot:"),
          ("cmd", "sudo nmcli connection modify 'Conexão cabeada 1' \\"),
          ("cmd", "     connection.zone lan-restrito"),
          ("cmd", "sudo nmcli connection up 'Conexão cabeada 1'"),
          ("cmd", "firewall-cmd --get-zone-of-interface=tailscale0"),
          ("out", "no zone   ← fica na zona padrão, e é assim que deve ficar"),
      ],
      hold=2.0),

    S("13-monitor", "terminal",
      "Passo 7: escolher o monitor certo",
      """Se você tem mais de um monitor, preste atenção neste passo, porque o erro aqui é
         silencioso. Sem configurar, o Sunshine pega o primeiro fluxo que aparecer, que pode não
         ser a sua tela principal. Nada falha, nenhum erro aparece: só chega a tela errada no
         celular. O nome do monitor você descobre no próprio log do Sunshine, e fixa no arquivo
         de configuração.""",
      sub="Sem output_name, o monitor capturado é sorteado",
      corpo=[
          ("cmd", "grep '\\[wayland\\] Name' .../sunshine.log | tail -2"),
          ("out", "Info: [wayland] Name: DP-1"),
          ("out", "Info: [wayland] Name: DP-2"),
          ("cmd", "echo 'output_name = DP-1' >> \"$CONF\""),
          ("cmd", "systemctl --user restart app-dev.lizardbyte.app.Sunshine"),
          ("cmd", "grep 'Streaming display' .../sunshine.log | tail -1"),
          ("out", "[pipewire] Streaming display 'DP-1' resolution: 3440x1440"),
      ],
      hold=1.8),

    S("14-sempre-pronto", "terminal",
      "Passo 8: o PC pronto mesmo sem ninguém na frente",
      """Tem um detalhe do Linux que pega todo mundo: no Bazzite o Sunshine roda como serviço do
         seu usuário, e a captura depende da sessão gráfica estar aberta. Se o computador
         reiniciar e ninguém logar, não existe tela para capturar. Então, se a ideia é ligar o PC
         de longe, ligue o login automático. É uma troca consciente: quem estiver fisicamente na
         frente da máquina entra sem senha. Também vale impedir que o computador durma sozinho.""",
      sub="Login automático, nada de suspender, serviço vivo",
      corpo=[
          ("note", "# 1. login automático no KDE"),
          ("cmd", "sudo tee /etc/sddm.conf.d/10-autologin.conf <<'EOF'"),
          ("out", "[Autologin]"),
          ("out", "User=edi"),
          ("out", "Session=plasma.desktop"),
          ("out", "EOF"),
          ("note", "# 2. não suspender, senão você perde o acesso remoto"),
          ("cmd", "sudo systemctl mask sleep.target suspend.target hibernate.target"),
          ("note", "# 3. manter o serviço do usuário vivo entre sessões"),
          ("cmd", "loginctl enable-linger $USER"),
      ],
      hold=1.8),

    S("15-cliente", "bullets",
      "Passo 9: o aparelho que vai receber",
      """No aparelho é rápido. Instale a Tailscale e entre na mesma conta, instale o Moonlight, e
         adicione o PC pelo endereço que começa com cem. O Moonlight vai mostrar um código de
         quatro dígitos, e esse código precisa ser informado no Sunshine. Dá para fazer pela
         interface web, ou, se preferir, direto pela linha de comando do computador, com uma
         chamada de API. Esse atalho evita o erro de CSRF de uma vez por todas.""",
      sub="Celular, tablet ou notebook: Tailscale + Moonlight",
      corpo=[
          "1. Instalar a Tailscale e entrar na MESMA conta do PC",
          "2. Instalar o Moonlight (loja do aparelho, ou flatpak no Linux)",
          "3. Add PC  »  digitar o endereço 100.x.x.x do computador",
          "4. O Moonlight mostra um PIN de quatro dígitos",
          "5. Enviar o PIN pela interface web, ou pela API do host:",
          "    curl -sk -u admin:SENHA -X POST \\",
          "      https://localhost:47990/api/pin -d '{\"pin\":\"1234\"}'",
      ],
      hold=1.8),

    S("16-resultado", "table",
      "O resultado, medido de verdade",
      """Esses números não são estimativa: saíram do log da instalação que serviu de base para
         este tutorial. Um iPhone, fora de casa, conectou direto no PC, sem passar por servidor
         intermediário, recebendo três mil quatrocentos e quarenta por mil quatrocentos e
         quarenta, com vídeo em HEVC codificado pela própria placa NVIDIA, e áudio digital.""",
      sub="Primeira sessão real, host Bazzite",
      corpo=[
          ("Endereço do host", "100.89.62.103 — rede privada Tailscale"),
          ("Cliente", "iPhone, conexão DIRETA (sem relay)"),
          ("Vídeo", "HEVC por NVENC, 3440x1440"),
          ("Taxa", "15 Mbps, cadência de 60 quadros por segundo"),
          ("Áudio", "Opus 48 kHz, dois canais"),
          ("Porta aberta na internet", "nenhuma"),
      ],
      hold=2.0),

    S("17-erros", "table",
      "Os quatro erros que você provavelmente vai ver",
      """Para fechar, os tropeços mais comuns, com a causa de cada um. Erro quinhentos e três é
         permissão de captura. Erro de CSRF é origem não autorizada. Imagem sem mouse é o script
         de permissões que não rodou. Tela errada é monitor não escolhido. E o aviso de
         CAP_SYS_ADMIN, que assusta, é só ruído. Vale pausar o vídeo aqui e guardar esta tela:
         ela economiza horas de procura em fórum.""",
      sub="Sintoma  »  causa e solução",
      corpo=[
          ("Erro 503, sem display", "o KWin recusou a captura: variável "
                                    "KWIN_WAYLAND_NO_PERMISSION_CHECKS e relogin"),
          ("CSRF Protection Error", "origem não autorizada: csrf_allowed_origins "
                                    "com o endereço exato"),
          ("Imagem sim, mouse não", "faltou rodar o additional-install.sh (uinput)"),
          ("Chegou a tela errada", "output_name não definido, com dois monitores"),
          ("Failed to gain CAP_SYS_ADMIN", "ruído: é a sonda de captura KMS. Pode ignorar"),
      ],
      hold=6.0),

    S("18-fecho", "title",
      "Guia completo, comandos e scripts",
      """Todo o passo a passo deste vídeo, com os comandos prontos para copiar, mais dois scripts
         de apoio, estão no repositório no link da descrição. Tem um script que valida a máquina
         antes de você mexer em qualquer coisa, e outro que aplica a parte do firewall, com um
         modo de simulação para você ver o que ele faria antes de aplicar de verdade. Se este
         vídeo te ajudou, deixa o like e comenta qual aparelho você vai usar para jogar.
         Até a próxima.""",
      sub="github.com/edilsonvilarinho/configurar-tailscale-sunshine-moonlight",
      hold=2.4),
]


# ---------------------------------------------------------------------------
# CORTE CURTO — Shorts / TikTok / Reels (9:16)
# ---------------------------------------------------------------------------

def _curto(cta_fala, cta_texto):
    return [
        S("c1-hook", "title",
          "Jogue o PC de casa, de qualquer lugar",
          """Dá para jogar os jogos do seu PC no celular, de qualquer lugar do mundo, sem abrir
             nenhuma porta para a internet. No Bazzite, em três passos.""",
          sub="Bazzite 44 · sem abrir porta no roteador", hold=0.8),

        S("c2-pecas", "bullets",
          "Três peças",
          """Sunshine no PC que tem os jogos. Moonlight no aparelho que recebe. E a Tailscale,
             que liga os dois numa rede privada, como se estivessem lado a lado.""",
          corpo=["SUNSHINE  no PC dos jogos",
                 "MOONLIGHT  no celular",
                 "TAILSCALE  a rede privada entre eles"], hold=0.8),

        S("c3-comandos", "terminal",
          "Dois comandos",
          """No Bazzite é quase pronto: a Tailscale já vem instalada, e o Sunshine tem receita
             pronta. Dois comandos, e um login no navegador.""",
          corpo=[("cmd", "ujust tailscale enable"),
                 ("cmd", "sudo tailscale up --operator=$USER"),
                 ("cmd", "ujust setup-sunshine"),
                 ("out", "> Enable (Flatpak)")], hold=0.8),

        S("c4-pegadinha", "bullets",
          "A pegadinha",
          """Agora a parte que quase ninguém conta: no Linux o firewall já deixa essas portas
             abertas. O trabalho não é abrir, é fechar. Você manda a placa de rede de casa para
             uma zona restrita, e deixa passar só a rede privada.""",
          sub="No Linux, o trabalho é fechar",
          corpo=["Zona padrão já libera TCP e UDP 1025-65535",
                 "Em TODAS as interfaces, inclusive a de casa",
                 "Solução: placa da LAN numa zona restrita",
                 "E nunca mexer na interface da Tailscale"], hold=0.8),

        S("c5-resultado", "table",
          "O resultado",
          """Resultado medido: iPhone conectando direto no PC, três mil quatrocentos e quarenta
             por mil quatrocentos e quarenta, em HEVC pela NVIDIA.""",
          corpo=[("Vídeo", "HEVC NVENC, 3440x1440"),
                 ("Conexão", "direta, sem relay"),
                 ("Porta exposta", "nenhuma")], hold=0.8),

        S("c6-cta", "title", "Guia completo, passo a passo", cta_fala,
          sub=cta_texto, hold=1.5),
    ]


CURTO_YOUTUBE = _curto(
    "O passo a passo completo, com todos os comandos, está no link da descrição.",
    "Link na descrição")
CURTO_TIKTOK = _curto(
    "O passo a passo completo, com todos os comandos, está no link do perfil. "
    "Me segue que tem mais.",
    "Link no perfil")
CURTO_INSTAGRAM = _curto(
    "O passo a passo completo, com todos os comandos, está no link da bio. "
    "Salva esse vídeo para não perder.",
    "Link na bio · salva o post")


# ---------------------------------------------------------------------------
# CORTE LINKEDIN (1:1)
# ---------------------------------------------------------------------------

LINKEDIN = [
    S("l1-abertura", "title",
      "Acesso remoto seguro, sem expor porta",
      """Montei um host de streaming de jogos em Linux com uma regra inegociável: nenhuma porta
         exposta na internet. O caminho foi Tailscale mais Sunshine, num Bazzite quarenta e
         quatro. Compartilho aqui o desenho, e as três armadilhas que encontrei.""",
      sub="Bazzite 44 · Tailscale · Sunshine", hold=1.2),

    S("l2-desenho", "bullets",
      "O desenho",
      """O desenho é simples, e vale para qualquer serviço interno, não só para jogos. A interface
         da rede privada fica numa zona de firewall permissiva, e a placa física vai para uma zona
         restrita. O serviço escuta normalmente, mas só é alcançável por quem está na rede
         privada.""",
      corpo=["O serviço escuta localmente, como de costume",
             "Interface da rede privada: zona permissiva",
             "Placa física da LAN: zona restrita",
             "Resultado: alcançável só pela tailnet, zero port forwarding"], hold=1.2),

    S("l3-inversao", "compare",
      "A inversão que surpreende",
      """A surpresa foi o firewall. Quem vem do Windows espera lutar para abrir portas. No Fedora
         e derivados, a zona padrão já libera a faixa alta inteira, em todas as interfaces. O
         trabalho de segurança não é abrir: é fechar, de forma seletiva.""",
      corpo=("Expectativa (Windows)", ["O firewall bloqueia",
                                       "Criar regra para liberar"],
             "Realidade (Fedora e Bazzite)", ["Zona padrão já libera 1025-65535",
                                              "Em todas as interfaces",
                                              "Fechar é o trabalho real"]),
      hold=1.4),

    S("l4-armadilhas", "table",
      "Três armadilhas que custaram tempo",
      """Três aprendizados que valem para quem automatiza Linux. Primeiro: pkexec não funciona a
         partir de um shell automatizado, porque não há agente de autenticação atrelado àquele
         processo. Segundo: nem todo erro no log é erro de verdade. Terceiro: configuração
         faltando nem sempre falha. Às vezes ela só escolhe errado, em silêncio.""",
      corpo=[("pkexec automatizado", "o polkit nega sem diálogo: não há agente "
                                     "para aquele processo"),
             ("Log alarmista", "CAP_SYS_ADMIN é sonda de captura; o próprio log "
                               "manda ignorar"),
             ("Falha silenciosa", "sem output_name, o monitor capturado é o "
                                  "primeiro da lista")],
      hold=1.6),

    S("l5-fecho", "title",
      "Documentado e publicado",
      """Documentei tudo em guia aberto, com scripts de validação e de firewall, incluindo modo de
         simulação antes de aplicar. Link nos comentários. Se você resolve esse tipo de problema
         de outro jeito, me conta: tenho interesse genuíno na comparação.""",
      sub="Guia, scripts e decisões no repositório", hold=1.6),
]


CORTES = {
    "youtube-longo":   {"cenas": LONGO,           "aspecto": (1920, 1080)},
    "youtube-shorts":  {"cenas": CURTO_YOUTUBE,   "aspecto": (1080, 1920)},
    "tiktok":          {"cenas": CURTO_TIKTOK,    "aspecto": (1080, 1920)},
    "instagram-reels": {"cenas": CURTO_INSTAGRAM, "aspecto": (1080, 1920)},
    "instagram-feed":  {"cenas": CURTO_INSTAGRAM, "aspecto": (1080, 1350)},
    "linkedin":        {"cenas": LINKEDIN,        "aspecto": (1080, 1080)},
}
