#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monta os videos do tutorial a partir de roteiro.py.

  python3 gerar_video.py --listar
  python3 gerar_video.py --preview youtube-longo:06-tailscale   # so um PNG
  python3 gerar_video.py --corte youtube-longo
  python3 gerar_video.py --todos

Dependencias: ffmpeg, PIL, e o piper do venv apontado por PIPER_BIN/PIPER_VOICE.
Nenhuma rede e usada na renderizacao -- a voz ja esta baixada.
"""

import argparse
import hashlib
import math
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import roteiro

AQUI = Path(__file__).resolve().parent
BUILD = Path(os.environ.get("VIDEO_BUILD", "/tmp/video-bazzite"))
SAIDA = Path(os.environ.get("VIDEO_OUT", BUILD / "render"))
PIPER_BIN = Path(os.environ.get("PIPER_BIN", ""))
PIPER_VOICE = Path(os.environ.get("PIPER_VOICE", ""))

FPS = 30
TRANSICAO = 0.65          # crossfade entre cenas, em segundos
LEAD = 0.45               # respiro antes da narracao comecar
CPS_DIGITACAO = 42.0      # caracteres por segundo "digitados"

COR = {
    "fundo":    (14, 17, 22),
    "painel":   (22, 26, 33),
    "painel2":  (28, 33, 42),
    "linha":    (42, 49, 60),
    "tinta":    (231, 235, 241),
    "fraca":    (154, 165, 180),
    "acento":   (169, 139, 255),
    "ok":       (110, 231, 160),
    "aviso":    (240, 198, 116),
    "ruim":     (255, 143, 143),
    "term_bg":  (10, 13, 18),
    "prompt":   (110, 231, 160),
}

FONTES = {
    "sans":   "/usr/share/fonts/google-noto/NotoSans-Regular.ttf",
    "sans_b": "/usr/share/fonts/google-noto/NotoSans-Bold.ttf",
    "sans_s": "/usr/share/fonts/google-noto/NotoSans-SemiBold.ttf",
    "mono":   "/usr/share/fonts/fira-code/FiraCode-Regular.ttf",
    "mono_b": "/usr/share/fonts/fira-code/FiraCode-Bold.ttf",
}

# Presets por formato. cpl = caracteres por linha no terminal.
PRESETS = {
    (1920, 1080): dict(margem=110, titulo=72, sub=33, corpo=35, mono=31, cpl=74, entre=1.62),
    (1080, 1920): dict(margem=68,  titulo=76, sub=35, corpo=41, mono=25, cpl=52, entre=1.72),
    (1080, 1350): dict(margem=68,  titulo=70, sub=33, corpo=39, mono=24, cpl=54, entre=1.66),
    (1080, 1080): dict(margem=68,  titulo=62, sub=31, corpo=35, mono=23, cpl=56, entre=1.58),
}

_cache_fonte = {}


def fonte(nome, tamanho):
    chave = (nome, tamanho)
    if chave not in _cache_fonte:
        _cache_fonte[chave] = ImageFont.truetype(FONTES[nome], tamanho)
    return _cache_fonte[chave]


def quebrar(texto, limite):
    """Quebra por palavras; linha de comando quebra com recuo de continuacao."""
    if len(texto) <= limite:
        return [texto]
    linhas, atual = [], ""
    for palavra in texto.split(" "):
        tentativa = (atual + " " + palavra).strip()
        if len(tentativa) <= limite:
            atual = tentativa
        else:
            if atual:
                linhas.append(atual)
            while len(palavra) > limite:
                linhas.append(palavra[:limite])
                palavra = palavra[limite:]
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas


class Tela:
    """Desenha uma cena. Cada metodo publico devolve lista de (imagem, duracao)."""

    def __init__(self, largura, altura):
        self.W, self.H = largura, altura
        p = PRESETS[(largura, altura)]
        self.m = p["margem"]
        self.f_titulo = fonte("sans_b", p["titulo"])
        self.f_sub = fonte("sans", p["sub"])
        self.f_corpo = fonte("sans", p["corpo"])
        self.f_corpo_b = fonte("sans_s", p["corpo"])
        self.f_mono = fonte("mono", p["mono"])
        self.f_mono_b = fonte("mono_b", p["mono"])
        self.f_tag = fonte("sans_b", max(18, int(p["sub"] * 0.62)))
        self.cpl = p["cpl"]
        self.entre = p["entre"]
        self.px_mono = p["mono"]
        self.px_corpo = p["corpo"]
        self.vertical = altura > largura
        # espaco reservado embaixo para a legenda queimada nos formatos de celular
        self.reserva = {(1080, 1920): 215, (1080, 1350): 175,
                        (1080, 1080): 140}.get((largura, altura), 0)
        self.base_y = altura - self.m - self.reserva

    # -- blocos reutilizaveis -------------------------------------------------

    def base(self, cena, tag=""):
        img = Image.new("RGB", (self.W, self.H), COR["fundo"])
        d = ImageDraw.Draw(img)
        y = self.m

        if tag:
            d.text((self.m, y), tag.upper(), font=self.f_tag, fill=COR["acento"])
            y += int(self.f_tag.size * 2.0)

        for linha in quebrar(cena["titulo"], 34 if self.vertical else 46):
            d.text((self.m, y), linha, font=self.f_titulo, fill=COR["tinta"])
            y += int(self.f_titulo.size * 1.22)

        if cena.get("sub"):
            y += int(self.f_sub.size * 0.35)
            for linha in quebrar(cena["sub"], 46 if self.vertical else 64):
                d.text((self.m, y), linha, font=self.f_sub, fill=COR["fraca"])
                y += int(self.f_sub.size * 1.35)

        y += int(self.f_sub.size * 0.5)
        d.line([(self.m, y), (self.m + int(self.W * 0.09), y)], fill=COR["acento"], width=4)
        y += int(self.f_sub.size * 1.3)
        return img, d, y

    def rodape(self, d):
        # nos formatos de celular o rodape brigaria com a legenda queimada
        if self.reserva:
            return
        txt = "Bazzite 44 · Tailscale · Sunshine · Moonlight"
        f = fonte("sans", max(16, int(self.f_sub.size * 0.58)))
        largura = d.textlength(txt, font=f)
        d.text((self.W - self.m - largura, self.base_y + int(f.size * 0.45)),
               txt, font=f, fill=(90, 100, 115))

    # -- cenas ----------------------------------------------------------------

    def titulo(self, cena):
        passos = []
        for etapa in (1, 2):
            img = Image.new("RGB", (self.W, self.H), COR["fundo"])
            d = ImageDraw.Draw(img)
            linhas = quebrar(cena["titulo"], 24 if self.vertical else 32)
            fonte_t = self.f_titulo
            if len(linhas) > 3:
                fonte_t = fonte("sans_b", int(self.f_titulo.size * 0.82))
                linhas = quebrar(cena["titulo"], 30 if self.vertical else 40)
            alt = len(linhas) * int(fonte_t.size * 1.2)
            y = (self.H - alt) // 2 - int(self.H * 0.06)
            d.line([(self.m, y - int(fonte_t.size * 0.9)),
                    (self.m + int(self.W * 0.12), y - int(fonte_t.size * 0.9))],
                   fill=COR["acento"], width=5)
            for linha in linhas:
                d.text((self.m, y), linha, font=fonte_t, fill=COR["tinta"])
                y += int(fonte_t.size * 1.2)
            if etapa == 2 and cena.get("sub"):
                y += int(self.f_sub.size * 0.7)
                for linha in quebrar(cena["sub"], 44 if self.vertical else 70):
                    d.text((self.m, y), linha, font=self.f_sub, fill=COR["acento"])
                    y += int(self.f_sub.size * 1.35)
            self.rodape(d)
            passos.append((img, 0.9 if etapa == 1 else 1.0))
        return passos

    def bullets(self, cena, tag=""):
        itens = cena["corpo"]
        passos, atual = [], None
        for i in range(len(itens) + 1):
            img, d, y = self.base(cena, tag)
            for item in itens[:i]:
                destaque = item.startswith(("1.", "2.", "3.", "4.", "5.")) or item.isupper()
                cor = COR["tinta"]
                f = self.f_corpo
                recuo = 0
                texto = item
                if item.startswith("    "):
                    recuo = int(self.W * 0.028)
                    texto = item.strip()
                    f = fonte("mono", int(self.px_mono * 0.92))
                    cor = COR["fraca"]
                elif "->" in item:
                    f = self.f_corpo_b
                for j, linha in enumerate(quebrar(texto, int(self.cpl * 0.95))):
                    if j == 0 and not recuo:
                        d.ellipse([(self.m, y + f.size * 0.42), (self.m + 9, y + f.size * 0.42 + 9)],
                                  fill=COR["acento"])
                    d.text((self.m + int(self.W * 0.022) + recuo, y), linha, font=f, fill=cor)
                    y += int(f.size * 1.32)
                y += int(self.px_corpo * 0.42)
            self.rodape(d)
            atual = img
            if i > 0:
                passos.append((img, 0.85))
        passos.insert(0, (passos[0][0] if passos else atual, 0.5))
        return passos

    def tabela(self, cena, tag=""):
        linhas = cena["corpo"]
        passos = []
        larg_rot = int(self.W * (0.40 if not self.vertical else 0.46))
        for i in range(1, len(linhas) + 1):
            img, d, y = self.base(cena, tag)
            for rotulo, valor in linhas[:i]:
                y0 = y
                for k, l in enumerate(quebrar(rotulo, 26 if self.vertical else 30)):
                    d.text((self.m, y), l, font=self.f_corpo_b, fill=COR["acento"])
                    y += int(self.px_corpo * 1.26)
                y_valor = y0
                for l in quebrar(valor, int(self.cpl * 0.62)):
                    d.text((self.m + larg_rot, y_valor), l,
                           font=fonte("sans", int(self.px_corpo * 0.94)), fill=COR["tinta"])
                    y_valor += int(self.px_corpo * 1.26)
                y = max(y, y_valor) + int(self.px_corpo * 0.30)
                d.line([(self.m, y), (self.W - self.m, y)], fill=COR["linha"], width=2)
                y += int(self.px_corpo * 0.42)
            self.rodape(d)
            passos.append((img, 0.95))
        return passos

    def comparar(self, cena, tag=""):
        esq_t, esq, dir_t, dire = cena["corpo"]
        passos = []
        for etapa in (1, 2):
            img, d, y = self.base(cena, tag)
            topo = y
            f_item = fonte("sans", int(self.px_corpo * 0.9))
            def altura_caixa(titulo, itens, larg_util):
                h = int(self.px_corpo * 0.9)
                h += len(quebrar(titulo, int(self.cpl * 0.45))) * int(self.px_corpo * 1.3)
                h += int(self.px_corpo * 0.5)
                for it in itens:
                    h += len(quebrar(it, larg_util)) * int(f_item.size * 1.3)
                    h += int(f_item.size * 0.45)
                return h + int(self.px_corpo * 0.9)
            if self.vertical:
                larg = self.W - 2 * self.m
                h1 = altura_caixa(esq_t, esq, int(self.cpl * 0.80))
                h2 = altura_caixa(dir_t, dire, int(self.cpl * 0.80))
                caixas = [(self.m, topo, larg, h1, esq_t, esq, COR["ruim"], int(self.cpl * 0.80)),
                          (self.m, topo + h1 + 22, larg, h2, dir_t, dire, COR["ok"],
                           int(self.cpl * 0.80))]
            else:
                larg = (self.W - 2 * self.m - 36) // 2
                util = int(self.cpl * 0.46)
                alt = max(altura_caixa(esq_t, esq, util), altura_caixa(dir_t, dire, util))
                alt = min(alt, self.base_y - topo)
                caixas = [(self.m, topo, larg, alt, esq_t, esq, COR["ruim"], util),
                          (self.m + larg + 36, topo, larg, alt, dir_t, dire, COR["ok"], util)]
            for idx, (x, yy, w, h, titulo, itens, cor, util) in enumerate(caixas):
                if idx >= etapa:
                    break
                d.rounded_rectangle([(x, yy), (x + w, yy + h)], radius=14,
                                    fill=COR["painel"], outline=COR["linha"], width=2)
                d.rounded_rectangle([(x, yy), (x + 6, yy + h)], radius=3, fill=cor)
                cy = yy + int(self.px_corpo * 0.9)
                for l in quebrar(titulo, int(self.cpl * 0.45)):
                    d.text((x + 30, cy), l, font=self.f_corpo_b, fill=cor)
                    cy += int(self.px_corpo * 1.3)
                cy += int(self.px_corpo * 0.5)
                f = f_item
                for item in itens:
                    for j, l in enumerate(quebrar(item, util)):
                        d.text((x + 30 + (0 if j == 0 else 18), cy), l, font=f, fill=COR["tinta"])
                        cy += int(f.size * 1.3)
                    cy += int(f.size * 0.45)
            self.rodape(d)
            passos.append((img, 1.2))
        return passos

    def terminal(self, cena, tag=""):
        """Digita os comandos. A janela tem a altura do conteudo, nao da tela."""
        img0, d0, topo = self.base(cena, tag)
        jan_w_prev = self.W - 2 * self.m

        # A fonte cresce para ocupar a largura da janela: num celular, terminal
        # com linha curta e fonte pequena e ilegivel.
        mais_longa = max((len(t) + (2 if k == "cmd" else 0))
                         for k, t in cena["corpo"] if t.strip())
        mais_longa = min(mais_longa, self.cpl)
        util = jan_w_prev - 112          # recuo interno dos dois lados, com folga
        px = int(min(self.px_mono * 1.7, max(self.px_mono, util / (mais_longa * 0.6))))

        disponivel = self.base_y - topo

        def metricas(tamanho):
            cpl_ = max(20, int(util / (tamanho * 0.6)))
            linha_ = int(tamanho * self.entre)
            n_, folga_ = 0, 0.0
            for tipo, texto in cena["corpo"]:
                lim = cpl_ - 2 if tipo == "cmd" else cpl_
                n_ += len(quebrar(texto, lim)) if texto.strip() else 1
                if tipo == "cmd":
                    folga_ += 0.12
            altura_ = (int(tamanho * 1.9) + int(tamanho * 0.9) + int(tamanho * 1.1) +
                       int((n_ + folga_) * linha_))
            return cpl_, linha_, n_, folga_, altura_

        # encolhe ate o conteudo caber inteiro: transbordar e pior que fonte menor
        while px > 14:
            if metricas(px)[4] <= disponivel:
                break
            px -= 1

        cpl, altura_linha, n_linhas, folga, _ = metricas(px)
        f_mono = fonte("mono", px)
        f_mono_b = fonte("mono_b", px)
        barra = int(px * 1.9)
        pad_topo = int(px * 0.9)
        pad_base = int(px * 1.1)

        jan_h = min(disponivel, barra + pad_topo + pad_base +
                    int((n_linhas + folga) * altura_linha))
        jan_x = self.m
        jan_w = self.W - 2 * self.m
        # no vertical o bloco fica no terco superior, nao no centro morto da tela
        jan_y = topo + (int(max(0, disponivel - jan_h) * 0.22) if self.vertical else 0)

        def moldura():
            img = img0.copy()
            d = ImageDraw.Draw(img)
            d.rounded_rectangle([(jan_x, jan_y), (jan_x + jan_w, jan_y + jan_h)],
                                radius=14, fill=COR["term_bg"], outline=COR["linha"], width=2)
            d.rounded_rectangle([(jan_x, jan_y), (jan_x + jan_w, jan_y + barra)],
                                radius=14, fill=COR["painel2"])
            d.rectangle([(jan_x, jan_y + barra - 14), (jan_x + jan_w, jan_y + barra)],
                        fill=COR["painel2"])
            for i, c in enumerate([(255, 95, 87), (254, 188, 46), (40, 200, 64)]):
                cx = jan_x + 26 + i * 26
                d.ellipse([(cx, jan_y + barra // 2 - 7), (cx + 14, jan_y + barra // 2 + 7)], fill=c)
            f = fonte("mono", int(px * 0.82))
            d.text((jan_x + 130, jan_y + barra // 2 - f.size * 0.62), "edi@bazzite:~",
                   font=f, fill=COR["fraca"])
            self.rodape(d)
            return img

        base_img = moldura()
        x = jan_x + 28
        y_inicial = jan_y + barra + pad_topo
        passos = []
        desenhadas = []

        def pintar(parcial=None):
            img = base_img.copy()
            d = ImageDraw.Draw(img)
            y = y_inicial
            for tipo, texto in list(desenhadas) + ([parcial] if parcial else []):
                if tipo == "cmd":
                    for j, l in enumerate(quebrar(texto, cpl - 2)):
                        pre = "$ " if j == 0 else "  "
                        d.text((x, y), pre, font=f_mono_b, fill=COR["prompt"])
                        d.text((x + d.textlength(pre, font=f_mono_b), y), l,
                               font=f_mono, fill=COR["tinta"])
                        y += altura_linha
                    y += int(altura_linha * 0.12)
                elif tipo == "out":
                    for l in quebrar(texto, cpl):
                        d.text((x, y), l, font=f_mono, fill=COR["fraca"])
                        y += altura_linha
                else:
                    for l in quebrar(texto, cpl):
                        d.text((x, y), l, font=f_mono,
                               fill=COR["aviso"] if l.strip() else COR["fraca"])
                        y += altura_linha
            return img

        for tipo, texto in cena["corpo"]:
            if tipo == "cmd" and texto.strip():
                passo_chars = max(2, len(texto) // 26 + 2)
                i = 0
                while i < len(texto):
                    i = min(len(texto), i + passo_chars)
                    passos.append((pintar((tipo, texto[:i])), passo_chars / CPS_DIGITACAO))
                desenhadas.append((tipo, texto))
                passos.append((pintar(), 0.30))
            else:
                desenhadas.append((tipo, texto))
                passos.append((pintar(), 0.36 if texto.strip() else 0.14))
        return passos or [(base_img, 1.0)]

    def desenhar(self, cena, tag=""):
        k = cena["kind"]
        if k == "title":
            return self.titulo(cena)
        if k == "bullets":
            return self.bullets(cena, tag)
        if k == "table":
            return self.tabela(cena, tag)
        if k == "compare":
            return self.comparar(cena, tag)
        if k == "terminal":
            return self.terminal(cena, tag)
        raise ValueError(f"kind desconhecido: {k}")


# -- narracao ----------------------------------------------------------------

def sintetizar(texto, destino):
    """Gera o wav da narracao (cacheado pelo hash do texto)."""
    if destino.exists():
        return destino
    destino.parent.mkdir(parents=True, exist_ok=True)
    bruto = destino.with_suffix(".bruto.wav")
    proc = subprocess.run(
        [str(PIPER_BIN), "-m", str(PIPER_VOICE), "--length-scale", "1.12",
         "--sentence-silence", "0.55", "-f", str(bruto)],
        input=texto.encode("utf-8"), capture_output=True)
    if proc.returncode != 0 or not bruto.exists():
        raise RuntimeError(f"piper falhou: {proc.stderr.decode()[:400]}")
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(bruto),
         "-af", "highpass=f=70,acompressor=threshold=-18dB:ratio=3:attack=10:release=180,"
                "loudnorm=I=-16:TP=-1.5:LRA=11",
         "-ar", "48000", "-ac", "2", str(destino)], check=True)
    bruto.unlink(missing_ok=True)
    return destino


def duracao(caminho):
    saida = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                            "-of", "csv=p=0", str(caminho)],
                           capture_output=True, text=True, check=True).stdout.strip()
    return float(saida)


def frases(texto):
    partes = re.split(r"(?<=[.!?:])\s+", texto.strip())
    return [p.strip() for p in partes if p.strip()]


def fatiar(texto, limite):
    """Divide a narracao em blocos curtos de legenda, respeitando a pontuacao."""
    blocos = []
    for f in frases(texto):
        if len(f) <= limite:
            blocos.append(f)
            continue
        atual = ""
        for palavra in f.split():
            if len((atual + " " + palavra).strip()) <= limite:
                atual = (atual + " " + palavra).strip()
            else:
                blocos.append(atual)
                atual = palavra
        if atual:
            blocos.append(atual)
    return blocos


def blocos_legenda(cenas, inicios, duracoes_voz, limite):
    """(inicio, fim, texto) de cada bloco, proporcional ao tamanho do texto."""
    saida = []
    for cena, inicio, dvoz in zip(cenas, inicios, duracoes_voz):
        partes = fatiar(cena["fala"], limite)
        if not partes:
            continue
        total = sum(len(p) for p in partes)
        t = inicio + LEAD
        for parte in partes:
            dur = dvoz * (len(parte) / total)
            saida.append((t, t + dur - 0.06, parte))
            t += dur
    return saida


def ass_tempo(seg):
    h = int(seg // 3600); m = int(seg % 3600 // 60); s = seg % 60
    return f"{h:d}:{m:02d}:{s:05.2f}"


def escrever_ass(blocos, destino, largura, altura, px, margem_v):
    """ASS com PlayRes igual ao video: tamanho em pixel de verdade.

    Pelo filtro subtitles com SRT, o ffmpeg assume 384x288 e o corpo da letra
    sai gigante -- foi o que aconteceu na primeira tentativa.
    """
    cab = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {largura}",
        f"PlayResY: {altura}", "WrapStyle: 0", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
        "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Fala,Noto Sans,{px},&H00FFFFFF,&H000000FF,&H00101418,&H96000000,-1,0,0,0,"
        f"100,100,0,0,1,{max(3, px // 12)},0,2,{int(largura * 0.08)},{int(largura * 0.08)},"
        f"{margem_v},1", "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    for ini, fim, texto in blocos:
        txt = texto.replace("\n", " ").replace("{", "(").replace("}", ")")
        cab.append(f"Dialogue: 0,{ass_tempo(ini)},{ass_tempo(fim)},Fala,,0,0,0,,{txt}")
    destino.write_text("\n".join(cab), encoding="utf-8")
    return destino


def srt_tempo(seg):
    h = int(seg // 3600); m = int(seg % 3600 // 60); s = seg % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int((s - int(s)) * 1000):03d}"


# -- montagem ----------------------------------------------------------------

def tag_da_cena(cena, indice, total):
    t = cena["titulo"].lower()
    m = re.match(r"^(passo \d+|passo zero)", t)
    if m:
        return m.group(1)
    if cena["kind"] == "title":
        return ""
    return f"{indice:02d} / {total:02d}"


def montar_cena(cena, tela, tag, dir_cena):
    """Renderiza os PNGs, sintetiza a voz e devolve (mp4_mudo, wav, duracao)."""
    dir_cena.mkdir(parents=True, exist_ok=True)
    mp4 = dir_cena / "cena.mp4"
    wav = sintetizar(cena["fala"], dir_cena / "voz.wav")
    d_narr = duracao(wav)

    passos = tela.desenhar(cena, tag)
    anim = sum(d for _, d in passos)
    janela = d_narr * 0.88
    if anim < janela and anim > 0:
        fator = min(2.6, janela / anim)
        passos = [(img, d * fator) for img, d in passos]
        anim = sum(d for _, d in passos)

    total = LEAD + max(anim, d_narr) + cena["hold"]
    sobra = total - LEAD - anim

    if mp4.exists() and (dir_cena / "dur.txt").exists():
        if abs(float((dir_cena / "dur.txt").read_text()) - total) < 0.01:
            return mp4, wav, total

    for antigo in dir_cena.glob("f*.png"):
        antigo.unlink()
    lista = dir_cena / "lista.txt"
    linhas = []
    arquivos = []
    for i, (img, dur) in enumerate(passos):
        p = dir_cena / f"f{i:04d}.png"
        img.save(p, compress_level=1)
        arquivos.append((p, dur))
    primeiro = arquivos[0][0]
    linhas.append(f"file '{primeiro.name}'\nduration {LEAD:.3f}")
    for p, dur in arquivos:
        linhas.append(f"file '{p.name}'\nduration {dur:.3f}")
    ultimo = arquivos[-1][0]
    linhas.append(f"file '{ultimo.name}'\nduration {max(0.1, sobra):.3f}")
    linhas.append(f"file '{ultimo.name}'")
    lista.write_text("\n".join(linhas))

    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", str(lista), "-vf", f"fps={FPS},format=yuv420p",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
                    "-movflags", "+faststart", str(mp4)], check=True, cwd=dir_cena)
    (dir_cena / "dur.txt").write_text(f"{total:.4f}")
    for p, _ in arquivos:
        p.unlink(missing_ok=True)
    return mp4, wav, total


def gerar_srt(blocos, destino):
    partes = []
    for n, (ini, fim, texto) in enumerate(blocos, 1):
        corpo = "\n".join(quebrar(texto, 42))
        partes.append(f"{n}\n{srt_tempo(ini)} --> {srt_tempo(fim)}\n{corpo}\n")
    destino.write_text("\n".join(partes), encoding="utf-8")
    return destino


def montar_corte(nome, corte, queimar_legenda=None):
    cenas = corte["cenas"]
    W, H = corte["aspecto"]
    tela = Tela(W, H)
    dir_corte = BUILD / nome
    dir_corte.mkdir(parents=True, exist_ok=True)

    mp4s, wavs, duracoes = [], [], []
    for i, cena in enumerate(cenas, 1):
        tag = tag_da_cena(cena, i, len(cenas))
        print(f"  [{nome}] cena {i:2d}/{len(cenas)}  {cena['id']}", flush=True)
        mp4, wav, dur = montar_cena(cena, tela, tag, dir_corte / cena["id"])
        mp4s.append(mp4); wavs.append(wav); duracoes.append(dur)

    inicios, acc = [], 0.0
    for i, d in enumerate(duracoes):
        inicios.append(acc)
        acc += d - (TRANSICAO if i < len(duracoes) - 1 else 0)
    total = acc

    entradas = []
    for m in mp4s:
        entradas += ["-i", str(m)]
    for w in wavs:
        entradas += ["-i", str(w)]

    n = len(mp4s)
    filtros = []
    atual = "0:v"
    L = duracoes[0]
    for i in range(1, n):
        saida = f"v{i}"
        filtros.append(f"[{atual}][{i}:v]xfade=transition=fade:duration={TRANSICAO}:"
                       f"offset={max(0.0, L - TRANSICAO):.4f}[{saida}]")
        atual = saida
        L = L + duracoes[i] - TRANSICAO
    for i in range(n):
        atraso = int((inicios[i] + LEAD) * 1000)
        filtros.append(f"[{n + i}:a]adelay={atraso}|{atraso}[a{i}]")
    filtros.append("".join(f"[a{i}]" for i in range(n)) +
                   f"amix=inputs={n}:normalize=0:dropout_transition=0[amix]")
    filtros.append(f"[amix]apad,atrim=0:{total:.3f},alimiter=limit=0.95[aout]")

    saida_v = f"[{atual}]" if n > 1 else "[0:v]"
    destino = SAIDA / f"{nome}.mp4"
    SAIDA.mkdir(parents=True, exist_ok=True)

    dvozes = [duracao(w) for w in wavs]
    limite = 58 if queimar_legenda else 84
    blocos = blocos_legenda(cenas, inicios, dvozes, limite)
    gerar_srt(blocos, SAIDA / f"{nome}.srt")

    if queimar_legenda:
        px, margem_v = queimar_legenda
        ass = escrever_ass(blocos, dir_corte / "legenda.ass", W, H, px, margem_v)
        filtros.append(f"{saida_v}subtitles='{ass}'[vout]")
        saida_v = "[vout]"

    cmd = (["ffmpeg", "-y", "-v", "error"] + entradas +
           ["-filter_complex", ";".join(filtros),
            "-map", saida_v, "-map", "[aout]",
            "-c:v", "libx264", "-preset", "slow", "-crf", "20",
            "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-movflags", "+faststart", str(destino)])
    subprocess.run(cmd, check=True)
    return destino, total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--preview", help="CORTE:ID_DA_CENA  -> gera um PNG de amostra")
    ap.add_argument("--corte", action="append", default=[])
    ap.add_argument("--todos", action="store_true")
    ap.add_argument("--capitulos", help="CORTE -> imprime os marcadores de capitulo")
    args = ap.parse_args()

    if args.listar:
        for nome, c in roteiro.CORTES.items():
            palavras = sum(len(s["fala"].split()) for s in c["cenas"])
            print(f"{nome:18s} {len(c['cenas']):2d} cenas  {palavras:4d} palavras  {c['aspecto']}")
        return

    if args.preview:
        nome, cena_id = args.preview.split(":")
        corte = roteiro.CORTES[nome]
        tela = Tela(*corte["aspecto"])
        cenas = corte["cenas"]
        idx = next(i for i, c in enumerate(cenas) if c["id"] == cena_id)
        passos = tela.desenhar(cenas[idx], tag_da_cena(cenas[idx], idx + 1, len(cenas)))
        BUILD.mkdir(parents=True, exist_ok=True)
        destinos = []
        for k, (img, _) in enumerate([passos[len(passos) // 2], passos[-1]]):
            p = BUILD / f"preview-{nome}-{cena_id}-{k}.png"
            img.save(p)
            destinos.append(str(p))
        print("\n".join(destinos))
        return

    if args.capitulos:
        corte = roteiro.CORTES[args.capitulos]
        dir_corte = BUILD / args.capitulos
        t = 0.0
        for cena in corte["cenas"]:
            arq = dir_corte / cena["id"] / "dur.txt"
            if not arq.exists():
                print(f"(renderize {args.capitulos} antes)", file=sys.stderr)
                return
            m, sg = divmod(int(t), 60)
            print(f"{m:d}:{sg:02d} {cena['titulo']}")
            t += float(arq.read_text()) - TRANSICAO
        return

    alvos = list(roteiro.CORTES) if args.todos else args.corte
    if not alvos:
        ap.error("informe --corte NOME, --todos, --listar ou --preview")

    for nome in alvos:
        corte = roteiro.CORTES[nome]
        W, H = corte["aspecto"]
        queimar = {(1080, 1920): (54, 150), (1080, 1350): (48, 120),
                   (1080, 1080): (42, 95)}.get((W, H))
        print(f"== {nome} ({W}x{H}) ==", flush=True)
        destino, total = montar_corte(nome, corte, queimar)
        print(f"   -> {destino}  ({total/60:.1f} min)\n", flush=True)


if __name__ == "__main__":
    main()
