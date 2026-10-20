# Material de publicação

Texto pronto para copiar. O link citado em todos é o repositório:
`https://github.com/edilsonvilarinho/configurar-tailscale-sunshine-moonlight`

Os vídeos estão em [`render/`](render/). Cada plataforma tem o seu corte — não reaproveite o 16:9
no Reels nem o vertical no YouTube: a proporção errada corta texto e derruba o alcance.

---

# 1. YouTube — vídeo longo

**Arquivo:** `render/youtube-longo.mp4` (1920×1080, 8min21)
**Legenda:** `render/youtube-longo.srt` (subir junto; o vídeo 16:9 não tem legenda queimada)
**Miniatura:** `render/youtube-thumb.png`

## Título (escolha um)

1. `Jogue os jogos do seu PC de QUALQUER lugar — Bazzite + Sunshine + Tailscale`
2. `Streaming de jogos no Linux sem abrir porta no roteador | Bazzite 44 passo a passo`
3. `Transforme seu PC Linux em servidor de jogos remoto (tutorial completo)`
4. `O erro de firewall que ninguém conta no streaming de jogos em Linux`

O primeiro é o mais clicável. O quarto é melhor se o canal já tem público técnico.

## Descrição

```
Neste tutorial a gente transforma um PC com Bazzite 44 num servidor de jogos remoto, para jogar
no celular, no tablet ou em outro notebook — de qualquer lugar do mundo, sem abrir nenhuma porta
no roteador e sem pagar serviço de nuvem.

São três peças: o Sunshine transmite, o Moonlight recebe, e a Tailscale faz a rede privada entre
os dois. Mostro todos os comandos na tela, incluindo as armadilhas que só aparecem no Linux e que
nenhum tutorial de Windows cobre:

• a permissão de captura do Wayland (o famoso erro 503);
• o serviço de usuário, que depende da sessão gráfica estar aberta;
• e o firewall — que no Linux funciona ao contrário do que você espera. No Windows você luta para
  abrir as portas; no Fedora e derivados a zona padrão já libera a faixa alta inteira, em todas as
  interfaces. O trabalho não é abrir: é fechar.

Resultado medido na instalação que serviu de base para este vídeo: um iPhone conectando direto no
PC, sem servidor intermediário, recebendo 3440x1440 em HEVC codificado pela própria NVIDIA, com
áudio digital, e nenhuma porta exposta na internet.

⚙️ GUIA ESCRITO, COM TODOS OS COMANDOS PARA COPIAR
https://github.com/edilsonvilarinho/configurar-tailscale-sunshine-moonlight

Inclui dois scripts: um que valida a máquina antes de você mexer em qualquer coisa, e outro que
aplica a parte do firewall com modo de simulação, para você ver o que ele faria antes de aplicar.

📋 O QUE VOCÊ PRECISA
• Um PC com Bazzite (usei a versão 44 Kinoite, imagem bazzite-nvidia-open)
• Uma conta gratuita na Tailscale
• Um celular, tablet ou notebook para receber a transmissão

⏱️ CAPÍTULOS
0:00 Seu PC de casa, jogando longe de casa
0:24 Primeiro: que sistema é esse
0:51 As três peças e o papel de cada uma
1:15 Por que Tailscale, e não abrir porta no roteador
1:40 Passo zero: olhar antes de tocar
2:01 Passo 1: ligar a Tailscale
2:27 Passo 2: instalar o Sunshine
2:57 Passo 3: a permissão que o Linux exige
3:27 Passo 4: criar a senha do Sunshine
3:53 Passo 5: liberar a interface pela rede privada
4:21 Passo 6: o firewall, e a surpresa do Linux
4:47 Fechando o Sunshine para a rede de casa
5:15 Passo 7: escolher o monitor certo
5:39 Passo 8: o PC pronto mesmo sem ninguém na frente
6:06 Passo 9: o aparelho que vai receber
6:35 O resultado, medido de verdade
6:57 Os quatro erros que você provavelmente vai ver
7:29 Guia completo, comandos e scripts

🔗 LINKS OFICIAIS
Bazzite — https://bazzite.gg
Sunshine — https://docs.lizardbyte.dev/projects/sunshine/
Moonlight — https://moonlight-stream.org
Tailscale — https://tailscale.com

#bazzite #linux #linuxgaming #tailscale #sunshine #moonlight #selfhosted #gaming
```

