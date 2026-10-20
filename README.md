# Tailscale + Sunshine + Moonlight

Procedimentos para jogar remotamente com Sunshine no host e Moonlight no cliente, com os dois lados
se enxergando apenas pela tailnet — sem port forwarding e sem porta pública.

## Host Bazzite (Linux)

- [Guia de instalação passo a passo (HTML)](guias/bazzite-host-tailscale-sunshine.html)
- [Plano, decisões e pontos de situação](planos/configurar-bazzite-sunshine-tailscale-moonlight.md)
- Scripts de apoio:
  - `scripts/bazzite-host-preflight.sh` — pré-validação somente leitura do host
  - `scripts/bazzite-host-firewall-tailnet.sh` — restringe as portas do Sunshine à tailnet (`--apply` / `--revert`)

## Host Windows

- [Plano e registro da execução](planos/configurar-tailscale-sunshine-moonlight.md)
- Scripts PowerShell em `planos/*.ps1`

## Vídeo-tutorial

Gerado por código — roteiro, narração sintetizada e telas desenhadas. Ver [`video/README.md`](video/README.md).

| Corte | Formato | Duração | Arquivo |
|---|---|---|---|
| YouTube (completo) | 1920×1080 | 8min21 | [`video/render/youtube-longo.mp4`](video/render/youtube-longo.mp4) |
| YouTube Shorts | 1080×1920 | 1min00 | [`video/render/youtube-shorts.mp4`](video/render/youtube-shorts.mp4) |
| TikTok | 1080×1920 | 1min01 | [`video/render/tiktok.mp4`](video/render/tiktok.mp4) |
| Instagram Reels | 1080×1920 | 1min03 | [`video/render/instagram-reels.mp4`](video/render/instagram-reels.mp4) |
| Instagram feed | 1080×1350 | 1min03 | [`video/render/instagram-feed.mp4`](video/render/instagram-feed.mp4) |
| LinkedIn | 1080×1080 | 1min38 | [`video/render/linkedin.mp4`](video/render/linkedin.mp4) |

Legenda `.srt` para cada corte, miniatura em `video/render/youtube-thumb.png`, e os textos de
publicação (título, descrição, hashtags, capítulos) em [`video/publicacao.md`](video/publicacao.md).

## Cliente

- [Guia da máquina cliente (Tailscale + Moonlight)](planos/guia-maquina-cliente-tailscale-moonlight.md)

## Regra válida para todos os documentos

Senha, token e PIN não entram neste repositório.
