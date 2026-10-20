#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Miniatura 1280x720 do vídeo longo, no mesmo visual das cenas.

  python3 gerar_miniatura.py [destino.png]

Regra de miniatura: três elementos no máximo, texto legível em 120 px de largura
(que é o tamanho real no celular). Por isso a frase é curta e o corpo é enorme.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

from gerar_video import COR, fonte

W, H = 1280, 720
destino = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/video-bazzite/render/youtube-thumb.png")

img = Image.new("RGB", (W, H), COR["fundo"])
d = ImageDraw.Draw(img)

# brilho diagonal discreto, para o fundo não ficar chapado
for i in range(260):
    t = i / 260
    d.line([(0, H - 300 + i), (W, H - 620 + i)],
           fill=(int(14 + 10 * (1 - t)), int(17 + 8 * (1 - t)), int(22 + 26 * (1 - t))))

f_grande = fonte("sans_b", 100)
f_medio = fonte("sans_b", 54)
f_tag = fonte("sans_b", 30)
f_mono = fonte("mono_b", 30)

y = 92
d.text((70, y), "JOGUE O PC DE CASA", font=f_grande, fill=COR["tinta"]); y += 112
d.text((70, y), "DE QUALQUER LUGAR", font=f_grande, fill=COR["acento"]); y += 148

d.rounded_rectangle([(70, y), (70 + 470, y + 62)], radius=10,
                    fill=COR["painel"], outline=COR["linha"], width=2)
d.text((94, y + 14), "$ ujust setup-sunshine", font=f_mono, fill=COR["prompt"])

d.text((70, y + 96), "Bazzite 44  ·  Tailscale  ·  Sunshine", font=f_medio, fill=COR["fraca"])

# selo: o diferencial do tutorial, no canto que o titulo nao ocupa
selo_w, selo_h = 392, 118
sx, sy = W - selo_w - 55, H - selo_h - 55
d.rounded_rectangle([(sx, sy), (sx + selo_w, sy + selo_h)], radius=14,
                    fill=(18, 39, 27), outline=COR["ok"], width=3)
d.text((sx + 26, sy + 18), "SEM ABRIR", font=f_tag, fill=COR["ok"])
d.text((sx + 26, sy + 58), "PORTA NO ROTEADOR", font=f_tag, fill=COR["ok"])

destino.parent.mkdir(parents=True, exist_ok=True)
img.save(destino)
print(destino)