## Tags (campo de tags do estúdio, separadas por vírgula)

```
bazzite, bazzite linux, sunshine moonlight, sunshine streaming, moonlight streaming, tailscale,
tailscale tutorial, linux gaming, jogar remotamente, streaming de jogos, game streaming, fedora
atomic, kinoite, kde plasma, wayland, firewalld, self hosted, homelab, steam big picture,
nvidia nvenc, tutorial linux, acesso remoto
```

## Comentário para fixar

```
📌 Resumo em 3 comandos, para quem já conhece o terreno:

   ujust tailscale enable && sudo tailscale up --operator=$USER
   ujust setup-sunshine        # opção: Enable (Flatpak)
   # e então: origin_web_ui_allowed = wan + csrf_allowed_origins no sunshine.conf

O guia escrito tem o resto (firewall, permissão do Wayland, autologin):
https://github.com/edilsonvilarinho/configurar-tailscale-sunshine-moonlight

Qual aparelho você vai usar para jogar? Celular, tablet ou notebook?
```

---

# 2. YouTube Shorts

**Arquivo:** `render/youtube-shorts.mp4` (1080×1920, 1min00, legenda queimada)

## Título

```
Jogue os jogos do PC no celular, sem abrir porta no roteador #shorts
```

## Descrição

```
Bazzite + Sunshine + Tailscale: o PC transmite, o celular recebe, e nada fica exposto na internet.

A pegadinha do Linux: o firewall já deixa essas portas abertas. O trabalho não é abrir — é fechar.

Tutorial completo de 8 minutos no canal. Guia escrito com todos os comandos:
https://github.com/edilsonvilarinho/configurar-tailscale-sunshine-moonlight

#shorts #bazzite #linux #linuxgaming #tailscale #sunshine #moonlight #tecnologia #selfhosted
```

---

# 3. TikTok

**Arquivo:** `render/tiktok.mp4` (1080×1920, 1min01, legenda queimada)

## Legenda

```
Dá pra jogar os jogos do seu PC no celular, de qualquer lugar — e sem abrir porta no roteador 👀

A parte que quase ninguém conta: no Linux o firewall JÁ deixa essas portas abertas. O trabalho
não é abrir, é fechar 🔒

Guia completo com todos os comandos no link do perfil.

#bazzite #linux #linuxgaming #tailscale #sunshine #moonlight #tech #programacao #selfhosted
#setupgamer #nerd #tecnologia
```

## Observações de publicação

- Os três primeiros segundos decidem tudo. O corte já abre com a frase de impacto na tela:
  **não acrescente intro, vinheta ou "fala galera" antes.**
- Texto de capa sugerido no editor do TikTok: `o PC fica em casa. você não.`
- Responda os primeiros comentários na primeira hora; é o que mais empurra o alcance ali.

---

# 4. Instagram — Reels

**Arquivo:** `render/instagram-reels.mp4` (1080×1920, 1min03, legenda queimada)

## Legenda

```
Seu PC de casa, jogando longe de casa 🎮

Sunshine transmite · Moonlight recebe · Tailscale conecta os dois numa rede privada.
Sem abrir porta no roteador, sem IP fixo, sem servidor no meio e sem mensalidade.

A parte que mais trava gente no Linux não é instalar: é a permissão de captura do Wayland e o
firewall — que aqui funciona ao contrário do Windows. Lá você briga para abrir as portas; aqui
elas já nascem abertas, e o trabalho é fechar.

Guia completo, com todos os comandos e dois scripts prontos, no link da bio.
Salva para quando for montar o seu 🔖

#bazzite #linux #linuxgaming #tailscale #sunshine #moonlight #selfhosted #homelab #tecnologia
#programacao #setupgamer #remotegaming #devops #nerd #gamer
```

## Primeiro comentário

```
Guia escrito, com os comandos para copiar:
github.com/edilsonvilarinho/configurar-tailscale-sunshine-moonlight
```

---

# 5. Instagram — feed (4:5)

