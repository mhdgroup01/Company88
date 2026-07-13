#!/usr/bin/env python3
"""[เลิกใช้แล้ว 2026-07-13] สร้างไอคอนโล่ทอง+ดาว+กุญแจ (โลโก้เดิม)

ตอนนี้โลโก้แอปเปลี่ยนเป็น "ตราตำรวจลาว" (icons/emblem-police.svg) แล้ว —
ไอคอน icon-192/512, maskable, apple-touch เรนเดอร์จาก SVG นั้นผ่าน browser canvas
(ดู CLAUDE.md). สคริปต์นี้เก็บไว้อ้างอิงเท่านั้น ห้ามรันเผลอ ๆ จะเขียนทับไอคอนตราตำรวจ.
รันจริงต้องใส่ --force."""
import os, sys
if '--force' not in sys.argv:
    sys.exit("ยกเลิก: สคริปต์นี้จะเขียนทับไอคอนตราตำรวจ ใส่ --force ถ้าตั้งใจจริง")
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, 'icons')
os.makedirs(OUT, exist_ok=True)

GOLD = (232, 184, 24, 255)        # sun-400
GREEN_DARK = (26, 48, 42, 255)    # forest-800
GRAD_TOP = (47, 86, 68)           # forest-600
GRAD_BOT = (16, 31, 28)           # forest-900

S = 1024  # วาดที่ 1024 แล้วย่อ


def bezier(p0, p1, p2, p3, n=40):
    """สุ่มจุดบน cubic bezier"""
    pts = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        x = mt**3 * p0[0] + 3 * mt**2 * t * p1[0] + 3 * mt * t**2 * p2[0] + t**3 * p3[0]
        y = mt**3 * p0[1] + 3 * mt**2 * t * p1[1] + 3 * mt * t**2 * p2[1] + t**3 * p3[1]
        pts.append((x, y))
    return pts


def shield_points(cx, cy, scale):
    """โล่ตาม path ของ emblem ใน index.html (viewBox 48) หดเข้าศูนย์กลาง (24,24)"""
    def m(x, y):
        return (cx + (x - 24) * scale, cy + (y - 24) * scale)
    pts = [m(24, 3), m(41, 9), m(41, 22)]
    pts += bezier(m(41, 22), m(41, 33), m(34, 41), m(24, 45))
    pts += bezier(m(24, 45), m(14, 41), m(7, 33), m(7, 22))
    pts += [m(7, 9)]
    return pts


def star_points(cx, cy, r_out, r_in):
    import math
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        a = math.pi / 2 + i * math.pi / 5  # เริ่มแหลมขึ้นบน
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
    return pts


def gradient_bg(size):
    img = Image.new('RGBA', (size, size))
    d = ImageDraw.Draw(img)
    for y in range(size):
        t = y / size
        col = tuple(round(GRAD_TOP[i] + (GRAD_BOT[i] - GRAD_TOP[i]) * t) for i in range(3)) + (255,)
        d.line([(0, y), (size, y)], fill=col)
    return img


def draw_art(img, cx, cy, k):
    """วาดโล่+ดาว+กุญแจ; k = scale (พิกเซลต่อหน่วย viewBox 48)"""
    d = ImageDraw.Draw(img)
    d.polygon(shield_points(cx, cy, k), fill=GOLD)
    d.polygon(shield_points(cx, cy, k * 0.855), fill=GREEN_DARK)
    # ดาว 5 แฉก
    scx, scy = cx, cy + (19.0 - 24) * k
    d.polygon(star_points(scx, scy, 6.6 * k, 2.65 * k), fill=GOLD)
    # แม่กุญแจ: ห่วง (arc) + ตัวเรือน
    body_w, body_h = 10 * k, 7.2 * k
    bx0, by0 = cx - body_w / 2, cy + (30 - 24) * k
    r = 3.1 * k
    lw = max(2, round(1.9 * k))
    d.arc([cx - r, by0 - r - lw * 0.2, cx + r, by0 + r], 180, 360, fill=GOLD, width=lw)
    d.rounded_rectangle([bx0, by0, bx0 + body_w, by0 + body_h], radius=1.7 * k, fill=GOLD)
    # รูกุญแจ
    kr = 1.15 * k
    kcx, kcy = cx, by0 + body_h * 0.42
    d.ellipse([kcx - kr, kcy - kr, kcx + kr, kcy + kr], fill=GREEN_DARK)
    d.rectangle([kcx - kr * 0.45, kcy, kcx + kr * 0.45, kcy + body_h * 0.32], fill=GREEN_DARK)


def rounded_mask(size, radius):
    m = Image.new('L', (size, size), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    return m


def make(filename, out_size, art_ratio, rounded):
    img = gradient_bg(S)
    k = (S * art_ratio) / 48.0
    draw_art(img, S / 2, S / 2, k)
    if rounded:
        img.putalpha(rounded_mask(S, round(S * 0.225)))
    img = img.resize((out_size, out_size), Image.LANCZOS)
    if not rounded:
        img = img.convert('RGB')  # apple-touch/maskable ไม่ต้องโปร่ง
        img.save(os.path.join(OUT, filename), 'PNG')
    else:
        img.save(os.path.join(OUT, filename), 'PNG')
    print('✓', filename, out_size)


make('icon-512.png', 512, 0.94, rounded=True)
make('icon-192.png', 192, 0.94, rounded=True)
make('icon-maskable-512.png', 512, 0.62, rounded=False)   # กันขอบ safe zone
make('apple-touch-icon.png', 180, 0.78, rounded=False)
print('done →', OUT)
