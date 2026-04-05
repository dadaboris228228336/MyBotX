#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Создаёт иконку MyBotX.ico"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_icon():
    sizes = [16, 32, 48, 64, 128, 256]
    images = []
    for size in sizes:
        img = Image.new("RGBA", (size, size), (13, 13, 13, 255))
        draw = ImageDraw.Draw(img)
        # Зелёный круг фон
        margin = size // 8
        draw.ellipse([margin, margin, size-margin, size-margin],
                     fill=(0, 255, 136, 255))
        # Буква M по центру
        font_size = int(size * 0.55)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()
        text = "M"
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (size - tw) // 2 - bbox[0]
        y = (size - th) // 2 - bbox[1]
        draw.text((x, y), text, fill=(13, 13, 13, 255), font=font)
        images.append(img)

    out = Path(__file__).parent / "mybotx.ico"
    images[0].save(out, format="ICO", sizes=[(s, s) for s in sizes],
                   append_images=images[1:])
    print(f"✅ Иконка создана: {out}")

if __name__ == "__main__":
    create_icon()
