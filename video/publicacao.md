# Material de publicação

Texto pronto para cada plataforma. O link citado em todos é o repositório:
`https://github.com/edilsonvilarinho/configurar-tailscale-sunshine-moonlight`

---

## YouTube — vídeo longo (`youtube-longo.mp4`)

**Título** (escolha um):

1. `Jogue os jogos do seu PC de QUALQUER lugar — Bazzite + Sunshine + Tailscale (tutorial completo)`
2. `Streaming de jogos em Linux sem abrir porta no roteador | Bazzite 44 passo a passo`
3. `Transforme seu PC Linux em servidor de jogos remoto — tutorial completo em 11 minutos`

**Descrição:**

```
Neste tutorial a gente transforma um PC com Bazzite 44 num servidor de jogos remoto, para jogar
no celular, no tablet ou em outro notebook — de qualquer lugar do mundo, sem abrir nenhuma porta
no roteador.

Tudo é feito com três peças: o Sunshine transmite, o Moonlight recebe, e a Tailscale faz a rede
privada entre os dois. Mostro todos os comandos na tela, incluindo as armadilhas que o Linux tem
e que nenhum tutorial de Windows cobre: a permissão de captura do Wayland, o serviço de usuário
que depende da sessão gráfica, e o firewall — que aqui funciona ao contrário do que você espera.

⚙️ Guia escrito, com todos os comandos para copiar e dois scripts de apoio:
https://github.com/edilsonvilarinho/configurar-tailscale-sunshine-moonlight

📋 O que você precisa:
• Um PC com Bazzite (usei a versão 44 Kinoite, imagem bazzite-nvidia-open)
• Uma conta gratuita na Tailscale
• Um celular, tablet ou notebook para receber a transmissão

🔗 Links oficiais:
• Bazzite — https://bazzite.gg
• Sunshine — https://docs.lizardbyte.dev/projects/sunshine/
• Moonlight — https://moonlight-stream.org
• Tailscale — https://tailscale.com

⏱️ Capítulos:
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

#bazzite #linux #gaming #tailscale #sunshine #moonlight #linuxgaming #selfhosted
```

**Miniatura sugerida:** fundo escuro, o texto `JOGUE O PC DE CASA, DE QUALQUER LUGAR` em duas
linhas grandes, com o logo do Bazzite de um lado e um celular mostrando um jogo do outro.
Evite poluir: três elementos no máximo.

---

## YouTube Shorts (`youtube-shorts.mp4`)

**Título:** `Jogue os jogos do PC no celular, sem abrir porta no roteador #bazzite #linux`

**Descrição:**
```
Bazzite + Sunshine + Tailscale: o PC transmite, o celular recebe, e nada fica exposto na internet.
Tutorial completo (11 min) no canal, e o guia escrito está no link da descrição.

#bazzite #linux #linuxgaming #tailscale #sunshine #moonlight #tecnologia #shorts
```

---

## TikTok (`tiktok.mp4`)

```
Dá pra jogar os jogos do seu PC no celular, de qualquer lugar — e sem abrir porta no roteador 👀

No Linux tem uma pegadinha que quase ninguém conta: o firewall já deixa essas portas abertas.
O trabalho não é abrir, é FECHAR. Explico no vídeo.

Guia completo com todos os comandos no link do perfil.

#bazzite #linux #linuxgaming #tailscale #sunshine #moonlight #tech #programacao #selfhosted #setup
```

Dica de publicação: os 3 primeiros segundos decidem. O corte já abre com a pergunta na tela,
então não acrescente intro antes.

---

## Instagram Reels (`instagram-reels.mp4`) e feed (`instagram-feed.mp4`)

```
Seu PC de casa, jogando longe de casa 🎮

Sunshine transmite · Moonlight recebe · Tailscale conecta os dois numa rede privada.
Sem abrir porta no roteador, sem IP fixo, sem servidor no meio.

A parte que mais trava gente no Linux: a permissão de captura do Wayland e o firewall — que aqui
funciona ao contrário do Windows.

Guia completo, com todos os comandos e dois scripts prontos, no link da bio.
Salva para quando for montar o seu 🔖

#bazzite #linux #linuxgaming #tailscale #sunshine #moonlight #selfhosted #homelab #tecnologia
#programacao #setupgamer #remotegaming
```

---

## LinkedIn (`linkedin.mp4`)

```
Montei um host de streaming de jogos em Linux com uma regra inegociável: nenhuma porta exposta
na internet.

O desenho vale para qualquer serviço interno, não só para jogos:

• o serviço escuta localmente, como de costume;
• a interface da rede privada (Tailscale) fica numa zona de firewall permissiva;
• a placa física da LAN vai para uma zona restrita;
• resultado: alcançável apenas pela tailnet, com zero port forwarding.

Três coisas que custaram tempo e que valem para quem automatiza Linux:

1. pkexec não funciona a partir de um shell automatizado — o polkit nega sem abrir diálogo,
   porque não há agente de autenticação atrelado àquele processo. A saída foi abrir um terminal
   na sessão do usuário e deixar o sudo pedir a senha ali.

2. Nem todo erro no log é erro. O Sunshine registra "Failed to gain CAP_SYS_ADMIN" quatro vezes
   no arranque e encerra o bloco com um comentário dizendo para ignorar: é só a sonda de captura
   KMS falhando no Flatpak.

3. Configuração faltando nem sempre falha. Sem definir o monitor de captura, o sistema não dá
   erro: ele escolhe o primeiro da lista. Com duas telas, o cliente recebe a tela errada e nada
   no log acusa.

A surpresa maior foi o firewall. Quem vem do Windows espera lutar para abrir portas; no Fedora e
derivados, a zona padrão já libera a faixa alta inteira, em todas as interfaces. O trabalho de
segurança não é abrir — é fechar, de forma seletiva.

Documentei tudo em guia aberto, com scripts de validação e de firewall (este último com modo de
simulação antes de aplicar). Link nos comentários.

Se você resolve esse tipo de problema de outro jeito, me conta: tenho interesse genuíno na
comparação.

#linux #devops #seguranca #infraestrutura #tailscale #selfhosted #automacao
```

Publique o link do repositório **no primeiro comentário**, não no corpo do post.

---

## Ordem de publicação sugerida

1. YouTube longo primeiro — é o destino de todos os outros links.
2. No mesmo dia: Shorts e Reels, que levam tráfego para o longo.
3. TikTok no dia seguinte, com o link no perfil apontando para o vídeo longo.
4. LinkedIn em dia útil, de manhã — o público e o tom ali são outros.
