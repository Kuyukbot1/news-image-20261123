#!/usr/bin/env python3
"""Draw the Monday 23 November 2026 front page: 50 verified stories, 1024x1024 PNG.

Written fresh for news-image-20261123. Uses only the Python standard library
plus Pillow (build-time drawing); the shipped entry.png is drawn by this file.
Layout (evolved winning format): giant masthead date, UTC timeline ruler,
15 illustrated feature cards with per-card verification labels, world map with
numbered pins, region-grouped ALSO ON list, DATE CHECK box, sources footer.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 242, 231)
INK = (26, 26, 26)
NAVY = (27, 58, 107)
RED = (164, 30, 34)
GOLD = (178, 134, 11)
TEAL = (14, 94, 94)
PURPLE = (96, 60, 120)
GREEN = (46, 110, 60)
GREY = (90, 86, 78)
CARD_BG = (255, 253, 247)
RULE = (180, 172, 152)
MAP_LAND = (206, 186, 148)
MAP_SEA = (214, 229, 238)
DATE_BG = (250, 235, 232)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def tw(d, s, f):
    return d.textlength(s, font=f)


def wrap(d, s, f, max_w):
    """Greedy word wrap; returns list of lines."""
    lines, cur = [], ""
    for word in s.split(" "):
        trial = (cur + " " + word).strip()
        if tw(d, trial, f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def trunc(d, s, f, max_w):
    """Truncate to one line with an ellipsis."""
    if tw(d, s, f) <= max_w:
        return s
    while s and tw(d, s + "…", f) > max_w:
        s = s[:-1]
    return s + "…"


def draw_wrapped(d, x, y, s, f, max_w, fill, lh, max_lines=None):
    """Draw wrapped text; returns y just below the last line drawn."""
    lines = wrap(d, s, f, max_w)
    if max_lines is not None:
        lines = lines[:max_lines]
        if len(wrap(d, s, f, max_w)) > max_lines and lines:
            lines[-1] = trunc(d, lines[-1], f, max_w)
    for ln in lines:
        d.text((x, y), ln, font=f, fill=fill)
        y += lh
    return y


def centre(d, cx, y, s, f, fill):
    d.text((cx - tw(d, s, f) / 2, y), s, font=f, fill=fill)


def spaced_centre(d, cx, y, s, f, fill, track=3):
    """Centred text with letter tracking."""
    widths = [d.textlength(ch, font=f) for ch in s]
    total = sum(widths) + track * (len(s) - 1)
    x = cx - total / 2
    for ch, w in zip(s, widths):
        d.text((x, y), ch, font=f, fill=fill)
        x += w + track


# ---------------------------------------------------------------- map
# Simplified continent outlines (lon, lat). Equirectangular, cropped to
# lat -58..84, drawn into the map box with a vertical squash.
CONTINENTS = [
    # North America
    [(-168, 66), (-165, 60), (-158, 58), (-152, 60), (-140, 60), (-135, 57),
     (-130, 54), (-125, 49), (-124, 42), (-120, 34), (-114, 29), (-110, 24),
     (-105, 20), (-97, 16), (-94, 17), (-90, 14), (-86, 12), (-83, 9),
     (-80, 8), (-77, 7), (-79, 9), (-81, 13), (-83, 15), (-86, 16),
     (-88, 18), (-90, 21), (-91, 19), (-94, 19), (-97, 22), (-97, 26),
     (-93, 30), (-89, 30), (-84, 30), (-81, 25), (-80, 32), (-76, 35),
     (-74, 40), (-70, 42), (-68, 45), (-65, 44), (-60, 46), (-55, 47),
     (-60, 52), (-64, 58), (-68, 58), (-72, 62), (-78, 62), (-85, 66),
     (-92, 66), (-95, 69), (-110, 68), (-125, 70), (-140, 70), (-155, 71),
     (-165, 68)],
    # Greenland
    [(-58, 64), (-52, 60), (-43, 60), (-40, 64), (-32, 68), (-22, 70),
     (-20, 74), (-25, 78), (-35, 80), (-55, 80), (-60, 76), (-68, 76),
     (-62, 70)],
    # South America
    [(-77, 7), (-75, 10), (-72, 12), (-64, 10), (-60, 8), (-55, 6),
     (-52, 5), (-50, 0), (-44, -3), (-38, -5), (-35, -8), (-38, -13),
     (-40, -20), (-48, -27), (-52, -32), (-57, -38), (-62, -41), (-65, -45),
     (-68, -50), (-69, -52), (-71, -54), (-74, -50), (-73, -44), (-73, -37),
     (-71, -30), (-70, -23), (-70, -18), (-75, -15), (-77, -12), (-80, -6),
     (-81, -1), (-80, 1), (-77, 4)],
    # Africa
    [(-17, 15), (-17, 21), (-15, 27), (-10, 31), (-6, 33), (0, 36),
     (10, 37), (11, 34), (20, 32), (30, 31), (32, 31), (34, 28), (37, 22),
     (39, 18), (40, 15), (43, 12), (48, 11), (51, 12), (48, 5), (42, 0),
     (40, -5), (40, -10), (38, -15), (36, -20), (33, -26), (28, -33),
     (20, -35), (17, -32), (15, -27), (13, -20), (12, -15), (13, -10),
     (12, -5), (9, 0), (9, 4), (4, 6), (-2, 5), (-8, 5), (-13, 8), (-17, 12)],
    # Eurasia
    [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-2, 50),
     (0, 51), (3, 53), (5, 53), (8, 55), (8, 57), (10, 59), (5, 60),
     (5, 62), (10, 64), (12, 66), (18, 69), (25, 71), (32, 70), (40, 68),
     (44, 68), (50, 69), (55, 68), (60, 69), (68, 73), (75, 73), (80, 73),
     (90, 75), (100, 76), (110, 74), (120, 73), (130, 72), (140, 72),
     (150, 70), (158, 69), (162, 66), (170, 66), (178, 65), (178, 62),
     (170, 60), (162, 60), (158, 55), (156, 51), (150, 59), (142, 55),
     (140, 50), (135, 44), (130, 42), (127, 40), (122, 38), (120, 35),
     (122, 31), (120, 28), (118, 25), (110, 21), (108, 18), (105, 10),
     (103, 8), (100, 7), (98, 10), (97, 15), (94, 17), (92, 21), (89, 22),
     (86, 20), (82, 17), (80, 13), (77, 8), (76, 10), (73, 16), (70, 21),
     (66, 25), (62, 25), (58, 25), (56, 27), (54, 27), (52, 28), (50, 30),
     (48, 30), (44, 29), (43, 26), (40, 22), (39, 21), (38, 18), (36, 15),
     (35, 12), (34, 10), (33, 13), (35, 16), (37, 20), (39, 24), (40, 28),
     (42, 31), (38, 34), (36, 36), (33, 36), (30, 36), (27, 37), (26, 38),
     (23, 36), (22, 37), (20, 40), (19, 42), (16, 44), (14, 45), (12, 44),
     (10, 44), (8, 44), (7, 44), (3, 43), (0, 40), (-2, 37), (-6, 36),
     (-9, 37)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
     (-3, 50)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (137, 35), (139, 37), (141, 39),
     (141, 41), (143, 42), (145, 44), (142, 45), (140, 44), (139, 42),
     (137, 38), (135, 35), (133, 34)],
    # Borneo
    [(109, 1), (113, 4), (117, 6), (119, 1), (116, -3), (111, -3), (109, 0)],
    # Sumatra
    [(95, 5), (100, 0), (104, -3), (106, -6), (103, -5), (100, -1), (96, 4)],
    # Java
    [(105, -6), (110, -7), (114, -8), (114, -9), (108, -8), (105, -7)],
    # New Guinea
    [(131, -1), (136, -2), (141, -3), (146, -6), (147, -9), (142, -8),
     (137, -6), (132, -4)],
    # New Zealand
    [(167, -45), (170, -42), (173, -41), (175, -38), (178, -37),
     (176, -40), (173, -42), (170, -44), (167, -46)],
    # Madagascar
    [(44, -16), (47, -15), (50, -16), (49, -20), (47, -24), (44, -25),
     (43, -21)],
    # Australia
    [(113, -22), (114, -30), (115, -33), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (137, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -23), (146, -19), (142, -15), (142, -11),
     (140, -17), (136, -15), (135, -12), (132, -11), (130, -13), (126, -14),
     (122, -17), (118, -20)],
]

MAP_BOX = (16, 586, 1008, 680)  # x0, y0, x1, y1


def project(lon, lat):
    x0, y0, x1, y1 = MAP_BOX
    x = x0 + (lon + 180.0) / 360.0 * (x1 - x0)
    y = y0 + (84.0 - lat) / 142.0 * (y1 - y0)
    return x, y


def draw_map(d):
    x0, y0, x1, y1 = MAP_BOX
    d.rectangle([x0, y0, x1, y1], fill=MAP_SEA, outline=RULE, width=1)
    # graticule: equator + tropics
    for lat, col in ((0, (170, 190, 205)), (23.5, (190, 205, 215)),
                     (-23.5, (190, 205, 215))):
        _, gy = project(0, lat)
        d.line([(x0, gy), (x1, gy)], fill=col, width=1)
    for poly in CONTINENTS:
        pts = [project(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=MAP_LAND, outline=(150, 132, 96))
    # pins: (num, lon, lat, colour) — positions nudged so neighbours do not
    # collide at this scale (pin diameter ~12px ~= 4.4 deg lon)
    pins = [
        (1, 28.0, 35.0, GREY), (2, 50.6, 26.2, RED), (3, 20.1, 32.1, NAVY),
        (4, 33.0, 52.0, NAVY), (5, -74.0, 38.0, TEAL), (6, 106.4, -6.2, GOLD),
        (7, 174.8, -41.3, GREEN), (8, -115.0, 36.0, TEAL),
        (9, 127.0, 37.5, PURPLE), (10, -0.1, 51.5, GREY),
        (11, 35.2, 31.8, RED), (12, -88.0, 34.0, TEAL),
        (13, 77.2, 28.6, PURPLE), (14, -9.1, 38.7, NAVY),
        (15, -82.0, 42.0, TEAL),
    ]
    fnum = font(SANS_B, 8)
    for num, lon, lat, col in pins:
        px, py = project(lon, lat)
        r = 6
        d.ellipse([px - r, py - r, px + r, py + r], fill=col,
                  outline=(255, 255, 255), width=1)
        s = str(num)
        d.text((px - tw(d, s, fnum) / 2, py - 5.5), s, font=fnum,
               fill=(255, 255, 255))


# ---------------------------------------------------------------- scenes
def scene(d, kind, x, y, w, h):
    """A small flat scene of the actual event inside (x, y, w, h)."""
    if kind == "bahrain":
        d.rectangle([x, y, x + w, y + h], fill=(198, 216, 232))
        d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(110, 155, 190))
        for bx, bh in ((0.06, 0.30), (0.20, 0.42), (0.36, 0.26), (0.55, 0.36)):
            d.rectangle([x + w * bx, y + h * 0.62 - h * bh, x + w * (bx + 0.12),
                         y + h * 0.62], fill=(90, 100, 115))
        d.line([(x + w * 0.15, y + h * 0.60), (x + w * 0.45, y + h * 0.18),
                (x + w * 0.72, y + h * 0.55)], fill=(200, 60, 30), width=2)
        for px, py in ((0.45, 0.18), (0.72, 0.55)):
            d.ellipse([x + w * px - 4, y + h * py - 4, x + w * px + 4,
                       y + h * py + 4], fill=(255, 140, 40))
        d.ellipse([x + w * 0.80, y + h * 0.10, x + w * 0.92, y + h * 0.10 + 12],
                  fill=(255, 170, 60))
    elif kind == "riyadh":
        d.rectangle([x, y, x + w, y + h], fill=(232, 205, 165))
        d.rectangle([x, y + h * 0.70, x + w, y + h], fill=(120, 105, 90))
        # Kingdom-Centre-like tower: two legs + arch
        tx, tw_ = x + w * 0.42, w * 0.16
        d.rectangle([tx, y + h * 0.12, tx + tw_ * 0.32, y + h * 0.70],
                    fill=(70, 80, 100))
        d.rectangle([tx + tw_ * 0.68, y + h * 0.12, tx + tw_, y + h * 0.70],
                    fill=(70, 80, 100))
        d.pieslice([tx - 2, y + h * 0.02, tx + tw_ + 2, y + h * 0.30],
                   180, 360, fill=(70, 80, 100))
        d.rectangle([x + w * 0.08, y + h * 0.40, x + w * 0.24, y + h * 0.70],
                    fill=(95, 100, 110))
        d.rectangle([x + w * 0.68, y + h * 0.48, x + w * 0.84, y + h * 0.70],
                    fill=(95, 100, 110))
        d.arc([x + w * 0.05, y - h * 0.15, x + w * 0.55, y + h * 0.75],
              300, 360, fill=(255, 255, 255), width=2)
        d.arc([x + w * 0.45, y - h * 0.10, x + w * 0.95, y + h * 0.80],
              200, 260, fill=(255, 255, 255), width=2)
        d.ellipse([x + w * 0.86, y + h * 0.16, x + w * 0.86 + 9,
                   y + h * 0.16 + 9], fill=(255, 120, 30))
    elif kind == "cop31":
        d.rectangle([x, y, x + w, y + h], fill=(205, 222, 235))
        cx, cy, r = x + w * 0.30, y + h * 0.52, h * 0.34
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(70, 130, 200),
                  outline=NAVY, width=1)
        d.ellipse([cx - r * 0.55, cy - r * 0.6, cx - r * 0.1, cy - r * 0.1],
                  fill=(90, 170, 90))
        d.ellipse([cx + r * 0.1, cy + r * 0.15, cx + r * 0.6, cy + r * 0.6],
                  fill=(90, 170, 90))
        # thermometer
        tx = x + w * 0.66
        d.rectangle([tx, y + h * 0.14, tx + 8, y + h * 0.78], fill=(255, 255, 255),
                    outline=INK, width=1)
        d.rectangle([tx + 1, y + h * 0.34, tx + 7, y + h * 0.78], fill=RED)
        d.ellipse([tx - 3, y + h * 0.72, tx + 11, y + h * 0.72 + 14], fill=RED)
        # flags row
        for i, col in enumerate((RED, NAVY, GOLD, TEAL, GREEN, PURPLE)):
            fx = x + w * (0.08 + i * 0.14)
            d.line([(fx, y + h * 0.86), (fx, y + h * 0.62)], fill=INK, width=1)
            d.rectangle([fx, y + h * 0.62, fx + 12, y + h * 0.72], fill=col)
    elif kind == "kyiv":
        d.rectangle([x, y, x + w, y + h], fill=(38, 48, 78))
        for bx, bh in ((0.04, 0.45), (0.20, 0.60), (0.38, 0.38), (0.55, 0.55),
                       (0.72, 0.42), (0.86, 0.50)):
            d.rectangle([x + w * bx, y + h - h * bh, x + w * (bx + 0.13), y + h],
                        fill=(20, 26, 48))
            for wy in range(2):
                d.rectangle([x + w * bx + 3, y + h - h * bh + 6 + wy * 12,
                             x + w * bx + 7, y + h - h * bh + 10 + wy * 12],
                            fill=(255, 210, 90))
        for dx, dy in ((0.15, 0.18), (0.35, 0.10), (0.55, 0.22), (0.75, 0.12),
                       (0.90, 0.25)):
            d.ellipse([x + w * dx - 2, y + h * dy - 2, x + w * dx + 2,
                       y + h * dy + 2], fill=(255, 255, 255))
            d.line([(x + w * dx, y + h * dy), (x + w * dx - 8, y + h * dy + 8)],
                   fill=(255, 90, 40), width=1)
        d.ellipse([x + w * 0.30, y + h * 0.72, x + w * 0.55, y + h * 0.72 + 14],
                  fill=(255, 140, 40))
    elif kind == "poland":
        d.rectangle([x, y, x + w, y + h], fill=(190, 215, 170))
        d.polygon([(x + w * 0.10, y + h * 0.85), (x + w * 0.45, y + h * 0.15),
                   (x + w * 0.90, y + h * 0.25), (x + w * 0.95, y + h * 0.80),
                   (x + w * 0.55, y + h * 0.95)],
                  fill=(215, 225, 190), outline=(120, 140, 110))
        d.line([(x + w * 0.55, y + h * 0.20), (x + w * 0.62, y + h * 0.55),
                (x + w * 0.58, y + h * 0.80)], fill=RED, width=2)
        d.line([(x + w * 0.70, y + h * 0.15), (x + w * 0.68, y + h * 0.50)],
               fill=RED, width=2)
        for px, py in ((0.62, 0.55), (0.68, 0.50), (0.58, 0.80)):
            d.ellipse([x + w * px - 3, y + h * py - 3, x + w * px + 3,
                       y + h * py + 3], fill=RED)
        d.text((x + w * 0.60, y + h * 0.58), "✕", font=font(SANS_B, 11),
               fill=RED)
    elif kind == "elchapo":
        d.rectangle([x, y, x + w, y + h], fill=(30, 34, 52))
        for bx, bh in ((0.05, 0.50), (0.25, 0.65), (0.60, 0.45), (0.78, 0.60)):
            d.rectangle([x + w * bx, y + h - h * bh, x + w * (bx + 0.16), y + h],
                        fill=(55, 60, 85))
            d.rectangle([x + w * bx + 3, y + h - h * bh + 5, x + w * bx + 7,
                         y + h - h * bh + 9], fill=(255, 220, 100))
        # helicopter + searchlight
        hx, hy = x + w * 0.55, y + h * 0.20
        d.ellipse([hx, hy, hx + 26, hy + 10], fill=(200, 200, 210))
        d.line([(hx - 8, hy + 2), (hx + 34, hy + 2)], fill=(200, 200, 210),
               width=2)
        d.line([(hx + 26, hy + 5), (hx + 40, hy + 5)], fill=(200, 200, 210),
               width=2)
        d.polygon([(hx + 6, hy + 10), (hx + 20, hy + 10),
                   (x + w * 0.78, y + h), (x + w * 0.58, y + h)],
                  fill=(255, 240, 150))
        # badge star
        sx, sy = x + w * 0.12, y + h * 0.18
        d.ellipse([sx, sy, sx + 14, sy + 14], fill=GOLD, outline=(255, 255, 255))
        d.text((sx + 4, sy + 1), "★", font=font(SANS_B, 10), fill=(255, 255, 255))
    elif kind == "nigeria":
        d.rectangle([x, y, x + w, y + h], fill=(150, 195, 225))
        d.rectangle([x, y + h * 0.55, x + w, y + h], fill=(60, 120, 175))
        for wy in (0.62, 0.72, 0.84):
            d.arc([x + w * 0.05, y + h * wy, x + w * 0.95, y + h * wy + 10],
                  0, 180, fill=(255, 255, 255), width=1)
        # capsized boat: hull upside down
        d.polygon([(x + w * 0.30, y + h * 0.52), (x + w * 0.70, y + h * 0.52),
                   (x + w * 0.62, y + h * 0.38), (x + w * 0.38, y + h * 0.38)],
                  fill=(120, 70, 40))
        for fx, fy in ((0.34, 0.44), (0.66, 0.42), (0.50, 0.30)):
            d.ellipse([x + w * fx - 3, y + h * fy - 3, x + w * fx + 3,
                       y + h * fy + 3], fill=(40, 30, 25))
            d.line([(x + w * fx, y + h * fy - 3), (x + w * fx, y + h * fy - 10)],
                   fill=(40, 30, 25), width=2)
    elif kind == "ship":
        d.rectangle([x, y, x + w, y + h], fill=(170, 195, 215))
        d.rectangle([x, y + h * 0.60, x + w, y + h], fill=(70, 120, 165))
        # hull + containers
        d.polygon([(x + w * 0.08, y + h * 0.58), (x + w * 0.92, y + h * 0.58),
                   (x + w * 0.84, y + h * 0.78), (x + w * 0.16, y + h * 0.78)],
                  fill=(40, 45, 60))
        for i, col in enumerate((RED, GOLD, TEAL, NAVY)):
            d.rectangle([x + w * (0.16 + i * 0.15), y + h * 0.36,
                         x + w * (0.28 + i * 0.15), y + h * 0.56], fill=col)
        # flames + smoke
        for fx, fh in ((0.30, 0.22), (0.50, 0.30), (0.68, 0.20)):
            d.ellipse([x + w * fx - 6, y + h * 0.36 - h * fh,
                       x + w * fx + 6, y + h * 0.36], fill=(255, 140, 30))
            d.ellipse([x + w * fx - 3, y + h * 0.36 - h * fh,
                       x + w * fx + 3, y + h * 0.36], fill=(255, 220, 80))
        for sx, sy, sr in ((0.35, 0.14, 7), (0.52, 0.08, 9), (0.66, 0.16, 6)):
            d.ellipse([x + w * sx - sr, y + h * sy - sr, x + w * sx + sr,
                       y + h * sy + sr], fill=(120, 120, 125))
    elif kind == "card":
        d.rectangle([x, y, x + w, y + h], fill=(225, 225, 215))
        # Capitol dome
        d.rectangle([x + w * 0.06, y + h * 0.55, x + w * 0.44, y + h * 0.85],
                    fill=(245, 245, 240), outline=(150, 150, 140))
        d.pieslice([x + w * 0.16, y + h * 0.18, x + w * 0.34, y + h * 0.62],
                   180, 360, fill=(245, 245, 240), outline=(150, 150, 140))
        d.rectangle([x + w * 0.24, y + h * 0.10, x + w * 0.26, y + h * 0.20],
                    fill=(150, 150, 140))
        # credit card
        cx, cy = x + w * 0.52, y + h * 0.30
        d.rounded_rectangle([cx, cy, cx + w * 0.42, cy + h * 0.52], radius=4,
                            fill=NAVY)
        d.rectangle([cx + 6, cy + 8, cx + 22, cy + 20], fill=GOLD)
        d.text((cx + 6, cy + h * 0.30), "10%", font=font(SANS_B, 13),
               fill=(255, 255, 255))
    elif kind == "fbi":
        d.rectangle([x, y, x + w, y + h], fill=(35, 40, 55))
        for i in range(3):
            rx = x + w * (0.06 + i * 0.20)
            d.rectangle([rx, y + h * 0.18, rx + w * 0.15, y + h * 0.85],
                        fill=(60, 66, 82), outline=(120, 125, 140))
            for ly in range(4):
                d.ellipse([rx + 4, y + h * (0.26 + ly * 0.14),
                           rx + 8, y + h * (0.26 + ly * 0.14) + 4],
                          fill=(80, 220, 120) if ly != 2 else RED)
        # shield with crack
        sx, sy = x + w * 0.70, y + h * 0.22
        d.polygon([(sx, sy), (sx + 22, sy), (sx + 22, sy + 14),
                   (sx + 11, sy + 28), (sx, sy + 14)], fill=(60, 110, 200),
                  outline=(255, 255, 255))
        d.line([(sx + 11, sy + 2), (sx + 7, sy + 12), (sx + 13, sy + 18),
                (sx + 9, sy + 26)], fill=(255, 255, 255), width=2)
    elif kind == "gaza":
        d.rectangle([x, y, x + w, y + h], fill=(228, 210, 185))
        d.rectangle([x, y + h * 0.68, x + w, y + h], fill=(170, 150, 125))
        # aid truck
        tx = x + w * 0.14
        d.rectangle([tx, y + h * 0.38, tx + w * 0.42, y + h * 0.68],
                    fill=(245, 245, 240), outline=INK, width=1)
        d.rectangle([tx + w * 0.42, y + h * 0.46, tx + w * 0.56, y + h * 0.68],
                    fill=(200, 60, 40))
        d.text((tx + 4, y + h * 0.46), "AID", font=font(SANS_B, 11), fill=RED)
        for wx in (0.22, 0.52):
            d.ellipse([x + w * wx - 5, y + h * 0.66 - 5, x + w * wx + 5,
                       y + h * 0.66 + 5], fill=INK)
        # smoke plumes
        for sx, sy, sr in ((0.72, 0.30, 9), (0.82, 0.18, 12), (0.90, 0.34, 7)):
            d.ellipse([x + w * sx - sr, y + h * sy - sr, x + w * sx + sr,
                       y + h * sy + sr], fill=(140, 135, 130))
        for bx in (0.66, 0.74):
            d.rectangle([x + w * bx, y + h * 0.78, x + w * bx + 0.06,
                         y + h * 0.88], fill=(150, 110, 70))
    elif kind == "basra":
        d.rectangle([x, y, x + w, y + h], fill=(220, 200, 170))
        d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(140, 125, 105))
        for i, tx in enumerate((0.12, 0.40, 0.68)):
            d.polygon([(x + w * tx, y + h * 0.72), (x + w * (tx + 0.16),
                       y + h * 0.72), (x + w * (tx + 0.13), y + h * 0.30),
                      (x + w * (tx + 0.03), y + h * 0.30)],
                     fill=(180, 175, 165), outline=(120, 115, 105))
        for fx in (0.20, 0.48, 0.76):
            d.ellipse([x + w * fx - 7, y + h * 0.62, x + w * fx + 7,
                       y + h * 0.62 + 12], fill=(255, 140, 30))
            d.ellipse([x + w * fx - 3, y + h * 0.66, x + w * fx + 3,
                       y + h * 0.66 + 8], fill=(255, 220, 80))
        for sx, sy, sr in ((0.30, 0.16, 8), (0.60, 0.10, 10), (0.85, 0.20, 6)):
            d.ellipse([x + w * sx - sr, y + h * sy - sr, x + w * sx + sr,
                       y + h * sy + sr], fill=(110, 108, 105))
    elif kind == "cricket":
        d.rectangle([x, y, x + w, y + h], fill=(120, 175, 110))
        d.rectangle([x + w * 0.30, y, x + w * 0.70, y + h], fill=(190, 165, 110))
        # stumps
        for i in range(3):
            sx = x + w * (0.44 + i * 0.03)
            d.line([(sx, y + h * 0.78), (sx, y + h * 0.58)], fill=(255, 220, 80),
                   width=2)
        # batsman
        bx, by = x + w * 0.60, y + h * 0.45
        d.ellipse([bx - 5, by - 14, bx + 5, by - 4], fill=(60, 40, 30))
        d.line([(bx, by - 4), (bx, by + 12)], fill=(30, 60, 120), width=4)
        d.line([(bx, by + 12), (bx - 8, by + 26)], fill=(30, 60, 120), width=3)
        d.line([(bx, by + 12), (bx + 8, by + 26)], fill=(30, 60, 120), width=3)
        d.line([(bx + 2, by + 2), (bx + 14, by + 20)], fill=(180, 140, 90),
               width=3)
        # scoreboard
        d.rectangle([x + w * 0.72, y + h * 0.10, x + w * 0.97, y + h * 0.34],
                    fill=INK)
        d.text((x + w * 0.74, y + h * 0.13), "720/9", font=font(SANS_B, 11),
               fill=(255, 255, 255))
    elif kind == "chahal":
        d.rectangle([x, y, x + w, y + h], fill=(235, 225, 205))
        # flag stripes
        for i, col in enumerate(((255, 153, 51), (255, 255, 255), (19, 136, 8))):
            d.rectangle([x + w * 0.06, y + h * (0.16 + i * 0.16),
                         x + w * 0.94, y + h * (0.32 + i * 0.16)], fill=col)
        d.ellipse([x + w * 0.44, y + h * 0.34, x + w * 0.56, y + h * 0.34 + 12],
                  outline=NAVY, width=2)
        # cricket ball
        bx, by, br = x + w * 0.50, y + h * 0.72, 11
        d.ellipse([bx - br, by - br, bx + br, by + br], fill=(178, 34, 34),
                  outline=(120, 20, 20), width=1)
        d.arc([bx - br + 3, by - br + 3, bx + br - 3, by + br - 3], 40, 140,
              fill=(255, 255, 255), width=1)
    elif kind == "bitcoin":
        d.rectangle([x, y, x + w, y + h], fill=(235, 228, 200))
        # chart: dip then rebound
        pts = [(x + w * 0.08, y + h * 0.35), (x + w * 0.25, y + h * 0.55),
               (x + w * 0.42, y + h * 0.72), (x + w * 0.60, y + h * 0.50),
               (x + w * 0.78, y + h * 0.30), (x + w * 0.92, y + h * 0.18)]
        d.line(pts, fill=(20, 130, 60), width=3, joint="curve")
        for px, py in pts[1:-1]:
            d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(20, 130, 60))
        d.line([(x + w * 0.06, y + h * 0.85), (x + w * 0.96, y + h * 0.85)],
               fill=GREY, width=1)
        # coin
        cx, cy, cr = x + w * 0.80, y + h * 0.62, 13
        d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=GOLD,
                  outline=(140, 100, 10), width=2)
        d.text((cx - 6, cy - 8), "₿", font=font(SANS_B, 13), fill=(255, 255, 255))


    elif kind == "merkury":
        d.rectangle([x, y, x + w, y + h], fill=(150, 170, 200))
        d.rectangle([x, y + h * 0.58, x + w, y + h], fill=(50, 95, 135))
        # capsized corvette: hull tipped, bow up
        d.polygon([(x + w * 0.12, y + h * 0.62), (x + w * 0.55, y + h * 0.55),
                   (x + w * 0.62, y + h * 0.42), (x + w * 0.42, y + h * 0.30),
                   (x + w * 0.30, y + h * 0.44), (x + w * 0.18, y + h * 0.52)],
                  fill=(70, 75, 85))
        d.rectangle([x + w * 0.58, y + h * 0.38, x + w * 0.66, y + h * 0.44],
                    fill=(90, 95, 105))
        # explosion + smoke over the harbour
        for fx, fy, fr in ((0.55, 0.30, 10), (0.66, 0.22, 13), (0.78, 0.32, 8)):
            d.ellipse([x + w * fx - fr, y + h * fy - fr, x + w * fx + fr,
                       y + h * fy + fr], fill=(255, 140, 30))
        for sx, sy, sr in ((0.60, 0.12, 8), (0.72, 0.08, 10), (0.84, 0.16, 6)):
            d.ellipse([x + w * sx - sr, y + h * sy - sr, x + w * sx + sr,
                       y + h * sy + sr], fill=(110, 110, 115))
        # harbour wall + drone boat wake
        d.rectangle([x, y + h * 0.86, x + w, y + h], fill=(120, 110, 95))
        d.line([(x + w * 0.70, y + h * 0.72), (x + w * 0.90, y + h * 0.68)],
               fill=(255, 255, 255), width=2)
    elif kind == "dymer":
        d.rectangle([x, y, x + w, y + h], fill=(40, 46, 72))
        # apartment block, middle section collapsed
        d.rectangle([x + w * 0.08, y + h * 0.20, x + w * 0.40, y + h * 0.82],
                    fill=(140, 135, 125))
        d.rectangle([x + w * 0.60, y + h * 0.28, x + w * 0.92, y + h * 0.82],
                    fill=(140, 135, 125))
        for wx in (0.14, 0.24, 0.34, 0.66, 0.76, 0.86):
            for wy in (0.30, 0.44, 0.58):
                d.rectangle([x + w * wx, y + h * wy, x + w * wx + 6,
                             y + h * wy + 7], fill=(255, 210, 90))
        # rubble pile + rescue searchlight
        d.polygon([(x + w * 0.40, y + h * 0.82), (x + w * 0.60, y + h * 0.82),
                   (x + w * 0.55, y + h * 0.60), (x + w * 0.45, y + h * 0.60)],
                  fill=(90, 85, 80))
        d.polygon([(x + w * 0.82, y + h * 0.82), (x + w * 0.90, y + h * 0.82),
                   (x + w * 0.50, y + h * 0.55), (x + w * 0.46, y + h * 0.62)],
                  fill=(255, 240, 150))
        d.ellipse([x + w * 0.50, y + h * 0.52, x + w * 0.50 + 6,
                   y + h * 0.52 + 6], fill=(255, 120, 30))
    elif kind == "house258":
        d.rectangle([x, y, x + w, y + h], fill=(225, 228, 235))
        # Capitol dome
        d.rectangle([x + w * 0.30, y + h * 0.55, x + w * 0.70, y + h * 0.85],
                    fill=(245, 245, 240), outline=(150, 150, 140))
        d.pieslice([x + w * 0.40, y + h * 0.22, x + w * 0.60, y + h * 0.58],
                   180, 360, fill=(245, 245, 240), outline=(150, 150, 140))
        d.rectangle([x + w * 0.49, y + h * 0.12, x + w * 0.51, y + h * 0.24],
                    fill=(150, 150, 140))
        # big 258 banner
        d.rectangle([x + w * 0.06, y + h * 0.06, x + w * 0.42, y + h * 0.34],
                    fill=NAVY)
        d.text((x + w * 0.09, y + h * 0.10), "258", font=font(SANS_B, 16),
               fill=(255, 255, 255))
        # seats bar: blue majority
        d.rectangle([x + w * 0.06, y + h * 0.42, x + w * 0.94, y + h * 0.48],
                    fill=(200, 60, 50))
        d.rectangle([x + w * 0.06, y + h * 0.42, x + w * 0.65, y + h * 0.48],
                    fill=(40, 80, 180))
    elif kind == "factory":
        d.rectangle([x, y, x + w, y + h], fill=(210, 195, 175))
        d.rectangle([x, y + h * 0.70, x + w, y + h], fill=(130, 118, 100))
        # factory shed + chimney
        d.rectangle([x + w * 0.10, y + h * 0.42, x + w * 0.70, y + h * 0.72],
                    fill=(170, 160, 145), outline=(110, 105, 95))
        d.polygon([(x + w * 0.08, y + h * 0.44), (x + w * 0.40, y + h * 0.28),
                   (x + w * 0.72, y + h * 0.44)], fill=(120, 110, 100))
        d.rectangle([x + w * 0.76, y + h * 0.16, x + w * 0.86, y + h * 0.72],
                    fill=(150, 140, 130))
        for fx in (0.22, 0.42, 0.60):
            d.ellipse([x + w * fx - 8, y + h * 0.55, x + w * fx + 8,
                       y + h * 0.55 + 13], fill=(255, 140, 30))
            d.ellipse([x + w * fx - 4, y + h * 0.60, x + w * fx + 4,
                       y + h * 0.60 + 9], fill=(255, 220, 80))
        for sx, sy, sr in ((0.30, 0.14, 8), (0.55, 0.08, 11), (0.80, 0.06, 7)):
            d.ellipse([x + w * sx - sr, y + h * sy - sr, x + w * sx + sr,
                       y + h * sy + sr], fill=(105, 102, 100))
    elif kind == "f1":
        d.rectangle([x, y, x + w, y + h], fill=(25, 22, 45))
        # neon strip + skyline
        for bx, bh in ((0.04, 0.35), (0.18, 0.55), (0.36, 0.42), (0.58, 0.60),
                       (0.76, 0.48)):
            d.rectangle([x + w * bx, y + h - h * bh, x + w * (bx + 0.12), y + h],
                        fill=(45, 40, 80))
            for wy in range(3):
                d.rectangle([x + w * bx + 2, y + h - h * bh + 4 + wy * 9,
                             x + w * bx + 6, y + h - h * bh + 8 + wy * 9],
                            fill=(255, 200, 60))
        # race car silhouette + headlights
        cx, cy = x + w * 0.50, y + h * 0.62
        d.polygon([(cx - 26, cy + 6), (cx - 22, cy - 2), (cx - 6, cy - 6),
                   (cx + 14, cy - 6), (cx + 26, cy + 2), (cx + 24, cy + 6)],
                  fill=(200, 30, 40))
        for wx in (-28, 24):
            d.ellipse([cx + wx - 4, cy + 2, cx + wx + 4, cy + 10], fill=INK)
        d.polygon([(cx + 26, cy), (cx + 44, cy - 6), (cx + 44, cy + 6)],
                  fill=(255, 240, 150))
        # chequered flag
        for r in range(2):
            for c in range(4):
                col = INK if (r + c) % 2 == 0 else (255, 255, 255)
                d.rectangle([x + w * (0.84 + c * 0.04), y + h * (0.10 + r * 0.08),
                             x + w * (0.88 + c * 0.04), y + h * (0.18 + r * 0.08)],
                            fill=col)
    elif kind == "exam":
        d.rectangle([x, y, x + w, y + h], fill=(235, 230, 215))
        # exam paper + phone with AI spark
        d.rectangle([x + w * 0.10, y + h * 0.18, x + w * 0.55, y + h * 0.85],
                    fill=(255, 255, 255), outline=INK, width=1)
        for i in range(4):
            d.line([(x + w * 0.16, y + h * (0.28 + i * 0.12)),
                    (x + w * 0.49, y + h * (0.28 + i * 0.12))], fill=GREY, width=1)
        d.text((x + w * 0.16, y + h * 0.20), "Q1 ✓ Q2 ✓", font=font(SANS_B, 9),
               fill=TEAL)
        # phone
        d.rounded_rectangle([x + w * 0.62, y + h * 0.22, x + w * 0.88, y + h * 0.78],
                            radius=4, fill=INK)
        d.text((x + w * 0.66, y + h * 0.40), "AI", font=font(SANS_B, 16),
               fill=(120, 220, 255))
        # red X over the phone
        d.line([(x + w * 0.60, y + h * 0.20), (x + w * 0.90, y + h * 0.80)],
               fill=RED, width=3)
        d.line([(x + w * 0.90, y + h * 0.20), (x + w * 0.60, y + h * 0.80)],
               fill=RED, width=3)
    elif kind == "knesset":
        d.rectangle([x, y, x + w, y + h], fill=(220, 222, 228))
        # podium + microphones
        d.rectangle([x + w * 0.30, y + h * 0.45, x + w * 0.70, y + h * 0.85],
                    fill=(90, 70, 60))
        d.rectangle([x + w * 0.34, y + h * 0.50, x + w * 0.66, y + h * 0.56],
                    fill=(245, 245, 240))
        d.line([(x + w * 0.42, y + h * 0.45), (x + w * 0.38, y + h * 0.28)],
               fill=INK, width=2)
        d.line([(x + w * 0.58, y + h * 0.45), (x + w * 0.62, y + h * 0.28)],
               fill=INK, width=2)
        d.ellipse([x + w * 0.36, y + h * 0.24, x + w * 0.36 + 6,
                   y + h * 0.24 + 6], fill=INK)
        d.ellipse([x + w * 0.60, y + h * 0.24, x + w * 0.60 + 6,
                   y + h * 0.24 + 6], fill=INK)
        # two small flags behind
        for i, col in enumerate((NAVY, (0, 120, 180))):
            fx = x + w * (0.10 + i * 0.14)
            d.line([(fx, y + h * 0.85), (fx, y + h * 0.30)], fill=INK, width=1)
            d.rectangle([fx, y + h * 0.30, fx + 14, y + h * 0.42], fill=col)
        d.text((x + w * 0.78, y + h * 0.14), "!", font=font(SANS_B, 16),
               fill=RED)
    elif kind == "delta":
        d.rectangle([x, y, x + w, y + h], fill=(180, 200, 225))
        # plane + delay board
        d.ellipse([x + w * 0.10, y + h * 0.30, x + w * 0.55, y + h * 0.42],
                  fill=(245, 245, 250))
        d.polygon([(x + w * 0.52, y + h * 0.30), (x + w * 0.72, y + h * 0.34),
                   (x + w * 0.52, y + h * 0.42)], fill=(245, 245, 250))
        d.polygon([(x + w * 0.30, y + h * 0.30), (x + w * 0.36, y + h * 0.16),
                   (x + w * 0.44, y + h * 0.30)], fill=(200, 40, 50))
        d.ellipse([x + w * 0.12, y + h * 0.32, x + w * 0.12 + 8,
                   y + h * 0.32 + 8], fill=(120, 180, 255))
        # departure board
        d.rectangle([x + w * 0.60, y + h * 0.55, x + w * 0.96, y + h * 0.90],
                    fill=INK)
        d.text((x + w * 0.63, y + h * 0.58), "DELAYED", font=font(SANS_B, 11),
               fill=(255, 180, 40))
        d.text((x + w * 0.63, y + h * 0.72), "DELAYED", font=font(SANS_B, 11),
               fill=(255, 180, 40))
        d.line([(x + w * 0.06, y + h * 0.85), (x + w * 0.94, y + h * 0.85)],
               fill=GREY, width=1)
    elif kind == "nepal":
        d.rectangle([x, y, x + w, y + h], fill=(232, 222, 200))
        # table with two flags: Nepal (crimson) + India (saffron/white/green)
        d.rectangle([x, y + h * 0.70, x + w, y + h], fill=(120, 90, 60))
        d.line([(x + w * 0.28, y + h * 0.70), (x + w * 0.28, y + h * 0.25)],
               fill=INK, width=1)
        d.polygon([(x + w * 0.28, y + h * 0.25), (x + w * 0.46, y + h * 0.34),
                   (x + w * 0.28, y + h * 0.43)], fill=(220, 20, 60))
        d.line([(x + w * 0.72, y + h * 0.70), (x + w * 0.72, y + h * 0.25)],
               fill=INK, width=1)
        for i, col in enumerate(((255, 153, 51), (255, 255, 255), (19, 136, 8))):
            d.rectangle([x + w * 0.72, y + h * (0.25 + i * 0.09),
                         x + w * 0.90, y + h * (0.34 + i * 0.09)], fill=col)
        # handshake dots
        d.ellipse([x + w * 0.46, y + h * 0.60, x + w * 0.46 + 7,
                   y + h * 0.60 + 7], fill=GOLD)
        d.ellipse([x + w * 0.54, y + h * 0.60, x + w * 0.54 + 7,
                   y + h * 0.60 + 7], fill=GOLD)
    elif kind == "march":
        d.rectangle([x, y, x + w, y + h], fill=(215, 205, 190))
        # street + crowd with placards
        d.rectangle([x, y + h * 0.68, x + w, y + h], fill=(150, 140, 130))
        for i, px in enumerate((0.08, 0.24, 0.40, 0.56, 0.72, 0.86)):
            col = (NAVY, RED, TEAL, GOLD, PURPLE, GREEN)[i]
            d.ellipse([x + w * px, y + h * 0.52, x + w * px + 9,
                       y + h * 0.52 + 9], fill=(60, 45, 35))
            d.rectangle([x + w * px - 2, y + h * 0.61, x + w * px + 11,
                         y + h * 0.78], fill=col)
            d.line([(x + w * px + 4, y + h * 0.61), (x + w * px + 4,
                    y + h * 0.44)], fill=INK, width=1)
            d.rectangle([x + w * (px - 0.02), y + h * 0.32, x + w * (px + 0.10),
                         y + h * 0.44], fill=(255, 255, 255), outline=INK)
        d.text((x + w * 0.30, y + h * 0.08), "COST OF LIVING",
               font=font(SANS_B, 9), fill=RED)
    elif kind == "ohio":
        d.rectangle([x, y, x + w, y + h], fill=(30, 34, 52))
        # police lights + tape
        for lx, col in ((0.18, (200, 40, 40)), (0.42, (40, 80, 220)),
                        (0.66, (200, 40, 40)), (0.86, (40, 80, 220))):
            d.ellipse([x + w * lx - 8, y + h * 0.22 - 8, x + w * lx + 8,
                       y + h * 0.22 + 8], fill=col)
            d.line([(x + w * lx, y + h * 0.22 + 8), (x + w * lx, y + h * 0.55)],
                   fill=col, width=2)
        # police tape
        d.rectangle([x, y + h * 0.58, x + w, y + h * 0.72], fill=(255, 220, 60))
        d.text((x + w * 0.05, y + h * 0.61), "POLICE LINE — DO NOT CROSS",
               font=font(SANS_B, 8), fill=INK)
        # house silhouette
        d.rectangle([x + w * 0.30, y + h * 0.78, x + w * 0.70, y + h * 0.95],
                    fill=(70, 70, 85))
        d.polygon([(x + w * 0.26, y + h * 0.80), (x + w * 0.50, y + h * 0.66),
                   (x + w * 0.74, y + h * 0.80)], fill=(55, 55, 70))


# ---------------------------------------------------------------- data
# (num, region, topic, headline, deck, label, scene, region_colour)
FEATURES = [
    (1, "GLOBAL", "CLIMATE", "COP31 collapses with no deal",
     "Longest COP ever ends in failure; the pact never says 'fossil fuels'.",
     "CONFIRMED · CNN", "cop31", GREY),
    (2, "GULF", "IRAN WAR", "Bahrain: two hurt as strikes go on",
     "IRGC claims Patriot-radar hits; CENTCOM calls the F-16 claim 'FALSE'.",
     "CLAIM · REUTERS", "bahrain", RED),
    (3, "EUROPE", "UKRAINE WAR", "Russian corvette sunk off Libya",
     "Merkury capsizes at Benghazi after a suspected sea-drone attack.",
     "CONFIRMED · WSJ", "merkury", NAVY),
    (4, "EUROPE", "UKRAINE WAR", "14 missing after drone hits Kyiv flats",
     "Drone partly collapses a five-storey block in Dymer; nine rescued.",
     "CONFIRMED · REUTERS", "dymer", NAVY),
    (5, "AMERICAS", "POLITICS", "Democrats clinch 258 House seats",
     "Biggest House majority since 1992, and the largest of the century.",
     "CONFIRMED · AP", "house258", TEAL),
    (6, "ASIA", "DISASTER", "Indonesia factory fire: 24 body bags",
     "Candy factory blaze in Cikande; dozens of workers still missing.",
     "CONFIRMED · REUTERS", "factory", GOLD),
    (7, "OCEANIA", "SPORT", "India 720/9, a record in New Zealand",
     "Highest Test total ever on Kiwi soil; 50+ stands for seven wickets.",
     "CONFIRMED · CRICINFO", "cricket", GREEN),
    (8, "US", "SPORT", "Verstappen wins a 35-lead-change Vegas GP",
     "Third Las Vegas win in four years; Norris 2nd, Piastri 3rd from 17th.",
     "CONFIRMED · AP", "f1", TEAL),
    (9, "ASIA", "TECH", "Korea minister quits over AI cheating",
     "Choi Kyo-jin resigns after the suneung exam-cheating scare.",
     "CONFIRMED · GUARDIAN", "exam", PURPLE),
    (10, "GLOBAL", "MARKETS", "Bitcoin bounces off a two-year low",
     "Jumps 8%+ to retake $60,000; S&P ends its worst week since April 2025.",
     "CONFIRMED · REUTERS", "bitcoin", GREY),
    (11, "MIDDLE EAST", "ISRAEL", "Eisenkot: settler attacks are 'terrorism'",
     "Opposition leader condemns West Bank violence; coalition talks fail.",
     "CONFIRMED · AL JAZEERA", "knesset", RED),
    (12, "US", "TRAVEL", "Delta meltdown on Thanksgiving weekend",
     "Automation fault delays well over half of Delta's flights on Sunday.",
     "CONFIRMED · AP", "delta", TEAL),
    (13, "ASIA", "DIPLOMACY", "Nepal PM talks with Modi in Delhi",
     "Balendra Shah's state visit reviews the full range of relations.",
     "CONFIRMED · OBSERVER VOICE", "nepal", PURPLE),
    (14, "EUROPE", "PROTEST", "Thousands march in Lisbon over prices",
     "Cost-of-living anger fills the streets of the Portuguese capital.",
     "REPORTED · JAGRAN", "march", NAVY),
    (15, "US", "CRIME", "Three killed at an Ohio baby shower",
     "Shooting kills three and wounds one; one man is in custody.",
     "CONFIRMED · AP", "ohio", TEAL),
]

# (hour_float, "HH:MM", short label) — Sun 00:00 -> Mon 00:00 UTC
TIMELINE = [
    (5.18, "05:11", "India declare 720/9"),
    (10.53, "10:32", "Bahrain: two injured"),
    (12.93, "12:56", "Dymer rescue under way"),
    (13.50, "13:30", "Bitcoin retakes $60k"),
    (18.00, "18:00", "Democrats reach 258"),
    (22.60, "22:36", "Merkury sunk"),
    (24.03, "00:02", "UN: lethal-AI talks go on"),
]

ALSO_ON = [
    "US: Army plans to detonate bomb-making chemicals in Iowa by Tuesday.",
    "US: ICE detains a father and daughter at Seattle airport; governor calls ICE 'out of control'.",
    "US: Congress member threatens to halt SpaceX resources over Starshield limits in Ukraine.",
    "US: Tom Jackson, ex-Broncos star and ESPN broadcaster, dies at 75.",
    "US: Miley Cyrus marries Maxx Morando in a California ceremony.",
    "US: Treasury chief Bessent calls on Nvidia to answer on chip sales to China.",
    "US: Nvidia falls 14% as the SEC examines its accounting; Anthropic down 8.9% on day two.",
    "US: Democrats' 100-day agenda: reverse Medicaid cuts, restore ACA tax credits.",
    "UK: Theresa May warns Andy Burnham to 'accept Brexit and move on'.",
    "EU: Council president unveils a reduced EU budget, keeps €100bn for Ukraine.",
    "UK: Briton swims the length of the Strait of Hormuz to highlight the war's cost.",
    "Portugal: Thousands march in Lisbon as living costs fuel anger.",
    "Finland: PM Orpo backs Ukraine's right to fight back after the Baltic ship strike.",
    "UK: NHS wasting billions of taxpayers' cash, data show.",
    "Russia: Kaliningrad governor says the Sparta II was hit by two drones.",
    "Iran: 14 tankers mass at Kharg to break the US blockade; power cuts begin Sunday.",
    "Gulf: UKMTO logs two more tanker strikes near Khasab, Oman, on Saturday.",
    "Saudi Arabia: Coalition intercepts a Houthi missile; Gulf states condemn the Bahrain attack.",
    "Libya: Eastern government seeks a UN investigation into the Benghazi warship attack.",
    "Libya: Malta-flagged vessel hit by a drone boat off Benghazi; 20+ drone boats intercepted.",
    "Israel: Netanyahu and Eisenkot parties fail to agree in a second round of coalition talks.",
    "Gulf: Two tankers hit by projectiles in the Strait of Hormuz, UKMTO reports.",
    "India: Amit Shah launches a ₹4,000 crore infrastructure push in Arunachal Pradesh.",
    "India: PM Modi inaugurates an AI centre at IIT Patna.",
    "India: BJP Rajya Sabha MP Ramrao Wadkute dies of cardiac arrest in Delhi.",
    "India: Tata Steel's ₹28,000 crore deal with APL Apollo.",
    "India: IFFI 2026 hosts a BRICS Roundtable on film partnerships.",
    "Myanmar: Army-backed government calls the ASEAN decision 'unfair and imbalanced'.",
    "Malaysia: To coordinate with the UN and OIC after the ICJ Myanmar atrocity ruling.",
    "Australia: Government reprimands the US Congressional Budget Office over AUKUS comments.",
    "Cricket: New Zealand 119/2 at stumps in Wellington; India lead by 233 into the final day.",
    "F1: Piastri charges from 17th on the grid to third in Las Vegas.",
    "Markets: Asian stocks crash — Nikkei down 5.1%, KOSPI down 5.2%, Hang Seng down 1.8%.",
    "Markets: S&P 500 falls 3.7% on Friday, its seventh straight loss; Nasdaq down 10% on the week.",
    "Snooker: Anupama defends the IBSF World Women's Snooker Championship.",
]

DATE_CHECK_LEFT = [
    "Shenzhen trilateral summit (19 Nov)",
    "Anthropic's record IPO debut (19 Nov)",
    "Denmark expels Russian attache (20 Nov)",
    "Zecler verdict: three police jailed (20 Nov)",
    "NSE world's 5th-largest exchange (20 Nov)",
]
DATE_CHECK_RIGHT = [
    "Bayer's $7.25bn Roundup deal (20 Nov)",
    "Pentagon UFO files, batch 8 (20 Nov)",
    "Cyclone Akvan's Odisha landfall (20 Nov)",
    "GTA VI's $3.79bn first-day sales (21 Nov)",
    "FAA nationwide ground stop (13 Nov)",
]
DATE_CHECK_NOT_YET = ("Not yet: Louisiana's two House runoffs, 12 Dec, "
                      "settle the final margin.")


def draw_card(d, x, y, w, h, feat, big):
    num, region, topic, headline, deck, label, kind, col = feat
    d.rectangle([x, y, x + w, y + h], fill=CARD_BG, outline=RULE, width=1)
    illu_h = 52 if big else 36
    scene(d, kind, x + 1, y + 1, w - 2, illu_h)
    d.line([(x, y + illu_h + 1), (x + w, y + illu_h + 1)], fill=RULE, width=1)
    tx = x + 8
    content_w = w - 16
    # number badge + kicker
    ky = y + illu_h + 6
    r = 8 if big else 7
    cx, cy = tx + r, ky + r
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    ns = str(num)
    nf = font(SANS_B, 10 if big else 9)
    d.text((cx - tw(d, ns, nf) / 2, cy - 7), ns, font=nf, fill=(255, 255, 255))
    kf = font(SANS_B, 10 if big else 8)
    d.text((tx + 2 * r + 4, ky + 2), f"{region} \u00b7 {topic}", font=kf, fill=col)
    hy = ky + 17 if big else ky + 15
    hf = font(SERIF_B, 14 if big else 11)
    hy = draw_wrapped(d, tx, hy, headline, hf, content_w, INK,
                      16 if big else 12.5, max_lines=2)
    df = font(SANS, 10 if big else 8)
    deck_y = hy + (2 if big else 1)
    draw_wrapped(d, tx, deck_y, deck, df, content_w, (60, 58, 52),
                 12 if big else 10.5, max_lines=2)
    lf = font(SANS_B, 9 if big else 8)
    lcol = RED if label.startswith("CLAIM") else TEAL
    d.text((tx, y + h - 13), f"\u25cf {label}", font=lf, fill=lcol)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead
    d.rectangle([16, 8, 1008, 11], fill=NAVY)
    spaced_centre(d, 512, 16, "THE DAY IN WORLD NEWS", font(SANS_B, 14), NAVY, 4)
    centre(d, 512, 30, "MONDAY 23 NOVEMBER 2026", font(SERIF_B, 50), INK)
    centre(d, 512, 80, "50 STORIES \u00b7 7 REGIONS \u00b7 UTC TIMELINE + DATE CHECK",
           font(SANS_B, 13), RED)
    d.rectangle([16, 94, 1008, 96], fill=INK)

    # ---- UTC timeline ruler (Sun 00:00 -> Mon 00:00 UTC, 24 hours)
    d.text((16, 100), "MONDAY'S NEWS CYCLE \u2014 SUN 00:00 \u2192 MON 00:00 UTC \u00b7 "
           "THE 24 HOURS BEHIND TODAY'S PAPERS", font=font(SANS_B, 9), fill=NAVY)
    ry = 140
    d.line([(16, ry), (1008, ry)], fill=INK, width=2)
    tf = font(SANS_B, 8)
    lf = font(SANS, 8)
    # end labels above the ruler (clear of the event labels)
    d.text((16, 110), "SUN 00:00", font=tf, fill=GREY)
    end_lab = "MON 00:00"
    d.text((1008 - tw(d, end_lab, tf), 110), end_lab, font=tf, fill=GREY)
    for hh in (0, 4, 8, 12, 16, 20, 24):
        tx = 16 + hh / 24.0 * 992
        d.line([(tx, ry - 4), (tx, ry + 4)], fill=INK, width=1)
    for i, (t, tstr, lab) in enumerate(TIMELINE):
        ex = min(16 + t / 24.0 * 992, 1004)
        d.ellipse([ex - 4, ry - 4, ex + 4, ry + 4], fill=RED,
                  outline=(255, 255, 255), width=1)
        above = (i % 2 == 0)
        # exactly two lines: bold time, then one truncated label line;
        # the last event sits at the right edge, so right-align its labels
        lines = [tstr, trunc(d, lab, lf, 120)]
        ly = 110 if above else 146
        for j, ln in enumerate(lines):
            f = tf if j == 0 else lf
            if ex > 948:
                d.text((1008 - tw(d, ln, f), ly + j * 10), ln, font=f,
                       fill=RED if j == 0 else INK)
            else:
                d.text((ex - tw(d, ln, f) / 2, ly + j * 10), ln, font=f,
                       fill=RED if j == 0 else INK)

    # ---- feature cards
    row1 = FEATURES[:3]
    row2 = FEATURES[3:9]
    row3 = FEATURES[9:15]
    for i, feat in enumerate(row1):
        draw_card(d, 16 + i * 333, 170, 325, 138, feat, big=True)
    for i, feat in enumerate(row2):
        draw_card(d, 16 + i * 166, 314, 160, 122, feat, big=False)
    for i, feat in enumerate(row3):
        draw_card(d, 16 + i * 166, 442, 160, 122, feat, big=False)

    # ---- map
    d.text((16, 570), "WHERE IT HAPPENED", font=font(SANS_B, 12), fill=NAVY)
    legend = [("GULF", RED), ("EUROPE", NAVY), ("AMERICAS", TEAL),
              ("AFRICA", GOLD), ("ASIA", PURPLE), ("OCEANIA", GREEN),
              ("GLOBAL", GREY)]
    lx = 1008
    lf2 = font(SANS_B, 8)
    for name, col in reversed(legend):
        wname = tw(d, name, lf2)
        lx -= wname + 14
        d.ellipse([lx, 573, lx + 8, 581], fill=col)
        d.text((lx + 10, 572), name, font=lf2, fill=GREY)
        lx -= 8
    draw_map(d)

    # ---- ALSO ON list
    centre(d, 512, 686, "ALSO ON MONDAY 23 NOVEMBER", font(SANS_B, 13), NAVY)
    d.line([(16, 702), (1008, 702)], fill=RULE, width=1)
    af = font(SANS, 10)
    col_w = 488
    for i, item in enumerate(ALSO_ON):
        num = 16 + i
        if i < 18:
            cx0, cy = 16, 708 + i * 12
        else:
            cx0, cy = 520, 708 + (i - 18) * 12
        text = f"{num}. {item}"
        text = trunc(d, text, af, col_w)
        d.text((cx0, cy), text, font=af, fill=INK)

    # ---- DATE CHECK box
    bx0, by0, bx1, by1 = 16, 926, 1008, 1000
    d.rectangle([bx0, by0, bx1, by1], fill=DATE_BG, outline=RED, width=1)
    d.text((bx0 + 8, by0 + 4), "DATE CHECK \u2014 LEFT OUT AS OLDER NEWS",
           font=font(SANS_B, 10), fill=RED)
    dcf = font(SANS, 9)
    for i, item in enumerate(DATE_CHECK_LEFT):
        d.text((bx0 + 8, by0 + 18 + i * 9), "\u00b7 " + item, font=dcf, fill=INK)
    for i, item in enumerate(DATE_CHECK_RIGHT):
        d.text((512, by0 + 18 + i * 9), "\u00b7 " + item, font=dcf, fill=INK)
    d.text((512, by0 + 18 + 5 * 9), DATE_CHECK_NOT_YET, font=font(SANS_B, 9), fill=RED)

    # ---- footer
    centre(d, 512, 1004,
           "Every story happened or was first reported on Monday 23 November 2026; "
           "disputed claims are attributed.", font(SANS, 9), GREY)
    centre(d, 512, 1014,
           "Sources: Reuters, AP, AFP, BBC, Al Jazeera, CNN, UN News, Le Monde, "
           "NDTV, Cricinfo, Formula1, The Guardian. Original drawings.",
           font(SANS, 9), GREY)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG")
    print(f"wrote {out} {os.path.getsize(out)} bytes")


if __name__ == "__main__":
    main()
