#!/usr/bin/env python3
"""Draw the Monday 23 November 2026 front page: 50 sourced stories, a UTC
timeline and a date check. Pure PIL, no network, no clock, deterministic:
same code, same bytes, every run."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (246, 241, 229)
INK = (25, 25, 25)
NAVY = (29, 58, 110)
RED = (169, 44, 44)
GOLD = (150, 110, 0)
TEAL = (15, 107, 92)
LIGHT = (233, 225, 206)
SKY = (214, 228, 240)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIFB = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def centre(d, x, y, s, f, fill=INK):
    d.text((x, y), s, font=f, fill=fill, anchor="ma")


def trunc(d, s, f, maxw):
    while s and d.textlength(s + "...", font=f) > maxw:
        s = s[:-1].rstrip()
    return s + ("..." if d.textlength(s, font=f) > maxw else "")


# ---------------------------------------------------------------- data
# (n, region, topic, headline, deck, label, label colour)
FEATURES = [
    (1, "GLOBAL", "CLIMATE",
     "COP31 collapses with no deal",
     "190+ nations reject the Antalya Pact: it never mentions fossil fuels. Longest COP ever ends in breakdown.",
     "CONFIRMED · CNN / UN NEWS", NAVY),
    (2, "GULF", "IRAN WAR",
     "Bahrain: two hurt as strikes go on",
     "Bahrain confirms two injured; IRGC claims radar strikes; CENTCOM calls the F-16 claim FALSE. 14 tankers mass at Kharg.",
     "CLAIM · REUTERS", RED),
    (3, "EUROPE", "UKRAINE WAR",
     "Russian corvette sunk off Libya",
     "The Merkury capsizes at Benghazi after a suspected Ukrainian sea-drone attack; the Ascalon is also hit. 10 injured.",
     "CONFIRMED · WSJ / TIMES", NAVY),
    (4, "EUROPE", "UKRAINE WAR",
     "14 missing after drone hits Kyiv flats",
     "A Russian drone partly collapses a five-storey block in Dymer; nine evacuated, rescue under way, fire contained.",
     "CONFIRMED · REUTERS", NAVY),
    (5, "AMERICAS", "POLITICS",
     "Democrats clinch 258 House seats",
     "AP calls NC-05 for Chuck Hubbard: the largest House majority since 1992, the biggest of the century.",
     "CONFIRMED · AP / REUTERS", NAVY),
    (6, "ASIA", "DISASTER",
     "Indonesia factory fire: 24 body bags",
     "Police pull 24 body bags from the PT Fonusa candy factory in Cikande, a day after the blaze; dozens still missing.",
     "CONFIRMED · REUTERS", NAVY),
    (7, "OCEANIA", "SPORT",
     "India 720/9, a record in New Zealand",
     "India declare at the Basin Reserve — the highest Test total ever in NZ. Rahul 136, Pant 128; 50+ for every wicket.",
     "CONFIRMED · CRICINFO / WISDEN", NAVY),
    (8, "US", "SPORT",
     "Verstappen wins a 35-lead-change Vegas GP",
     "Max holds off Russell, Antonelli and Norris in a 50-lap slipstream classic — his third Vegas win in four years.",
     "CONFIRMED · AP / FORMULA 1", NAVY),
    (9, "ASIA", "TECH",
     "S. Korea minister quits over AI cheating",
     "Education minister Choi Kyo-jin resigns after the suneung scare: a top scorer used a hidden camera and generative AI.",
     "CONFIRMED · THE GUARDIAN", NAVY),
    (10, "GLOBAL", "MARKETS",
     "Bitcoin bounces off a two-year low",
     "Bitcoin jumps 8%+ to retake $60,000 after touching $55,252; the S&P 500 ends its worst week since April 2025.",
     "CONFIRMED · REUTERS", NAVY),
    (11, "MIDDLE EAST", "ISRAEL",
     "Eisenkot: settler attacks are 'terrorism'",
     "Opposition leader Gadi Eisenkot condemns West Bank settler violence as 'an act of Jewish terrorism'; coalition talks fail.",
     "CONFIRMED · AL JAZEERA", NAVY),
    (12, "US", "TRAVEL",
     "Delta meltdown on Thanksgiving weekend",
     "A weight-and-balance automation fault delays well over half of Delta's Sunday flights; fixed by the afternoon.",
     "CONFIRMED · AP", NAVY),
    (13, "ASIA", "DIPLOMACY",
     "Nepal PM talks with Modi in Delhi",
     "Nepal's PM Balendra Shah holds bilateral talks with PM Modi on a 22–23 Nov state visit, reviewing all relations.",
     "CONFIRMED · OBSERVER VOICE", NAVY),
    (14, "EUROPE", "PROTEST",
     "Thousands march in Lisbon over living costs",
     "Cost-of-living anger fills the streets of the Portuguese capital as marchers demand relief.",
     "REPORTED · JAGRAN", RED),
    (15, "US", "CRIME",
     "Three killed at an Ohio baby shower",
     "A shooting at a baby shower in Ohio kills three and wounds one; one man is in custody.",
     "CONFIRMED · AP", NAVY),
]

# (hour, time label, short label)
TIMELINE = [
    (5.18, "05:11", "India declare 720/9"),
    (10.53, "10:32", "Bahrain: two hurt"),
    (12.93, "12:56", "Dymer rescue"),
    (13.50, "13:30", "Bitcoin $60,000"),
    (18.00, "18:00", "Democrats 258"),
    (22.60, "22:36", "Merkury sunk"),
    (24.03, "00:02", "AI-rules talks"),
]

# ("HEADER", text) or (n, text)
ALSO_ON = [
    ("HEADER", "AMERICAS"),
    (16, "US: Army to detonate bomb chemicals in Iowa by Tuesday"),
    (17, "US: ICE detains father and daughter at Seattle airport"),
    (18, "US: Congress member threatens to halt SpaceX resources"),
    (19, "US: Tom Jackson, ex-Broncos star and ESPN voice, dies at 75"),
    (20, "US: Miley Cyrus marries Maxx Morando in California"),
    (21, "US: Bessent calls on Nvidia over chip sales to China"),
    (22, "US: Nvidia falls 14% as SEC examines its accounting"),
    (23, "US: Democrats' 100-day agenda: reverse Medicaid cuts"),
    ("HEADER", "EUROPE"),
    (24, "UK: May warns Burnham to 'accept Brexit and move on'"),
    (25, "EU: Council unveils reduced budget, €100bn for Ukraine"),
    (26, "UK: Briton swims Strait of Hormuz for the war's cost"),
    (27, "Portugal: Thousands march in Lisbon on living costs"),
    (28, "Finland: PM Orpo backs Ukraine's right to fight back"),
    (29, "UK: NHS wasting billions, data show"),
    (30, "Russia: Sparta II hit by two drones, governor says"),
    ("HEADER", "MIDDLE EAST & AFRICA"),
    (31, "Iran: 14 tankers mass at Kharg; power cuts begin"),
    (32, "Gulf: Two more tanker strikes near Khasab, Oman"),
    (33, "Saudi: Coalition intercepts a Houthi missile"),
    (34, "Libya: East seeks UN probe into Benghazi attack"),
    (35, "Libya: Malta vessel hit by drone boat off Benghazi"),
    (36, "Israel: Netanyahu–Eisenkot talks fail, second round"),
    (37, "Gulf: Two tankers hit in the Strait of Hormuz"),
    ("HEADER", "ASIA & PACIFIC"),
    (38, "India: Shah launches ₹4,000 cr push in Arunachal"),
    (39, "India: Modi inaugurates AI centre at IIT Patna"),
    (40, "India: BJP MP Ramrao Wadkute dies of cardiac arrest"),
    (41, "India: Tata Steel's ₹28,000 cr deal with APL Apollo"),
    (42, "India: IFFI 2026 hosts BRICS film roundtable"),
    (43, "Myanmar: Army-backed govt calls ASEAN move 'unfair'"),
    (44, "Malaysia: To coordinate with UN and OIC on Myanmar"),
    (45, "Australia: Reprimands US CBO over AUKUS comments"),
    ("HEADER", "SPORT & MARKETS"),
    (46, "Cricket: NZ 119/2 at stumps; India lead by 233"),
    (47, "F1: Piastri charges from 17th to third in Vegas"),
    (48, "Markets: Nikkei -5.1%, KOSPI -5.2%, Hang Seng -1.8%"),
    (49, "Markets: S&P 500 -3.7%, seventh straight loss"),
    (50, "Snooker: Anupama defends world women's title"),
]

DATE_CHECK = [
    "Trump–Xi–Putin summit, Shenzhen (19 Nov)",
    "Anthropic's record IPO, briefly above $2tn (19 Nov)",
    "Denmark expels Russia's defence attache (20 Nov)",
    "Paris jails three police over Zecler beating (20 Nov)",
    "NSE becomes world's 5th-largest exchange (20 Nov)",
    "Bayer's $7.25bn Roundup settlement (20 Nov)",
    "Pentagon's PURSUE UFO files, batch 8 (20 Nov)",
    "Cyclone Akvan's Odisha landfall (20 Nov)",
    "GTA VI's $3.79bn first-day sales (21 Nov)",
    "FAA nationwide ground stop (13 Nov)",
]
NOT_YET = "Not yet: Louisiana's two House runoffs on 12 Dec settle the final margin."

# pin positions (x, y) on the map strip for features 1..15
PINS = {
    1: (585, 668), 2: (612, 688), 3: (560, 698), 4: (575, 658),
    5: (205, 680), 6: (838, 715), 7: (950, 720), 8: (148, 680),
    9: (822, 656), 10: (232, 654), 11: (592, 698), 12: (190, 698),
    13: (745, 678), 14: (482, 686), 15: (222, 666),
}


# ---------------------------------------------------------------- scenes
def scene(d, n, x, y, w, h):
    """Flat detailed scene for feature n inside box (x, y, w, h)."""
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    if n == 1:  # COP31 hall, flags, torn pact
        d.rectangle([x, y + h * 0.55, x + w, y + h], fill=(120, 140, 110))
        d.rectangle([x + w * 0.18, y + h * 0.25, x + w * 0.82, y + h * 0.62],
                    fill=(240, 235, 220), outline=NAVY, width=2)
        d.pieslice([x + w * 0.38, y + h * 0.02, x + w * 0.62, y + h * 0.34],
                   180, 360, fill=(240, 235, 220), outline=NAVY, width=2)
        for i, c in enumerate([(0, 90, 160), (200, 40, 40), (0, 120, 60),
                               (220, 180, 0)]):
            fx = x + w * (0.12 + i * 0.22)
            d.rectangle([fx, y + h * 0.42, fx + 3, y + h * 0.62], fill=INK)
            d.polygon([(fx + 3, y + h * 0.42), (fx + 16, y + h * 0.47),
                       (fx + 3, y + h * 0.52)], fill=c)
        d.polygon([(x + w * 0.55, y + h * 0.72), (x + w * 0.95, y + h * 0.72),
                   (x + w * 0.88, y + h * 0.95), (x + w * 0.62, y + h * 0.95)],
                  fill=(255, 255, 255), outline=RED, width=2)
        d.line([x + w * 0.68, y + h * 0.78, x + w * 0.82, y + h * 0.92],
               fill=RED, width=3)
        d.line([x + w * 0.82, y + h * 0.78, x + w * 0.68, y + h * 0.92],
               fill=RED, width=3)
    elif n == 2:  # Bahrain industrial site, radar, tankers
        d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(40, 90, 130))
        d.rectangle([x + w * 0.08, y + h * 0.40, x + w * 0.30, y + h * 0.62],
                    fill=(180, 180, 175), outline=INK)
        d.rectangle([x + w * 0.34, y + h * 0.30, x + w * 0.38, y + h * 0.62],
                    fill=(150, 60, 50))
        d.ellipse([x + w * 0.55, y + h * 0.18, x + w * 0.80, y + h * 0.45],
                  outline=INK, width=2)
        d.line([x + w * 0.67, y + h * 0.45, x + w * 0.67, y + h * 0.62],
               fill=INK, width=2)
        for i in range(3):
            tx = x + w * (0.15 + i * 0.30)
            d.polygon([(tx, y + h * 0.78), (tx + w * 0.22, y + h * 0.78),
                       (tx + w * 0.18, y + h * 0.90), (tx + w * 0.04, y + h * 0.90)],
                      fill=(60, 60, 60))
    elif n == 3:  # corvette sinking, drone
        d.rectangle([x, y + h * 0.55, x + w, y + h], fill=(30, 80, 140))
        d.polygon([(x + w * 0.12, y + h * 0.62), (x + w * 0.82, y + h * 0.38),
                   (x + w * 0.78, y + h * 0.56), (x + w * 0.18, y + h * 0.72)],
                  fill=(90, 95, 100), outline=INK)
        d.rectangle([x + w * 0.55, y + h * 0.28, x + w * 0.62, y + h * 0.44],
                    fill=(90, 95, 100), outline=INK)
        d.ellipse([x + w * 0.60, y + h * 0.08, x + w * 0.86, y + h * 0.28],
                  fill=(200, 200, 200, 120))
        d.ellipse([x + w * 0.66, y + h * 0.02, x + w * 0.80, y + h * 0.14],
                  fill=(180, 180, 180))
        for wx in (0.10, 0.45, 0.80):
            d.arc([x + w * wx, y + h * 0.58, x + w * (wx + 0.14),
                   y + h * 0.72], 0, 180, fill=(255, 255, 255), width=2)
        d.ellipse([x + w * 0.12, y + h * 0.12, x + w * 0.22, y + h * 0.20],
                  fill=INK)
        d.line([x + w * 0.10, y + h * 0.16, x + w * 0.24, y + h * 0.16],
               fill=INK, width=2)
        d.line([x + w * 0.17, y + h * 0.20, x + w * 0.17, y + h * 0.26],
               fill=INK, width=2)
    elif n == 4:  # Kyiv flats, collapsed corner, ladder
        d.rectangle([x, y + h * 0.75, x + w, y + h], fill=(90, 90, 85))
        d.rectangle([x + w * 0.15, y + h * 0.20, x + w * 0.85, y + h * 0.78],
                    fill=(200, 170, 130), outline=INK, width=2)
        for r in range(4):
            for c in range(4):
                wx = x + w * (0.22 + c * 0.16)
                wy = y + h * (0.26 + r * 0.13)
                d.rectangle([wx, wy, wx + w * 0.08, wy + h * 0.07],
                            fill=(60, 60, 90) if (r + c) % 2 else (250, 220, 120))
        d.polygon([(x + w * 0.60, y + h * 0.20), (x + w * 0.85, y + h * 0.20),
                   (x + w * 0.85, y + h * 0.45), (x + w * 0.72, y + h * 0.45)],
                  fill=(70, 70, 70))
        d.ellipse([x + w * 0.68, y + h * 0.05, x + w * 0.92, y + h * 0.22],
                  fill=(180, 180, 180))
        d.line([x + w * 0.30, y + h * 0.78, x + w * 0.45, y + h * 0.35],
               fill=(200, 40, 40), width=3)
    elif n == 5:  # Capitol dome + 258
        d.rectangle([x, y, x + w, y + h], fill=NAVY)
        d.pieslice([x + w * 0.30, y + h * 0.08, x + w * 0.70, y + h * 0.55],
                   180, 360, fill=(245, 240, 225))
        d.rectangle([x + w * 0.22, y + h * 0.52, x + w * 0.78, y + h * 0.78],
                    fill=(245, 240, 225))
        for i in range(5):
            d.rectangle([x + w * (0.26 + i * 0.11), y + h * 0.58,
                         x + w * (0.32 + i * 0.11), y + h * 0.76],
                        fill=NAVY)
        d.text((x + w * 0.5, y + h * 0.80), "258", font=F(SERIFB, int(h * 0.22)),
               fill=(255, 210, 80), anchor="ma")
    elif n == 6:  # factory fire
        d.rectangle([x, y, x + w, y + h * 0.55], fill=(220, 90, 40))
        d.rectangle([x + w * 0.10, y + h * 0.45, x + w * 0.75, y + h * 0.85],
                    fill=(80, 80, 80), outline=INK, width=2)
        d.rectangle([x + w * 0.78, y + h * 0.25, x + w * 0.86, y + h * 0.85],
                    fill=(80, 80, 80))
        for i, (fx, fy, s) in enumerate([(0.25, 0.42, 0.16), (0.45, 0.36, 0.20),
                                         (0.65, 0.44, 0.14)]):
            d.polygon([(x + w * fx, y + h * fy),
                       (x + w * (fx + s / 2), y + h * (fy - 0.28)),
                       (x + w * (fx + s), y + h * fy)],
                      fill=(255, 200, 40) if i % 2 else (255, 120, 20))
        d.ellipse([x + w * 0.55, y + h * 0.05, x + w * 0.90, y + h * 0.30],
                  fill=(120, 120, 120))
    elif n == 7:  # cricket pitch, stumps, scoreboard
        d.rectangle([x, y, x + w, y + h], fill=(40, 130, 70))
        d.rectangle([x + w * 0.35, y + h * 0.15, x + w * 0.65, y + h * 0.85],
                    fill=(210, 185, 130))
        for i in range(3):
            sx = x + w * (0.44 + i * 0.06)
            d.line([sx, y + h * 0.22, sx, y + h * 0.42], fill=(255, 220, 60),
                   width=3)
        d.line([x + w * 0.44, y + h * 0.22, x + w * 0.56, y + h * 0.22],
               fill=(255, 220, 60), width=3)
        d.rectangle([x + w * 0.05, y + h * 0.72, x + w * 0.95, y + h * 0.94],
                    fill=(25, 25, 25))
        d.text((x + w * 0.5, y + h * 0.74), "720/9",
               font=F(SANSB, int(h * 0.13)), fill=(255, 255, 255), anchor="ma")
        d.ellipse([x + w * 0.78, y + h * 0.15, x + w * 0.95, y + h * 0.32],
                  fill=(255, 255, 255), outline=INK, width=2)
    elif n == 8:  # night Vegas GP, car, flag
        d.rectangle([x, y, x + w, y + h], fill=(15, 20, 50))
        for i in range(6):
            d.ellipse([x + w * (0.08 + i * 0.15), y + h * (0.10 + (i % 2) * 0.10),
                       x + w * (0.12 + i * 0.15), y + h * (0.14 + (i % 2) * 0.10)],
                      fill=(255, 220, 100))
        d.polygon([(x, y + h * 0.75), (x + w, y + h * 0.55),
                   (x + w, y + h * 0.85), (x, y + h * 0.95)],
                  fill=(50, 50, 55))
        d.polygon([(x + w * 0.15, y + h * 0.62), (x + w * 0.55, y + h * 0.52),
                   (x + w * 0.58, y + h * 0.62), (x + w * 0.18, y + h * 0.72)],
                  fill=(200, 30, 30), outline=INK)
        d.ellipse([x + w * 0.22, y + h * 0.66, x + w * 0.30, y + h * 0.74],
                  fill=INK)
        d.ellipse([x + w * 0.46, y + h * 0.60, x + w * 0.54, y + h * 0.68],
                  fill=INK)
        for r in range(2):
            for c in range(3):
                d.rectangle([x + w * (0.78 + c * 0.06), y + h * (0.15 + r * 0.06),
                             x + w * (0.84 + c * 0.06), y + h * (0.21 + r * 0.06)],
                            fill=(255, 255, 255) if (r + c) % 2 == 0 else INK)
    elif n == 9:  # exam desk, hidden camera, AI bubble
        d.rectangle([x, y + h * 0.60, x + w, y + h], fill=(140, 100, 60))
        d.rectangle([x + w * 0.15, y + h * 0.55, x + w * 0.85, y + h * 0.68],
                    fill=(200, 160, 110), outline=INK, width=2)
        d.rectangle([x + w * 0.25, y + h * 0.30, x + w * 0.75, y + h * 0.55],
                    fill=(255, 255, 255), outline=INK, width=2)
        for i in range(3):
            d.line([x + w * 0.30, y + h * (0.36 + i * 0.06),
                    x + w * 0.70, y + h * (0.36 + i * 0.06)],
                   fill=(120, 120, 120), width=2)
        d.ellipse([x + w * 0.68, y + h * 0.10, x + w * 0.88, y + h * 0.28],
                  fill=INK)
        d.ellipse([x + w * 0.74, y + h * 0.16, x + w * 0.82, y + h * 0.24],
                  fill=(80, 160, 255))
        d.ellipse([x + w * 0.05, y + h * 0.08, x + w * 0.35, y + h * 0.30],
                  fill=(255, 240, 150), outline=INK, width=2)
        d.text((x + w * 0.20, y + h * 0.13), "AI?",
               font=F(SANSB, int(h * 0.14)), fill=INK, anchor="ma")
    elif n == 10:  # bitcoin coin + rising chart
        d.rectangle([x, y, x + w, y + h], fill=(25, 25, 35))
        d.ellipse([x + w * 0.28, y + h * 0.12, x + w * 0.72, y + h * 0.58],
                  fill=(240, 180, 40), outline=(255, 220, 100), width=3)
        d.text((x + w * 0.5, y + h * 0.16), "₿",
               font=F(SANSB, int(h * 0.34)), fill=(25, 25, 35), anchor="ma")
        pts = [(x + w * 0.08, y + h * 0.88), (x + w * 0.28, y + h * 0.80),
               (x + w * 0.45, y + h * 0.86), (x + w * 0.62, y + h * 0.68),
               (x + w * 0.80, y + h * 0.72), (x + w * 0.94, y + h * 0.55)]
        d.line(pts, fill=(60, 200, 90), width=3)
        d.polygon([(x + w * 0.94, y + h * 0.55), (x + w * 0.88, y + h * 0.58),
                   (x + w * 0.94, y + h * 0.64)], fill=(60, 200, 90))
    elif n == 11:  # podium, flags, speech bubble
        d.rectangle([x + w * 0.10, y + h * 0.62, x + w * 0.90, y + h * 0.85],
                    fill=(120, 90, 60), outline=INK, width=2)
        d.rectangle([x + w * 0.40, y + h * 0.30, x + w * 0.60, y + h * 0.62],
                    fill=(40, 60, 110))
        d.ellipse([x + w * 0.43, y + h * 0.18, x + w * 0.57, y + h * 0.32],
                  fill=(230, 200, 170))
        for i, fx in enumerate([0.12, 0.78]):
            d.rectangle([x + w * fx, y + h * 0.25, x + w * (fx + 0.02),
                         y + h * 0.62], fill=INK)
            d.polygon([(x + w * (fx + 0.02), y + h * 0.25),
                       (x + w * (fx + 0.16), y + h * 0.30),
                       (x + w * (fx + 0.02), y + h * 0.35)],
                      fill=(255, 255, 255), outline=NAVY)
            d.line([x + w * (fx + 0.02), y + h * 0.30,
                    x + w * (fx + 0.16), y + h * 0.30], fill=NAVY, width=2)
        d.text((x + w * 0.5, y + h * 0.86), "“terrorism”",
               font=F(SERIFB, int(h * 0.11)), fill=INK, anchor="ma")
    elif n == 12:  # Delta plane, runway, clock
        d.polygon([(x + w * 0.08, y + h * 0.40), (x + w * 0.85, y + h * 0.32),
                   (x + w * 0.92, y + h * 0.38), (x + w * 0.30, y + h * 0.52),
                   (x + w * 0.15, y + h * 0.52)], fill=(250, 250, 250),
                  outline=NAVY, width=2)
        d.polygon([(x + w * 0.45, y + h * 0.30), (x + w * 0.55, y + h * 0.18),
                   (x + w * 0.60, y + h * 0.32)], fill=(250, 250, 250),
                  outline=NAVY, width=2)
        d.polygon([(x + w * 0.30, y + h * 0.52), (x + w * 0.38, y + h * 0.62),
                   (x + w * 0.48, y + h * 0.52)], fill=(200, 30, 50))
        d.rectangle([x, y + h * 0.78, x + w, y + h * 0.86], fill=(60, 60, 60))
        for i in range(5):
            d.rectangle([x + w * (0.05 + i * 0.19), y + h * 0.81,
                         x + w * (0.13 + i * 0.19), y + h * 0.83],
                        fill=(255, 220, 60))
        d.ellipse([x + w * 0.78, y + h * 0.08, x + w * 0.95, y + h * 0.26],
                  fill=(255, 255, 255), outline=INK, width=2)
        d.line([x + w * 0.865, y + h * 0.17, x + w * 0.865, y + h * 0.11],
               fill=INK, width=2)
        d.line([x + w * 0.865, y + h * 0.17, x + w * 0.91, y + h * 0.17],
               fill=INK, width=2)
    elif n == 13:  # Nepal + India flags, table
        d.rectangle([x + w * 0.08, y + h * 0.15, x + w * 0.42, y + h * 0.55],
                    fill=(220, 40, 60), outline=INK, width=2)
        d.polygon([(x + w * 0.08, y + h * 0.15), (x + w * 0.42, y + h * 0.15),
                   (x + w * 0.25, y + h * 0.35)], fill=(255, 255, 255))
        d.rectangle([x + w * 0.58, y + h * 0.15, x + w * 0.92, y + h * 0.55],
                    fill=(255, 255, 255), outline=INK, width=2)
        d.rectangle([x + w * 0.58, y + h * 0.15, x + w * 0.92, y + h * 0.28],
                    fill=(255, 150, 40))
        d.rectangle([x + w * 0.58, y + h * 0.42, x + w * 0.92, y + h * 0.55],
                    fill=(20, 140, 60))
        d.ellipse([x + w * 0.71, y + h * 0.30, x + w * 0.79, y + h * 0.40],
                  outline=NAVY, width=2)
        d.rectangle([x + w * 0.15, y + h * 0.68, x + w * 0.85, y + h * 0.85],
                    fill=(140, 100, 60), outline=INK, width=2)
    elif n == 14:  # Lisbon street, crowd, banners
        d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(110, 110, 105))
        d.rectangle([x + w * 0.05, y + h * 0.15, x + w * 0.35, y + h * 0.62],
                    fill=(240, 200, 120), outline=INK, width=2)
        d.rectangle([x + w * 0.65, y + h * 0.10, x + w * 0.95, y + h * 0.62],
                    fill=(200, 120, 90), outline=INK, width=2)
        for i in range(7):
            cx = x + w * (0.10 + i * 0.13)
            d.ellipse([cx, y + h * 0.55, cx + w * 0.07, y + h * 0.64],
                      fill=(230, 200, 170) if i % 2 else (180, 140, 110))
            d.rectangle([cx - w * 0.01, y + h * 0.64, cx + w * 0.08,
                         y + h * 0.85], fill=(40, 90, 160) if i % 3 else RED)
        d.rectangle([x + w * 0.30, y + h * 0.30, x + w * 0.72, y + h * 0.48],
                    fill=(255, 255, 255), outline=INK, width=2)
        d.text((x + w * 0.51, y + h * 0.33), "CUSTO DE VIDA",
               font=F(SANSB, int(h * 0.10)), fill=RED, anchor="ma")
    else:  # 15 Ohio house, police tape
        d.rectangle([x + w * 0.18, y + h * 0.35, x + w * 0.82, y + h * 0.80],
                    fill=(200, 170, 130), outline=INK, width=2)
        d.polygon([(x + w * 0.12, y + h * 0.35), (x + w * 0.50, y + h * 0.12),
                   (x + w * 0.88, y + h * 0.35)], fill=(150, 50, 50))
        d.rectangle([x + w * 0.44, y + h * 0.55, x + w * 0.56, y + h * 0.80],
                    fill=(90, 60, 40))
        d.rectangle([x + w * 0.24, y + h * 0.45, x + w * 0.34, y + h * 0.55],
                    fill=(180, 220, 240), outline=INK)
        d.rectangle([x + w * 0.66, y + h * 0.45, x + w * 0.76, y + h * 0.55],
                    fill=(180, 220, 240), outline=INK)
        for i in range(6):
            d.polygon([(x + w * (i * 0.17), y + h * 0.86),
                       (x + w * (i * 0.17 + 0.08), y + h * 0.86),
                       (x + w * (i * 0.17 + 0.17), y + h * 0.96),
                       (x + w * (i * 0.17 + 0.09), y + h * 0.96)],
                      fill=(255, 220, 0) if i % 2 == 0 else INK)


# ---------------------------------------------------------------- layout
def draw_page():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 14

    # ---- masthead
    d.line([M, 10, W - M, 10], fill=INK, width=3)
    centre(d, W // 2, 16, "T H E   D A Y   I N   W O R L D   N E W S",
           F(SANSB, 15), NAVY)
    centre(d, W // 2, 34, "MONDAY 23 NOVEMBER 2026", F(SERIFB, 46))
    centre(d, W // 2, 84, "50 STORIES  ·  7 REGIONS  ·  EVERY ONE FROM THIS DAY",
           F(SANSB, 13), RED)
    d.line([M, 100, W - M, 100], fill=INK, width=2)

    # ---- UTC timeline
    y0 = 102
    d.text((M, y0), "THE 24 HOURS BEHIND MONDAY'S PAPERS — UTC",
           font=F(SANSB, 11), fill=NAVY)
    d.text((W - M, y0), "SUN 00:00 → MON 00:00", font=F(SANS, 10),
           fill=INK, anchor="ra")
    rx0, rx1, ry = 40, 984, 140
    d.line([rx0, ry, rx1, ry], fill=INK, width=2)
    for hh in range(0, 25, 2):
        tx = rx0 + hh / 24.0 * (rx1 - rx0)
        d.line([tx, ry - 4, tx, ry + 4], fill=INK, width=1)
    d.text((rx0, ry - 12), "00:00", font=F(SANS, 8), fill=(90, 90, 90))
    for i, (hour, tlabel, slabel) in enumerate(TIMELINE):
        ex = rx0 + hour / 24.0 * (rx1 - rx0)
        lx = min(max(ex, 70), 954)  # keep labels inside the page
        d.ellipse([ex - 5, ry - 5, ex + 5, ry + 5], fill=RED, outline=INK,
                  width=1)
        if i % 2 == 0:
            centre(d, lx, ry - 24, slabel, F(SANS, 8))
            centre(d, lx, ry - 13, tlabel, F(SANSB, 9), RED)
        else:
            centre(d, lx, ry + 10, tlabel, F(SANSB, 9), RED)
            centre(d, lx, ry + 21, slabel, F(SANS, 8))
    d.line([M, 172, W - M, 172], fill=INK, width=1)

    # ---- feature cards: 3 heroes, then 12 small (3 cols x 4 rows)
    heroes = FEATURES[:3]
    cw, gap = 326, 6
    for i, (n, region, topic, head, deck, label, lcol) in enumerate(heroes):
        x = M + i * (cw + gap)
        y = 178
        ch = 138
        d.rectangle([x, y, x + cw, y + ch], outline=INK, width=1,
                    fill=(255, 255, 255))
        scene(d, n, x + 1, y + 1, cw - 2, 58)
        ty = y + 62
        d.text((x + 8, ty), "%d  %s · %s" % (n, region, topic),
               font=F(SANSB, 9), fill=NAVY)
        hl = wrap(d, head, F(SERIFB, 14), cw - 16)
        hy = ty + 13
        for line in hl[:2]:
            d.text((x + 8, hy), line, font=F(SERIFB, 14), fill=INK)
            hy += 16
        dl = wrap(d, deck, F(SANS, 10), cw - 16)
        for line in dl[:2]:
            d.text((x + 8, hy), line, font=F(SANS, 10), fill=(60, 60, 60))
            hy += 12
        d.text((x + 8, y + ch - 13), label, font=F(SANSB, 9), fill=lcol)

    small = FEATURES[3:]
    scw, sch = 326, 74
    for i, (n, region, topic, head, deck, label, lcol) in enumerate(small):
        col, row = i % 3, i // 3
        x = M + col * (scw + gap)
        y = 322 + row * (sch + 4)
        d.rectangle([x, y, x + scw, y + sch], outline=INK, width=1,
                    fill=(255, 255, 255))
        scene(d, n, x + 1, y + 1, 62, sch - 2)
        tx = x + 70
        d.text((tx, y + 4), "%d  %s · %s" % (n, region, topic),
               font=F(SANSB, 8), fill=NAVY)
        hl = wrap(d, head, F(SERIFB, 12), scw - 78)
        hy = y + 16
        for line in hl[:2]:
            d.text((tx, hy), line, font=F(SERIFB, 12), fill=INK)
            hy += 14
        dl = wrap(d, deck, F(SANS, 9), scw - 78)
        for line in dl[:1]:
            d.text((tx, hy), line, font=F(SANS, 9), fill=(60, 60, 60))
            hy += 11
        d.text((tx, hy + 1), label, font=F(SANSB, 8), fill=lcol)

    # ---- world map with pins
    my = 636
    d.text((M, my), "WHERE IT HAPPENED — 15 PINS, ONE FOR EACH FEATURE",
           font=F(SANSB, 11), fill=NAVY)
    d.text((W - M, my), "1 COP31 · 2 Bahrain · 3 Merkury · 4 Kyiv · 5 House 258",
           font=F(SANS, 9), fill=(90, 90, 90), anchor="ra")
    map_y0, map_y1 = my + 16, my + 102
    d.rectangle([M, map_y0, W - M, map_y1], fill=(226, 236, 242),
                outline=INK, width=1)
    continents = [
        [(40, 668), (230, 656), (262, 688), (222, 722), (120, 724), (58, 706)],
        [(262, 724), (300, 724), (290, 736), (266, 734)],
        [(480, 660), (560, 654), (572, 684), (522, 694), (480, 686)],
        [(520, 696), (582, 696), (576, 736), (540, 737)],
        [(600, 654), (900, 650), (932, 700), (852, 732), (700, 728),
         (610, 702)],
        [(880, 726), (962, 722), (952, 737), (890, 735)],
    ]
    for poly in continents:
        d.polygon(poly, fill=(214, 196, 150), outline=(120, 100, 70))
    for n, (px, py) in sorted(PINS.items()):
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED, outline=(255, 255, 255),
                  width=2)
        centre(d, px, py - 6, str(n), F(SANSB, 9), (255, 255, 255))
    d.text((M, map_y1 + 4),
           "6 Indonesia fire · 7 India 720/9 · 8 Vegas GP · 9 Seoul · 10 Bitcoin · "
           "11 West Bank · 12 Delta · 13 Delhi · 14 Lisbon · 15 Ohio",
           font=F(SANS, 9), fill=(90, 90, 90))

    # ---- ALSO ON (35 items, 3 columns)
    ay = 758
    d.text((M, ay), "ALSO ON MONDAY 23 NOVEMBER — 35 MORE STORIES",
           font=F(SANSB, 11), fill=NAVY)
    d.line([M, ay + 15, W - M, ay + 15], fill=INK, width=1)
    col_w = 326
    rows_per_col = 14
    for idx, item in enumerate(ALSO_ON):
        col, row = idx // rows_per_col, idx % rows_per_col
        x = M + col * (col_w + 6)
        y = ay + 19 + row * 10.5
        if item[0] == "HEADER":
            d.text((x, y - 1), item[1], font=F(SANSB, 9), fill=RED)
        else:
            n, s = item
            line = "%d. %s" % (n, s)
            d.text((x, y), trunc(d, line, F(SANS, 9), col_w),
                   font=F(SANS, 9), fill=INK)

    # ---- DATE CHECK box
    dy = 926
    d.rectangle([M, dy, W - M, 998], outline=GOLD, width=2,
                fill=(252, 246, 224))
    d.text((M + 8, dy + 4), "DATE CHECK — LEFT OUT AS OLDER NEWS",
           font=F(SANSB, 11), fill=GOLD)
    d.text((W - M - 8, dy + 4), "each of these happened BEFORE Monday",
           font=F(SANS, 9), fill=(90, 90, 90), anchor="ra")
    for i, item in enumerate(DATE_CHECK):
        col, row = i // 5, i % 5
        x = M + 8 + col * 495
        y = dy + 20 + row * 8.5
        d.text((x, y), "✕ " + trunc(d, item, F(SANS, 8), 480),
               font=F(SANS, 8), fill=(80, 60, 20))
    d.text((M + 8, dy + 20 + 5 * 8.5), NOT_YET, font=F(SANSB, 8), fill=NAVY)

    # ---- footer
    d.line([M, 1002, W - M, 1002], fill=INK, width=1)
    centre(d, W // 2, 1006,
           "Every story happened or was first reported on Sun 22 / Mon 23 Nov 2026; "
           "disputed claims are attributed. Sources: AP, Reuters, AFP, BBC, Al Jazeera, "
           "UN News, CNN, WSJ, The Guardian, Cricinfo, Formula 1. Original drawings.",
           F(SANS, 8), (70, 70, 70))
    return img


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "/output/entry.png"
    draw_page().save(out, "PNG")
    print("wrote", out)
