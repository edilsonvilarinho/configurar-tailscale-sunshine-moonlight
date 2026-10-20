# Vídeo-tutorial: Tailscale + Sunshine no Bazzite

Vídeo gerado por código: o roteiro é um arquivo de dados, a narração é sintetizada, e as telas
são desenhadas. Nada de edição manual — corrigir um comando é editar o roteiro e renderizar de novo.

## Arquivos

| Arquivo | O que é |
|---|---|
| `roteiro.py` | **fonte única de verdade**: cenas, narração e conteúdo de tela de cada corte |
| `gerar_video.py` | renderizador: desenha os quadros (PIL), sintetiza a voz (Piper) e monta (ffmpeg) |
| `publicacao.md` | títulos, descrições, hashtags e capítulos prontos para cada plataforma |

## Cortes gerados

| Corte | Formato | Onde |
|---|---|---|
| `youtube-longo` | 1920×1080 | YouTube — tutorial completo, com capítulos |
| `youtube-shorts` | 1080×1920 | YouTube Shorts |
| `tiktok` | 1080×1920 | TikTok |
| `instagram-reels` | 1080×1920 | Instagram Reels |
| `instagram-feed` | 1080×1350 | Instagram feed (4:5) |
| `linkedin` | 1080×1080 | LinkedIn |

Os três verticais e o 4:5 saem com **legenda queimada** (quem assiste no celular costuma estar sem
som). O corte de 16:9 sai limpo, com `.srt` separado para subir junto no YouTube. Todo corte gera
`.srt`, inclusive os que já têm legenda na imagem.

## Como regerar

Dependências: `ffmpeg`, `python3-pillow` e o Piper com uma voz pt-BR.

```bash
# uma vez: ambiente do Piper e a voz neural em português
python3 -m venv /tmp/tts-venv
/tmp/tts-venv/bin/pip install piper-tts
/tmp/tts-venv/bin/python -m piper.download_voices --download-dir /tmp/voices pt_BR-faber-medium

export PIPER_BIN=/tmp/tts-venv/bin/piper
export PIPER_VOICE=/tmp/voices/pt_BR-faber-medium.onnx

python3 gerar_video.py --listar                      # o que existe
python3 gerar_video.py --preview youtube-longo:06-tailscale   # confere o visual de uma cena
python3 gerar_video.py --corte tiktok                # um corte
python3 gerar_video.py --todos                       # tudo
python3 gerar_video.py --capitulos youtube-longo     # marcadores para a descrição
```

Saída em `/tmp/video-bazzite/render/` (mude com `VIDEO_OUT`). Os intermediários ficam em
`/tmp/video-bazzite/<corte>/` e são reaproveitados: cena cuja duração não mudou não é redesenhada.

## Decisões de produção

- **Voz**: Piper `pt_BR-faber-medium`, com `length-scale 1.12` e pausa de `0.55 s` entre frases.
  Em ritmo normal a narração atropela quem está lendo comando na tela.
- **Ritmo**: cada cena dura `0,45 s` de respiro + a narração + uma pausa final própria. Quando a
  animação é mais curta que a fala, ela é **esticada** até ocupar 88% dela (teto de 2,6×) — assim o
  texto não aparece todo de cara e depois fica parado.
- **Transição**: fade de `0,65 s` entre cenas. Corte seco em tutorial dá sensação de pressa.
- **Digitação**: 42 caracteres por segundo, em blocos — é rápido o bastante para não cansar e
  lento o bastante para acompanhar.
- **Legenda**: gerada como ASS com `PlayRes` igual ao vídeo. Com SRT direto no filtro `subtitles`,
  o ffmpeg assume 384×288 e a letra sai gigantesca — foi o primeiro resultado desta produção.
- **Terminal**: a fonte cresce para preencher a janela e encolhe até o conteúdo caber inteiro.
  Transbordar é pior que letra menor.
- **Setas**: `→` só em linha de terminal. A Noto Sans não tem esse glifo e renderiza um retângulo
  vazio; no texto comum usa-se `»`.
