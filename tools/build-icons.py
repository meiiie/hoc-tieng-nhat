#!/usr/bin/env python3
"""Rasterize the existing Neko SVG, leaving safe maskable padding."""
from pathlib import Path
import io
import cairosvg
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
svg=(ROOT/'icons/icon.svg').read_bytes()
for n in [192,512,180]:
 im=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg,output_width=n,output_height=n))).convert('RGBA')
 im.save(ROOT/'icons'/('apple-touch-icon.png' if n==180 else f'icon-{n}.png'))
 if n!=180:
  bg=Image.new('RGBA',(n,n),'#E7E3DE');size=int(n*.76);fg=im.resize((size,size),Image.Resampling.LANCZOS);bg.alpha_composite(fg,((n-size)//2,(n-size)//2));bg.convert('RGB').save(ROOT/'icons'/f'maskable-{n}.png')