**Arquivo:** `render/instagram-feed.mp4` (1080×1350, 1min03, legenda queimada)

## Legenda

```
Montei um servidor de jogos remoto em casa — e sem expor nada na internet.

O PC com Bazzite 44 roda o Sunshine, que captura a tela e codifica pela placa NVIDIA. O celular
roda o Moonlight. A Tailscale liga os dois numa rede privada criptografada, como se estivessem
lado a lado.

Resultado real, medido no log: iPhone conectando DIRETO no PC, sem servidor intermediário,
3440x1440 em HEVC, áudio digital, nenhuma porta aberta no roteador.

Três armadilhas que o tutorial cobre:
1. Wayland não deixa capturar a tela sem permissão explícita (o erro 503)
2. O serviço depende da sessão gráfica estar aberta — reiniciou sem login, acabou o streaming
3. O firewall do Linux já libera as portas: o trabalho é fechar, não abrir

Passo a passo completo no link da bio 👆

#bazzite #linux #linuxgaming #tailscale #sunshine #moonlight #selfhosted #homelab #tecnologia
#programacao #devops #setup #gamer
```

---

# 6. LinkedIn

**Arquivo:** `render/linkedin.mp4` (1080×1080, 1min38, legenda queimada)

## Post

```
Montei um host de streaming de jogos em Linux com uma regra inegociável: nenhuma porta exposta
na internet.

O desenho vale para qualquer serviço interno, não só para jogos:

• o serviço escuta localmente, como de costume;
• a interface da rede privada (Tailscale) fica numa zona de firewall permissiva;
• a placa física da LAN vai para uma zona restrita;
• resultado: alcançável apenas pela tailnet, com zero port forwarding.

Três aprendizados que valem para quem automatiza Linux:

1. pkexec não funciona a partir de um shell automatizado. O polkit nega sem abrir diálogo, porque
não há agente de autenticação atrelado àquele processo. A saída foi abrir um terminal na sessão
do usuário e deixar o sudo pedir a senha ali.

2. Nem todo erro no log é erro. O Sunshine registra "Failed to gain CAP_SYS_ADMIN" quatro vezes no
arranque e fecha o bloco com um comentário dizendo para ignorar: é a sonda de captura KMS falhando
dentro do Flatpak. Quem trata log por palavra-chave persegue fantasma.

3. Configuração faltando nem sempre falha — às vezes ela só escolhe errado, em silêncio. Sem
definir o monitor de captura, o sistema pega o primeiro da lista. Com duas telas, o cliente recebe
a tela errada e nada no log acusa.

A surpresa maior foi o firewall. Quem vem do Windows espera lutar para abrir portas; no Fedora e
derivados, a zona padrão já libera a faixa alta inteira, em todas as interfaces. O trabalho de
segurança não é abrir — é fechar, de forma seletiva.

Documentei tudo em guia aberto, com scripts de validação e de firewall (este último com modo de
simulação antes de aplicar). Link nos comentários.

Se você resolve esse tipo de problema de outro jeito, me conta: tenho interesse genuíno na
comparação.

#linux #devops #seguranca #infraestrutura #tailscale #selfhosted #automacao #sre
```

## Primeiro comentário

```
Guia completo, com os comandos e os scripts:
https://github.com/edilsonvilarinho/configurar-tailscale-sunshine-moonlight
```

No LinkedIn, link no corpo do post reduz alcance. Publique no primeiro comentário e, se quiser,
edite o post depois para citá-lo.

---

# Ordem de publicação sugerida

1. **YouTube longo primeiro** — é o destino para onde todos os outros links apontam.
2. **No mesmo dia:** Shorts e Reels, que levam tráfego para o longo.
3. **TikTok no dia seguinte**, com o link do perfil apontando para o vídeo longo.
4. **LinkedIn em dia útil, de manhã** — público e tom completamente diferentes; o post de lá fala
   de arquitetura e de automação, não de jogos.
5. **Instagram feed** alguns dias depois, como reforço, para não competir com o próprio Reels.

# Se for reaproveitar em outro lugar

O roteiro inteiro está em [`roteiro.py`](roteiro.py), já escrito para ser lido em voz alta. Serve
de base para post de blog, thread ou narração com a sua própria voz.
