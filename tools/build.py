"""Builds every animated SVG in assets/. Run: python tools/build.py

All motion is CSS keyframes inside the SVG, which GitHub renders through <img>.
Anything animated sits in its own <g> so CSS transforms never fight a transform attribute.
"""
import math
import os
import random
from html import escape

OUT = os.path.join(os.path.dirname(__file__), "..", "assets")

BG, INK, LINE, AMBER, DIM, SUB = "#0d0b09", "#ede6da", "#2a2520", "#ffc400", "#6b6155", "#a89f92"
SCL, RIM, PANEL = "#e6ddcf", "#3a332b", "#14110e"
SERIF = "Georgia,'Times New Roman',serif"
MONO = "Consolas,'SFMono-Regular',Menlo,monospace"

WORLDS = {
    "mint": ("I", "The Mint", "smart contracts", "#E9E1C8", "#1E3A2F"),
    "vault": ("II", "The Vault", "security", "#D6E2EE", "#1B2530"),
    "chain": ("III", "The Chain", "indexing & bridges", "#CFE3F5", "#0F2A44"),
    "desk": ("IV", "The Desk", "trading & bots", "#7CFF9B", "#0B2A12"),
    "arcade": ("V", "The Arcade", "3d & games", "#FFE14D", "#FF3D8B"),
    "room": ("VI", "The Room", "community", "#F1E4D8", "#3A2622"),
}


def almond(w, h):
    return f"M{-w/2:.1f} 0 Q0 {-h:.1f} {w/2:.1f} 0 Q0 {h:.1f} {-w/2:.1f} 0Z"


def kf(name, steps):
    body = "".join(f"{p:.2f}%{{{css}}}" for p, css in steps)
    return f"@keyframes {name}{{{body}}}"


def iris_grads():
    return "".join(
        f'<radialGradient id="ir-{k}" cx=".42" cy=".38" r=".7"><stop offset="0" stop-color="{c}"/>'
        f'<stop offset=".55" stop-color="{c}" stop-opacity=".85"/><stop offset="1" stop-color="{r}"/></radialGradient>'
        for k, (_, _, _, c, r) in WORLDS.items()
    )


class Svg:
    def __init__(self, w, h, defs="", grain=True):
        self.w, self.h, self.css, self.body, self.grain = w, h, [], [], grain
        self.defs = defs

    def add(self, s):
        self.body.append(s)

    def style(self, s):
        self.css.append(s)

    def render(self):
        w, h = self.w, self.h
        grain = ""
        if self.grain:
            grain = (f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="18" fill="#fff" filter="url(#grain)" '
                     f'clip-path="url(#frame)" opacity=".5"/>')
        return "\n".join([
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
            '<defs>',
            '<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" '
            'baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 1  0 0 0 0 .95  '
            '0 0 0 0 .85  .09 0 0 0 0"/></filter>',
            f'<clipPath id="frame"><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="18"/></clipPath>',
            f'<radialGradient id="vig" cx=".5" cy=".45" r=".75"><stop offset="0" stop-color="{AMBER}" stop-opacity=".07"/>'
            f'<stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></radialGradient>',
            self.defs,
            '</defs>',
            '<style>.a{transform-box:fill-box;transform-origin:center}'
            '.l{transform-box:fill-box;transform-origin:left center}' + "".join(self.css) + '</style>',
            f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="18" fill="{BG}"/>',
            f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="18" fill="url(#vig)"/>',
            *self.body,
            grain,
            f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="18" fill="none" stroke="{LINE}" stroke-width="2"/>',
            '</svg>',
        ])


def eye(world, w, cls="", style="", pupil_cls="", pupil_style="", stroke=2.0, look_cls="", look_style=""):
    """An eye centred on (0,0). `cls` animates the lid (scaleY)."""
    h = w * 0.68
    r = w * 0.19
    return (f'<g class="a {cls}" style="{style}"><path d="{almond(w, h)}" fill="{SCL}"/>'
            f'<g clip-path="url(#alm{int(w)})"><g class="{look_cls}" style="{look_style}">'
            f'<circle r="{r:.1f}" fill="url(#ir-{world})"/>'
            f'<g class="a {pupil_cls}" style="{pupil_style}"><circle r="{r*0.42:.1f}" fill="{BG}"/></g>'
            f'<circle cx="{-r*0.3:.1f}" cy="{-r*0.35:.1f}" r="{r*0.16:.1f}" fill="#fff" opacity=".85"/></g></g>'
            f'<path d="{almond(w, h)}" fill="none" stroke="{RIM}" stroke-width="{stroke}"/></g>')


def alm_clip(w):
    return f'<clipPath id="alm{int(w)}"><path d="{almond(w, w*0.68)}"/></clipPath>'


def corners(s, w, h, color=LINE, inset=18, arm=22):
    for x, y, dx, dy in [(inset, inset, 1, 1), (w - inset, inset, -1, 1), (inset, h - inset, 1, -1), (w - inset, h - inset, -1, -1)]:
        s.add(f'<path d="M{x} {y + dy*arm} V{y} H{x + dx*arm}" stroke="{color}" stroke-width="1.5" fill="none"/>')


# --------------------------------------------------------------------------- header
def header():
    W, H, L = 1000, 460, 12
    rnd = random.Random(21)
    s = Svg(W, H, defs=iris_grads() + alm_clip(300) + "".join(alm_clip(x) for x in range(12, 31)))
    corners(s, W, H, "#3a332b")

    # the hundred: placed around the watchman, never on the title or the HUD
    eyes = []
    while len(eyes) < 100:
        x, y = rnd.uniform(40, 960), rnd.uniform(40, 420)
        if ((x - 500) / 330) ** 2 + ((y - 235) / 205) ** 2 < 1:
            continue
        if (y < 92 or y > 392) and (x < 290 or x > 710):
            continue
        w = rnd.uniform(14, 30)
        if any((x - ex) ** 2 + (y - ey) ** 2 < (max(w, ew) + 10) ** 2 for ex, ey, ew, *_ in eyes):
            continue
        wake = rnd.uniform(12.5, 38)
        blink = rnd.uniform(wake + 10, 80)
        shut = rnd.uniform(83, 89)
        eyes.append((x, y, w, rnd.choice(list(WORLDS)), wake, blink, shut, rnd.uniform(.35, .8)))

    for i, (x, y, w, world, wake, blink, shut, op) in enumerate(eyes):
        s.style(kf(f"e{i}", [(0, "transform:scaleY(.05)"), (wake, "transform:scaleY(.05)"), (wake + 2.5, "transform:scaleY(1)"),
                             (blink, "transform:scaleY(1)"), (blink + .7, "transform:scaleY(.08)"), (blink + 1.4, "transform:scaleY(1)"),
                             (shut, "transform:scaleY(1)"), (shut + 2.5, "transform:scaleY(.05)"), (100, "transform:scaleY(.05)")]))
        dx = rnd.choice([-1, 1]) * w * 0.12
        s.style(kf(f"k{i}", [(0, "transform:translate(0,0)"), (46, "transform:translate(0,0)"), (49, f"transform:translate({dx:.1f}px,0)"),
                             (66, f"transform:translate({dx:.1f}px,0)"), (69, "transform:translate(0,0)"), (100, "transform:translate(0,0)")]))
        wi = int(round(w))
        s.add(f'<g transform="translate({x:.1f},{y:.1f})" opacity="{op:.2f}">'
              + eye(world, wi, style=f"animation:e{i} {L}s infinite linear", stroke=1.2,
                    look_style=f"animation:k{i} {L}s infinite ease-in-out") + '</g>')

    # the watchman
    s.style(kf("lid", [(0, "transform:scaleY(.03)"), (5, "transform:scaleY(.03)"), (12, "transform:scaleY(1)"), (56, "transform:scaleY(1)"),
                       (57.5, "transform:scaleY(.07)"), (59, "transform:scaleY(1)"), (90, "transform:scaleY(1)"), (96, "transform:scaleY(.03)"),
                       (100, "transform:scaleY(.03)")]))
    s.style(kf("look", [(0, "transform:translate(0,0)"), (26, "transform:translate(0,0)"), (30, "transform:translate(-44px,6px)"),
                        (40, "transform:translate(-44px,6px)"), (44, "transform:translate(44px,6px)"), (52, "transform:translate(44px,6px)"),
                        (55, "transform:translate(0,-4px)"), (100, "transform:translate(0,-4px)")]))
    s.style(kf("dil", [(0, "transform:scale(1)"), (14, "transform:scale(1.5)"), (28, "transform:scale(.8)"), (62, "transform:scale(1.3)"),
                       (100, "transform:scale(1)")]))
    s.style(kf("glow", [(0, "opacity:0"), (8, "opacity:0"), (16, "opacity:1"), (88, "opacity:1"), (96, "opacity:0"), (100, "opacity:0")]))
    s.defs += (f'<radialGradient id="halo"><stop offset="0" stop-color="{AMBER}" stop-opacity=".22"/>'
               f'<stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></radialGradient>')
    stops = ";".join(c for _, _, _, c, _ in WORLDS.values()) + ";" + list(WORLDS.values())[0][3]
    rims = ";".join(r for *_, r in WORLDS.values()) + ";" + list(WORLDS.values())[0][4]
    s.defs += (f'<radialGradient id="big" cx=".42" cy=".38" r=".72"><stop offset="0" stop-color="{AMBER}">'
               f'<animate attributeName="stop-color" values="{stops}" dur="{L*3}s" repeatCount="indefinite"/></stop>'
               f'<stop offset=".6" stop-color="{AMBER}" stop-opacity=".8"><animate attributeName="stop-color" values="{stops}" dur="{L*3}s" repeatCount="indefinite"/></stop>'
               f'<stop offset="1" stop-color="#1a1208"><animate attributeName="stop-color" values="{rims}" dur="{L*3}s" repeatCount="indefinite"/></stop></radialGradient>')
    s.add(f'<ellipse cx="500" cy="190" rx="230" ry="130" fill="url(#halo)" style="animation:glow {L}s infinite"/>')
    striae = "".join(
        f'<line x1="{math.cos(a)*16:.1f}" y1="{math.sin(a)*16:.1f}" x2="{math.cos(a)*50:.1f}" y2="{math.sin(a)*50:.1f}" '
        f'stroke="#000" stroke-opacity=".22" stroke-width="1.2"/>'
        for a in [i * math.pi / 22 for i in range(44)])
    s.add(f'<g transform="translate(500,190)"><g class="a" style="animation:lid {L}s infinite cubic-bezier(.6,0,.3,1)">'
          f'<path d="{almond(300, 204)}" fill="{SCL}"/>'
          f'<g clip-path="url(#alm300)"><g style="animation:look {L}s infinite cubic-bezier(.5,0,.2,1)">'
          f'<circle r="54" fill="url(#big)"/>{striae}<circle r="54" fill="none" stroke="#000" stroke-opacity=".35" stroke-width="3"/>'
          f'<g class="a" style="animation:dil {L}s infinite ease-in-out"><circle r="19" fill="{BG}"/></g>'
          f'<circle cx="-17" cy="-19" r="7" fill="#fff" opacity=".9"/><circle cx="14" cy="16" r="3" fill="#fff" opacity=".45"/></g></g>'
          f'<path d="{almond(300, 204)}" fill="none" stroke="{RIM}" stroke-width="3"/></g></g>')

    # title, letter by letter
    for i, ch in enumerate("THYIMPALER"):
        t0 = 13 + i * 1.3
        s.style(kf(f"t{i}", [(0, "opacity:0;transform:translateY(16px)"), (t0, "opacity:0;transform:translateY(16px)"),
                             (t0 + 3.5, "opacity:1;transform:translateY(0)"), (88 + i * .4, "opacity:1;transform:translateY(0)"),
                             (92 + i * .4, "opacity:0;transform:translateY(-6px)"), (100, "opacity:0;transform:translateY(16px)")]))
        s.add(f'<text x="{500 + (i - 4.5) * 52:.0f}" y="362" text-anchor="middle" fill="{INK}" font-family="{SERIF}" font-size="54" '
              f'style="animation:t{i} {L}s infinite cubic-bezier(.2,.7,.2,1)">{ch}</text>')
    s.style(kf("sub", [(0, "opacity:0"), (28, "opacity:0"), (33, "opacity:1"), (88, "opacity:1"), (92, "opacity:0"), (100, "opacity:0")]))
    s.add(f'<text x="500" y="398" text-anchor="middle" fill="{SUB}" font-family="{MONO}" font-size="14" letter-spacing="2" '
          f'style="animation:sub {L}s infinite">full-stack &amp; smart contract engineer</text>')

    # HUD
    s.add(f'<text x="42" y="52" fill="{AMBER}" font-family="{MONO}" font-size="11" letter-spacing="3">ARGUS PANOPTES</text>')
    s.add(f'<text x="42" y="68" fill="{DIM}" font-family="{MONO}" font-size="11" letter-spacing="3">THE HUNDRED-EYED</text>')
    s.add(f'<text x="42" y="424" fill="{DIM}" font-family="{MONO}" font-size="11" letter-spacing="3">IMPALER.DEV</text>')
    s.add(f'<text x="958" y="52" text-anchor="end" fill="{DIM}" font-family="{MONO}" font-size="11" letter-spacing="3">EYES OPEN</text>')
    wakes = sorted(e[4] + 2 for e in eyes)
    shut_at = min(e[6] for e in eyes)
    marks = [0] + [wakes[n * 10 - 1] for n in range(1, 11)]
    for n in range(11):
        if n == 0:
            vis = [(0, "opacity:1"), (marks[1], "opacity:0"), (shut_at, "opacity:1"), (100, "opacity:1")]
        else:
            b = marks[n + 1] if n < 10 else shut_at
            vis = [(0, "opacity:0"), (marks[n], "opacity:1"), (b, "opacity:0"), (100, "opacity:0")]
        s.style(kf(f"n{n}", vis))
        s.add(f'<text x="958" y="70" text-anchor="end" fill="{AMBER}" font-family="{MONO}" font-size="15" letter-spacing="3" '
              f'style="animation:n{n} {L}s infinite step-end">{n*10:03d}/100</text>')
    s.style(kf("rec", [(0, "opacity:1"), (50, "opacity:.15"), (100, "opacity:1")]))
    s.add(f'<circle cx="866" cy="420" r="4" fill="{AMBER}" style="animation:rec 1.6s infinite"/>')
    s.add(f'<text x="958" y="424" text-anchor="end" fill="{DIM}" font-family="{MONO}" font-size="11" letter-spacing="3">WATCHING</text>')
    return s.render()


# --------------------------------------------------------------------------- world panel frame
def panel(key, lines, scene, css=(), defs=""):
    num, name, domain, c, r = WORLDS[key]
    W, H = 1000, 300
    s = Svg(W, H, defs=iris_grads() + alm_clip(34) + defs)
    s.style(kf("pb", [(0, "transform:scaleY(1)"), (92, "transform:scaleY(1)"), (94, "transform:scaleY(.08)"), (96, "transform:scaleY(1)"),
                      (100, "transform:scaleY(1)")]))
    s.add(f'<path d="M18 40 V18 H40" stroke="{c}" stroke-width="2" fill="none" opacity=".7"/>')
    s.add(f'<path d="M982 260 V282 H960" stroke="{c}" stroke-width="2" fill="none" opacity=".7"/>')
    s.add(f'<g transform="translate(70,64)">' + eye(key, 34, style="animation:pb 5s infinite", stroke=2) + '</g>')
    s.add(f'<text x="100" y="69" fill="{AMBER}" font-family="{MONO}" font-size="12" letter-spacing="3">WORLD {num} · {escape(domain.upper())}</text>')
    s.add(f'<text x="52" y="142" fill="{INK}" font-family="{SERIF}" font-size="56">{name}</text>')
    for i, ln in enumerate(lines):
        s.add(f'<text x="54" y="{188 + i*22}" fill="{SUB}" font-family="{MONO}" font-size="13.5">{escape(ln)}</text>')
    s.add(f'<line x1="470" y1="36" x2="470" y2="264" stroke="{LINE}" stroke-width="1.5"/>')
    for x in css:
        s.style(x)
    s.add(scene)
    return s.render()


# --------------------------------------------------------------------------- I · the mint
def mint():
    L = 6
    css = [
        kf("press", [(0, "transform:translateY(0)"), (20, "transform:translateY(0)"), (30, "transform:translateY(24px)"),
                     (38, "transform:translateY(24px)"), (55, "transform:translateY(0)"), (100, "transform:translateY(0)")]),
        kf("flash", [(0, "opacity:0;transform:scale(.4)"), (29, "opacity:0;transform:scale(.4)"), (31, "opacity:1;transform:scale(1)"),
                     (45, "opacity:0;transform:scale(1.8)"), (100, "opacity:0")]),
    ]
    steps = [(0, "opacity:0;transform:translate(0,0) scale(.7)"), (7, "opacity:0;transform:translate(0,0) scale(.7)"),
             (9, "opacity:1;transform:translate(0,0) scale(1)")]
    for k in range(4):
        a, b = 13 + k * 25, 23 + k * 25
        steps += [(a, f"opacity:1;transform:translate({k*92}px,0) scale(1)"), (b, f"opacity:1;transform:translate({(k+1)*92}px,0) scale(1)")]
    steps[-1] = (98, "opacity:0;transform:translate(368px,0) scale(1)")
    steps += [(100, "opacity:0;transform:translate(0,0) scale(.7)")]
    css.append(kf("card", steps))
    css.append(kf("shim", [(0, "transform:translateX(-60px)"), (60, "transform:translateX(260px)"), (100, "transform:translateX(260px)")]))

    worlds = list(WORLDS)
    cards = ""
    for k in range(4):
        wk = ["desk", "arcade", "chain", "room"][k]
        cards += (f'<g transform="translate(528,138)"><g class="a" style="animation:card {L*4}s {-k*L}s infinite">'
                  f'<rect width="64" height="86" rx="7" fill="{PANEL}" stroke="#E9E1C8" stroke-opacity=".55" stroke-width="1.5"/>'
                  f'<text x="8" y="15" fill="{DIM}" font-family="{MONO}" font-size="8" letter-spacing="1">ERC-721</text>'
                  f'<g transform="translate(32,44)">{eye(wk, 34, stroke=1.5)}</g>'
                  f'<text x="32" y="78" text-anchor="middle" fill="{SUB}" font-family="{MONO}" font-size="9">{["0x9f1a", "0x3c77", "0xa402", "0x77e0"][k]}</text></g></g>')
    press = (f'<rect x="530" y="34" width="60" height="30" rx="4" fill="{PANEL}" stroke="{RIM}"/>'
             f'<g style="animation:press {L}s infinite cubic-bezier(.7,0,.3,1)">'
             f'<rect x="551" y="64" width="18" height="40" fill="#241f19" stroke="{RIM}"/>'
             f'<rect x="522" y="100" width="76" height="14" rx="3" fill="#2d2720" stroke="#E9E1C8" stroke-opacity=".4"/></g>'
             f'<g transform="translate(560,138)"><g class="a" style="animation:flash {L}s infinite">'
             f'<circle r="16" fill="none" stroke="{AMBER}" stroke-width="2"/></g></g>')
    track = (f'<line x1="516" y1="226" x2="960" y2="226" stroke="{RIM}" stroke-width="2"/>'
             + "".join(f'<line x1="{x}" y1="226" x2="{x-8}" y2="234" stroke="{LINE}" stroke-width="1.5"/>' for x in range(528, 960, 16)))
    split = (f'<text x="700" y="52" fill="{DIM}" font-family="{MONO}" font-size="10" letter-spacing="2">PRIMARY MINT SPLIT</text>'
             f'<clipPath id="bar"><rect x="700" y="62" width="250" height="10" rx="5"/></clipPath>'
             f'<g clip-path="url(#bar)"><rect x="700" y="62" width="250" height="10" fill="{LINE}"/>'
             f'<rect x="700" y="62" width="237" height="10" fill="#E9E1C8"/>'
             f'<rect x="700" y="62" width="50" height="10" fill="#fff" opacity=".35" style="animation:shim 3s infinite"/></g>'
             f'<text x="700" y="92" fill="#E9E1C8" font-family="{MONO}" font-size="11">95% creator</text>'
             f'<text x="950" y="92" text-anchor="end" fill="{DIM}" font-family="{MONO}" font-size="11">5%</text>')
    code = (f'<text x="516" y="262" fill="{DIM}" font-family="{MONO}" font-size="11.5">factory.deploy() → '
            f'<tspan fill="#E9E1C8">mint()</tspan> → pull payments, no reentrancy</text>')
    return panel("mint", ["erc-721 factories, royalties,", "reentrancy guards, pull payments.", "nest · $CHAD"],
                 split + track + cards + press + code, css)


# --------------------------------------------------------------------------- II · the vault
def vault():
    L = 9
    css = [
        kf("dial", [(0, "transform:rotate(0deg)"), (14, "transform:rotate(-252deg)"), (22, "transform:rotate(-252deg)"),
                    (36, "transform:rotate(-100deg)"), (44, "transform:rotate(-100deg)"), (58, "transform:rotate(-318deg)"),
                    (88, "transform:rotate(-318deg)"), (100, "transform:rotate(-360deg)")]),
        kf("ring", [(0, "opacity:0"), (60, "opacity:0"), (63, "opacity:1"), (86, "opacity:1"), (92, "opacity:0"), (100, "opacity:0")]),
        kf("locked", [(0, "opacity:1"), (60, "opacity:1"), (61, "opacity:0"), (90, "opacity:0"), (91, "opacity:1"), (100, "opacity:1")]),
        kf("open", [(0, "opacity:0"), (60, "opacity:0"), (61, "opacity:1"), (90, "opacity:1"), (91, "opacity:0"), (100, "opacity:0")]),
        kf("fill", [(0, "transform:scaleX(0)")] + [(7 + i * 13, f"transform:scaleX({v})") for i, v in
                                                     enumerate([.18, .34, .48, .71, 1.0])] +
           [(94, "transform:scaleX(1)"), (97, "transform:scaleX(0)"), (100, "transform:scaleX(0)")]),
        kf("shake", [(0, "transform:translateX(0)"), (70, "transform:translateX(0)"), (71, "transform:translateX(-5px)"),
                     (72, "transform:translateX(5px)"), (73, "transform:translateX(-3px)"), (74, "transform:translateX(0)"),
                     (100, "transform:translateX(0)")]),
        kf("deny", [(0, "opacity:0"), (70, "opacity:0"), (71, "opacity:1"), (92, "opacity:1"), (95, "opacity:0"), (100, "opacity:0")]),
    ]
    ticks = ""
    for i in range(80):
        a = i * 2 * math.pi / 80
        r1 = 78 if i % 8 == 0 else 84
        ticks += (f'<line x1="{math.sin(a)*r1:.1f}" y1="{-math.cos(a)*r1:.1f}" x2="{math.sin(a)*90:.1f}" y2="{-math.cos(a)*90:.1f}" '
                  f'stroke="{"#D6E2EE" if i % 8 == 0 else RIM}" stroke-width="{2 if i % 8 == 0 else 1.2}"/>')
        if i % 8 == 0:
            ticks += (f'<text x="{math.sin(a)*64:.1f}" y="{-math.cos(a)*64+4:.1f}" text-anchor="middle" fill="{SUB}" '
                      f'font-family="{MONO}" font-size="10">{i//2}</text>')
    grip = "".join(f'<line x1="{math.sin(i*math.pi/6)*18:.1f}" y1="{-math.cos(i*math.pi/6)*18:.1f}" '
                   f'x2="{math.sin(i*math.pi/6)*30:.1f}" y2="{-math.cos(i*math.pi/6)*30:.1f}" stroke="#0d0b09" stroke-width="3"/>'
                   for i in range(12))
    dial = (f'<g transform="translate(620,150)">'
            f'<circle r="100" fill="{PANEL}" stroke="{RIM}" stroke-width="2"/>'
            f'<circle r="104" fill="none" stroke="#D6E2EE" stroke-width="2" style="animation:ring {L}s infinite"/>'
            f'<g style="animation:dial {L}s infinite cubic-bezier(.6,0,.25,1)">{ticks}'
            f'<circle r="36" fill="#2a2f36" stroke="#D6E2EE" stroke-opacity=".4"/>{grip}<circle r="12" fill="#1B2530"/></g>'
            f'<path d="M0 -104 L-8 -118 H8Z" fill="{AMBER}"/></g>'
            f'<text x="620" y="276" text-anchor="middle" fill="{DIM}" font-family="{MONO}" font-size="11" letter-spacing="3" '
            f'style="animation:locked {L}s infinite">LOCKED</text>'
            f'<text x="620" y="276" text-anchor="middle" fill="#D6E2EE" font-family="{MONO}" font-size="11" letter-spacing="3" '
            f'style="animation:open {L}s infinite">OPEN</text>')
    rows = ["reserve $1.80  ok", "reserve $1.60  ok", "reserve $1.40  ok", "reserve $2.30  ok", "reserve $2.90  ok"]
    ledger = (f'<text x="760" y="52" fill="{DIM}" font-family="{MONO}" font-size="10" letter-spacing="2">PASS k3y_9f · CAP $10.00</text>'
              f'<g style="animation:shake {L}s infinite"><rect x="760" y="62" width="200" height="12" rx="6" fill="{LINE}"/>'
              f'<rect class="l" x="760" y="62" width="200" height="12" rx="6" fill="#D6E2EE" style="animation:fill {L}s infinite steps(1,end)"/></g>')
    for i, row in enumerate(rows):
        t = 6 + i * 13
        css.append(kf(f"r{i}", [(0, "opacity:0"), (t, "opacity:0"), (t + 1, "opacity:1"), (94, "opacity:1"), (96, "opacity:0"), (100, "opacity:0")]))
        ledger += (f'<text x="760" y="{104 + i*20}" fill="{SUB}" font-family="{MONO}" font-size="11.5" style="animation:r{i} {L}s infinite">'
                   f'<tspan fill="{DIM}">{i+1:02d}</tspan>  {row}</text>')
    ledger += (f'<g style="animation:deny {L}s infinite"><rect x="760" y="206" width="200" height="26" rx="4" fill="#2a1216" stroke="#f7768e"/>'
               f'<text x="770" y="223" fill="#f7768e" font-family="{MONO}" font-size="11.5">06  402 · cap reached</text></g>'
               f'<text x="760" y="258" fill="{DIM}" font-family="{MONO}" font-size="10.5">12 raced in at once. 10 fit. 0 leaked.</text>')
    return panel("vault", ["keypass. share ai access,", "never the key. a ledger that", "can't be raced past its cap."],
                 dial + ledger, css)


# --------------------------------------------------------------------------- III · the chain
def chain():
    L = 10
    X = [520 + i * 90 for i in range(5)]
    css = [kf("pulse", [(0, "transform:translateX(0);opacity:0"), (5, "opacity:1"), (90, "opacity:1"),
                        (100, "transform:translateX(420px);opacity:0")])]
    body = f'<line x1="520" y1="150" x2="950" y2="150" stroke="{RIM}" stroke-width="2" stroke-dasharray="4 6"/>'
    body += f'<g style="animation:pulse 2.6s infinite linear"><circle cx="520" cy="150" r="4" fill="#CFE3F5"/></g>'

    def block(x, label, h, stroke, cls, dot=False):
        d = f'<circle cx="{x+54}" cy="{120+14}" r="5" fill="{AMBER}"/>' if dot else ""
        return (f'<g style="animation:{cls} {L}s infinite cubic-bezier(.3,.7,.2,1)">'
                f'<rect x="{x}" y="120" width="70" height="60" rx="7" fill="{PANEL}" stroke="{stroke}" stroke-width="1.6"/>'
                f'<text x="{x+10}" y="140" fill="{INK}" font-family="{MONO}" font-size="11">#{label}</text>'
                f'<text x="{x+10}" y="170" fill="{DIM}" font-family="{MONO}" font-size="9.5">{h}</text>{d}</g>')

    for i in range(3):
        body += block(X[i], 402 + i, ["0x9f1a", "0x3c77", "0xa402"][i], "#CFE3F5", "none")
    css += [
        kf("b3", [(0, "opacity:0;transform:translateY(-30px)"), (6, "opacity:0;transform:translateY(-30px)"), (10, "opacity:1;transform:translateY(0)"),
                  (38, "opacity:1;transform:translateY(0)"), (44, "opacity:0;transform:translateY(40px)"), (100, "opacity:0;transform:translateY(40px)")]),
        kf("b4", [(0, "opacity:0;transform:translateY(-30px)"), (14, "opacity:0;transform:translateY(-30px)"), (18, "opacity:1;transform:translateY(0)"),
                  (38, "opacity:1;transform:translateY(0)"), (44, "opacity:0;transform:translateY(40px)"), (100, "opacity:0;transform:translateY(40px)")]),
        kf("bad", [(0, "opacity:0"), (27, "opacity:0"), (28, "opacity:1"), (30, "opacity:.2"), (32, "opacity:1"), (34, "opacity:.2"),
                   (36, "opacity:1"), (42, "opacity:0"), (100, "opacity:0")]),
        kf("keep", [(0, "opacity:0"), (42, "opacity:0"), (45, "opacity:1"), (60, "opacity:1"), (64, "opacity:0"), (100, "opacity:0")]),
        kf("n3", [(0, "opacity:0;transform:translateY(-30px)"), (56, "opacity:0;transform:translateY(-30px)"), (60, "opacity:1;transform:translateY(0)"),
                  (93, "opacity:1;transform:translateY(0)"), (98, "opacity:0;transform:translateY(0)"), (100, "opacity:0;transform:translateY(-30px)")]),
        kf("n4", [(0, "opacity:0;transform:translateY(-30px)"), (63, "opacity:0;transform:translateY(-30px)"), (67, "opacity:1;transform:translateY(0)"),
                  (93, "opacity:1;transform:translateY(0)"), (98, "opacity:0;transform:translateY(0)"), (100, "opacity:0;transform:translateY(-30px)")]),
        kf("ok", [(0, "opacity:0"), (72, "opacity:0"), (75, "opacity:1"), (93, "opacity:1"), (98, "opacity:0"), (100, "opacity:0")]),
    ]
    body += block(X[3], 405, "0x77e0", "#CFE3F5", "b3", dot=True)
    body += block(X[4], 406, "0x1be9", "#CFE3F5", "b4")
    body += (f'<g style="animation:bad {L}s infinite"><rect x="{X[3]-4}" y="116" width="164" height="68" rx="9" fill="none" stroke="#f7768e" stroke-width="2"/>'
             f'<text x="{X[3]+78}" y="104" text-anchor="middle" fill="#f7768e" font-family="{MONO}" font-size="12" letter-spacing="3">REORG</text></g>')
    body += (f'<g style="animation:keep {L}s infinite"><rect x="{X[2]-4}" y="116" width="78" height="68" rx="9" fill="none" stroke="{AMBER}" stroke-width="2"/>'
             f'<text x="{X[2]+35}" y="104" text-anchor="middle" fill="{AMBER}" font-family="{MONO}" font-size="11" letter-spacing="2">⟲ REWIND</text>'
             f'<text x="{X[2]+35}" y="206" text-anchor="middle" fill="{AMBER}" font-family="{MONO}" font-size="10">last hash kept</text></g>')
    body += block(X[3], 405, "0xd40c", "#7CFF9B", "n3", dot=True)
    body += block(X[4], 406, "0x58aa", "#7CFF9B", "n4")
    body += (f'<g style="animation:ok {L}s infinite"><text x="{X[3]+78}" y="104" text-anchor="middle" fill="#7CFF9B" font-family="{MONO}" '
             f'font-size="12" letter-spacing="3">REPLAYED</text>'
             f'<text x="{X[3]+54}" y="206" text-anchor="middle" fill="{AMBER}" font-family="{MONO}" font-size="10">mint still there</text></g>')
    css.append(kf("route", [(0, "stroke-dashoffset:24"), (100, "stroke-dashoffset:0")]))
    css.append(kf("hop", [(0, "transform:translateX(0);opacity:0"), (10, "opacity:1"), (80, "opacity:1"), (100, "transform:translateX(140px);opacity:0")]))
    for nx, lab in [(560, "BESC"), (700, "BNB"), (840, "ETH")]:
        body += (f'<rect x="{nx-26}" y="222" width="52" height="20" rx="10" fill="{PANEL}" stroke="#CFE3F5" stroke-opacity=".5"/>'
                 f'<text x="{nx}" y="236" text-anchor="middle" fill="{SUB}" font-family="{MONO}" font-size="10" letter-spacing="1">{lab}</text>')
    body += (f'<path d="M586 232 H674 M726 232 H814" stroke="#CFE3F5" stroke-opacity=".6" stroke-width="1.5" stroke-dasharray="4 8" '
             f'style="animation:route 1s infinite linear"/>'
             f'<g style="animation:hop 2.2s infinite ease-in-out"><circle cx="590" cy="232" r="3.5" fill="{AMBER}"/></g>'
             f'<g style="animation:hop 2.2s 1.1s infinite ease-in-out"><circle cx="730" cy="232" r="3.5" fill="{AMBER}"/></g>'
             f'<text x="880" y="236" fill="{DIM}" font-family="{MONO}" font-size="10">phantom bridge</text>')
    body += (f'<text x="516" y="52" fill="{DIM}" font-family="{MONO}" font-size="10" letter-spacing="2">NEST INDEXER · ROBINHOOD CHAIN</text>'
             f'<text x="516" y="88" fill="{DIM}" font-family="{MONO}" font-size="10.5">reorg → rewind → replay. nothing quietly lost.</text>')
    return panel("chain", ["an indexer that rewinds a reorg", "instead of eating a mint.", "phantom bridge · besc → bnb/eth"],
                 body, css)


# --------------------------------------------------------------------------- IV · the desk
def desk():
    L = 11
    rnd = random.Random(4)
    n, p = 24, 100.0
    candles = []
    for i in range(n):
        o = p
        if i < 15:
            p += rnd.uniform(-2.4, 2.4) + (100 - p) * 0.25
        else:
            p += rnd.uniform(1.4, 4.8) - (0.9 if i in (19, 21) else 0) * 6
        hi, lo = max(o, p) + rnd.uniform(.3, 1.6), min(o, p) - rnd.uniform(.3, 1.6)
        candles.append((o, p, hi, lo))
    top = max(c[2] for c in candles) + 2
    bot = min(c[3] for c in candles) - 2
    Y = lambda v: 74 + (top - v) / (top - bot) * 150
    css, body = [], ""
    for gy in range(4):
        y = 60 + gy * 50
        body += f'<line x1="510" y1="{y}" x2="960" y2="{y}" stroke="#15261a" stroke-width="1" stroke-dasharray="3 5"/>'
    res = max(c[2] for c in candles[:15])
    body += (f'<line x1="510" y1="{Y(res):.1f}" x2="960" y2="{Y(res):.1f}" stroke="{AMBER}" stroke-opacity=".5" stroke-dasharray="6 4"/>'
             f'<text x="514" y="{Y(res)-6:.1f}" fill="{AMBER}" fill-opacity=".7" font-family="{MONO}" font-size="9.5" letter-spacing="1">LIQUIDITY</text>')
    for i, (o, c, hi, lo) in enumerate(candles):
        t = 3 + i * 2.7
        css.append(kf(f"c{i}", [(0, "opacity:0;transform:scaleY(.2)"), (t, "opacity:0;transform:scaleY(.2)"), (t + 1.5, "opacity:1;transform:scaleY(1)"),
                                (90, "opacity:1;transform:scaleY(1)"), (95, "opacity:0;transform:scaleY(1)"), (100, "opacity:0;transform:scaleY(.2)")]))
        x = 516 + i * 18
        col = "#7CFF9B" if c >= o else "#ff5c7a"
        y1, y2 = Y(max(o, c)), Y(min(o, c))
        vol = rnd.uniform(6, 16) + (14 if i >= 15 else 0)
        body += (f'<g class="a" style="animation:c{i} {L}s infinite cubic-bezier(.2,.8,.2,1)">'
                 f'<line x1="{x+5}" y1="{Y(hi):.1f}" x2="{x+5}" y2="{Y(lo):.1f}" stroke="{col}" stroke-width="1.4"/>'
                 f'<rect x="{x}" y="{y1:.1f}" width="10" height="{max(y2-y1, 1.5):.1f}" fill="{col}" rx="1"/>'
                 f'<rect x="{x}" y="{262-vol:.1f}" width="10" height="{vol:.1f}" fill="{col}" opacity=".35"/></g>')
    bi = 16
    bx, by = 516 + bi * 18, Y(candles[bi][2])
    t = 3 + bi * 2.7 + 2
    css.append(kf("sig", [(0, "opacity:0;transform:translateY(8px)"), (t, "opacity:0;transform:translateY(8px)"), (t + 2, "opacity:1;transform:translateY(0)"),
                          (90, "opacity:1;transform:translateY(0)"), (95, "opacity:0"), (100, "opacity:0")]))
    css.append(kf("ping", [(0, "transform:scale(.5);opacity:1"), (100, "transform:scale(2.4);opacity:0")]))
    body += (f'<g style="animation:sig {L}s infinite"><g transform="translate({bx+5},{by-4:.1f})"><g class="a" style="animation:ping 1.2s infinite">'
             f'<circle r="8" fill="none" stroke="#7CFF9B" stroke-width="1.5"/></g></g>'
             f'<rect x="{bx-190}" y="42" width="178" height="42" rx="5" fill="#0b1a0f" stroke="#7CFF9B" stroke-opacity=".6"/>'
             f'<text x="{bx-180}" y="59" fill="#7CFF9B" font-family="{MONO}" font-size="10.5" letter-spacing="1">⚡ ALPHA SIGNALS</text>'
             f'<text x="{bx-180}" y="75" fill="{SUB}" font-family="{MONO}" font-size="10">onchain agents · EARLY → HEATING</text></g>')
    body += f'<text x="960" y="52" text-anchor="end" fill="{DIM}" font-family="{MONO}" font-size="10" letter-spacing="2">PERPS · 15M</text>'
    return panel("desk", ["reading narratives before the", "rotation is obvious. memecoins", "and perps since 2024."], body, css)


# --------------------------------------------------------------------------- V · the arcade
def arcade():
    L = 7
    defs = ('<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1.3" fill="#000" opacity=".35"/></pattern>'
            '<pattern id="net" width="14" height="14" patternUnits="userSpaceOnUse"><path d="M0 0H14M0 0V14" stroke="#FF3D8B" stroke-opacity=".22"/></pattern>')
    css = [
        kf("ball", [(0, "transform:translate(0,0) scale(1);opacity:1"), (12, "transform:translate(0,0) scale(1);opacity:1"),
                    (22, "transform:translate(-106px,-150px) scale(.55);opacity:1"), (36, "transform:translate(-106px,-150px) scale(.55);opacity:1"),
                    (40, "transform:translate(-106px,-150px) scale(.55);opacity:0"), (46, "transform:translate(0,0) scale(1);opacity:0"),
                    (50, "transform:translate(0,0) scale(1);opacity:1"), (60, "transform:translate(0,0) scale(1);opacity:1"),
                    (68, "transform:translate(-86px,-116px) scale(.6);opacity:1"), (78, "transform:translate(-160px,-14px) scale(.75);opacity:1"),
                    (90, "transform:translate(-160px,-14px) scale(.75);opacity:1"), (94, "transform:translate(-160px,-14px) scale(.75);opacity:0"),
                    (100, "transform:translate(0,0) scale(1);opacity:0")]),
        kf("keeper", [(0, "transform:translate(0,0) rotate(0)"), (6, "transform:translate(-6px,0) rotate(0)"), (12, "transform:translate(6px,0) rotate(0)"),
                      (15, "transform:translate(0,0) rotate(0)"), (22, "transform:translate(88px,16px) rotate(30deg)"),
                      (38, "transform:translate(88px,16px) rotate(30deg)"), (46, "transform:translate(0,0) rotate(0)"),
                      (56, "transform:translate(-6px,0) rotate(0)"), (60, "transform:translate(0,0) rotate(0)"),
                      (66, "transform:translate(-86px,-6px) rotate(-30deg)"), (86, "transform:translate(-86px,-6px) rotate(-30deg)"),
                      (94, "transform:translate(0,0) rotate(0)"), (100, "transform:translate(0,0) rotate(0)")]),
        kf("goal", [(0, "opacity:0;transform:scale(.6)"), (22, "opacity:0;transform:scale(.6)"), (24, "opacity:1;transform:scale(1.08)"),
                    (26, "opacity:1;transform:scale(1)"), (38, "opacity:1;transform:scale(1)"), (41, "opacity:0;transform:scale(1)"), (100, "opacity:0")]),
        kf("saved", [(0, "opacity:0;transform:scale(.6)"), (69, "opacity:0;transform:scale(.6)"), (71, "opacity:1;transform:scale(1.08)"),
                     (73, "opacity:1;transform:scale(1)"), (88, "opacity:1;transform:scale(1)"), (91, "opacity:0"), (100, "opacity:0")]),
        kf("netshake", [(0, "transform:translate(0,0)"), (22, "transform:translate(0,0)"), (23, "transform:translate(-3px,-2px)"),
                        (25, "transform:translate(2px,1px)"), (27, "transform:translate(0,0)"), (100, "transform:translate(0,0)")]),
        kf("s0", [(0, "opacity:1"), (24, "opacity:1"), (24.01, "opacity:0"), (71, "opacity:0"), (71.01, "opacity:1"), (100, "opacity:1")]),
        kf("s1", [(0, "opacity:0"), (24, "opacity:0"), (24.01, "opacity:1"), (71, "opacity:1"), (71.01, "opacity:0"), (100, "opacity:0")]),
    ]
    body = f'<rect x="500" y="30" width="460" height="240" rx="10" fill="#120a14"/>'
    body += (f'<g style="animation:netshake {L}s infinite"><rect x="590" y="72" width="280" height="122" fill="url(#net)"/></g>'
             f'<path d="M590 194 V72 H870 V194" fill="none" stroke="#FFE14D" stroke-width="6" shape-rendering="crispEdges"/>'
             f'<line x1="520" y1="194" x2="940" y2="194" stroke="#FFE14D" stroke-opacity=".25" stroke-width="2"/>'
             f'<circle cx="730" cy="252" r="3" fill="#FFE14D" opacity=".4"/>')
    keeper = ('<g shape-rendering="crispEdges">'
              '<rect x="-6" y="-34" width="12" height="12" fill="#E9D3B0"/><rect x="-10" y="-22" width="20" height="22" fill="#FF3D8B"/>'
              '<rect x="-24" y="-20" width="14" height="6" fill="#FF3D8B"/><rect x="10" y="-20" width="14" height="6" fill="#FF3D8B"/>'
              '<rect x="-31" y="-23" width="8" height="10" fill="#FFE14D"/><rect x="23" y="-23" width="8" height="10" fill="#FFE14D"/>'
              '<rect x="-10" y="0" width="20" height="8" fill="#231a26"/><rect x="-9" y="8" width="6" height="14" fill="#E9D3B0"/>'
              '<rect x="3" y="8" width="6" height="14" fill="#E9D3B0"/></g>')
    body += f'<g transform="translate(730,172)"><g style="animation:keeper {L}s infinite cubic-bezier(.3,.6,.2,1)">{keeper}</g></g>'
    body += (f'<g transform="translate(730,252)"><g style="animation:ball {L}s infinite cubic-bezier(.2,.7,.3,1)">'
             f'<rect x="-7" y="-7" width="14" height="14" fill="#fff" shape-rendering="crispEdges"/>'
             f'<rect x="-3" y="-3" width="6" height="6" fill="#231a26" shape-rendering="crispEdges"/></g></g>')

    def big(txt, anim, col):
        return (f'<g transform="translate(730,132)"><g class="a" style="animation:{anim} {L}s infinite">'
                f'<text x="3" y="3" text-anchor="middle" fill="#FF3D8B" font-family="{MONO}" font-weight="700" font-size="46" letter-spacing="6">{txt}</text>'
                f'<text x="0" y="0" text-anchor="middle" fill="{col}" font-family="{MONO}" font-weight="700" font-size="46" letter-spacing="6">{txt}</text></g></g>')

    body += big("GOAL", "goal", "#FFE14D") + big("SAVED", "saved", "#ffffff")
    body += (f'<text x="516" y="54" fill="#FFE14D" font-family="{MONO}" font-size="11" letter-spacing="3" style="animation:s0 {L}s infinite">STREAK 00</text>'
             f'<text x="516" y="54" fill="#FFE14D" font-family="{MONO}" font-size="11" letter-spacing="3" style="animation:s1 {L}s infinite">STREAK 01</text>'
             f'<text x="944" y="54" text-anchor="end" fill="#FF3D8B" font-family="{MONO}" font-size="11" letter-spacing="3">$RIGGK</text>')
    body += '<rect x="500" y="30" width="460" height="240" rx="10" fill="url(#scan)"/>'
    return panel("arcade", ["go the same way twice and the", "keeper will be there.", "$RIGGK · henny run"], body, css, defs)


# --------------------------------------------------------------------------- VI · the room
def room():
    L = 10
    rnd = random.Random(9)
    css = [kf("tw", [(0, "opacity:.18"), (50, "opacity:.9"), (100, "opacity:.18")])]
    body = ""
    for gx in range(20):
        for gy in range(13):
            x, y = 510 + gx * 12.5 + rnd.uniform(-3, 3), 58 + gy * 15 + rnd.uniform(-3, 3)
            col = "#F1E4D8" if rnd.random() > .08 else AMBER
            body += (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(1.6, 2.8):.1f}" fill="{col}" '
                     f'style="animation:tw {rnd.uniform(2.5, 6):.1f}s {-rnd.uniform(0, 6):.1f}s infinite"/>')
    bubbles = [("gm", 540, 150, 4), ("wen", 690, 110, 16), ("lfg", 600, 220, 30), ("free airdrop [link]", 596, 170, 44), ("ser", 560, 90, 66), ("gm gm", 700, 200, 78)]
    for i, (txt, x, y, t) in enumerate(bubbles):
        w = 14 + len(txt) * 7.2
        spam = "airdrop" in txt
        end = t + (20 if spam else 14)
        css.append(kf(f"b{i}", [(0, "opacity:0;transform:translateY(8px)"), (t, "opacity:0;transform:translateY(8px)"),
                                (t + 2, "opacity:1;transform:translateY(0)"), (end, "opacity:1;transform:translateY(-10px)"),
                                (end + 3, "opacity:0;transform:translateY(-16px)"), (100, "opacity:0;transform:translateY(8px)")]))
        stroke = "#f7768e" if spam else "#F1E4D8"
        extra = ""
        if spam:
            css.append(kf("strike", [(0, "transform:scaleX(0)"), (t + 7, "transform:scaleX(0)"), (t + 9, "transform:scaleX(1)"), (100, "transform:scaleX(1)")]))
            css.append(kf("rm", [(0, "opacity:0"), (t + 9, "opacity:0"), (t + 10, "opacity:1"), (100, "opacity:1")]))
            extra = (f'<rect class="l" x="{x+6}" y="{y-4}" width="{w-12}" height="2" fill="#f7768e" style="animation:strike {L}s infinite"/>'
                     f'<text x="{x+w/2}" y="{y+26}" text-anchor="middle" fill="#f7768e" font-family="{MONO}" font-size="10" letter-spacing="2" '
                     f'style="animation:rm {L}s infinite">REMOVED</text>')
        body += (f'<g style="animation:b{i} {L}s infinite ease-out"><rect x="{x}" y="{y-16}" width="{w:.0f}" height="22" rx="11" fill="#1d1914" '
                 f'stroke="{stroke}" stroke-width="1.4"/><text x="{x+w/2:.0f}" y="{y-1}" text-anchor="middle" fill="{INK}" '
                 f'font-family="{MONO}" font-size="11.5">{txt}</text>{extra}</g>')
    body += (f'<text x="790" y="96" fill="{INK}" font-family="{SERIF}" font-size="44">33,000</text>'
             f'<text x="792" y="116" fill="{DIM}" font-family="{MONO}" font-size="10.5" letter-spacing="2">MEMBERS · KLEIN FUNDING</text>')
    pts = [(790, 250), (805, 244), (818, 247), (832, 236), (846, 240), (860, 226), (872, 230), (884, 214), (896, 206), (906, 212),
           (916, 188), (926, 172), (934, 158), (944, 148)]
    d = "M" + " L".join(f"{x} {y}" for x, y in pts)
    css.append(kf("draw", [(0, "stroke-dashoffset:1"), (8, "stroke-dashoffset:1"), (58, "stroke-dashoffset:0"), (92, "stroke-dashoffset:0"),
                           (97, "stroke-dashoffset:1"), (100, "stroke-dashoffset:1")]))
    css.append(kf("ath", [(0, "opacity:0"), (56, "opacity:0"), (60, "opacity:1"), (92, "opacity:1"), (96, "opacity:0"), (100, "opacity:0")]))
    body += (f'<path d="{d}" fill="none" stroke="{AMBER}" stroke-width="2.2" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" '
             f'style="animation:draw {L}s infinite ease-in-out"/>'
             f'<g style="animation:ath {L}s infinite"><circle cx="944" cy="148" r="4" fill="{AMBER}"/>'
             f'<line x1="790" y1="148" x2="944" y2="148" stroke="{AMBER}" stroke-opacity=".4" stroke-dasharray="3 4"/>'
             f'<text x="790" y="142" fill="{AMBER}" font-family="{MONO}" font-size="11" letter-spacing="1">$HENNY ATH $105K · held</text></g>'
             f'<text x="790" y="272" fill="{DIM}" font-family="{MONO}" font-size="10.5" letter-spacing="2">100% UPTIME</text>')
    return panel("room", ["33,000 members. a $105k peak", "held through the noise.", "klein funding · $HENNY"], body, css)


# --------------------------------------------------------------------------- footer
def footer():
    W, H, L = 1000, 190, 9
    s = Svg(W, H, defs=iris_grads() + alm_clip(180) + f'<radialGradient id="ir-amber" cx=".42" cy=".38" r=".7"><stop offset="0" stop-color="{AMBER}"/><stop offset="1" stop-color="#3a2400"/></radialGradient>')
    s.style(kf("peek", [(0, "transform:scaleY(.03)"), (38, "transform:scaleY(.03)"), (44, "transform:scaleY(.42)"), (68, "transform:scaleY(.42)"),
                        (70, "transform:scaleY(.03)"), (100, "transform:scaleY(.03)")]))
    s.style(kf("peekl", [(0, "transform:translate(0,0)"), (46, "transform:translate(0,0)"), (52, "transform:translate(-26px,0)"),
                         (58, "transform:translate(26px,0)"), (64, "transform:translate(0,0)"), (100, "transform:translate(0,0)")]))
    lashes = "".join(f'<line x1="{x}" y1="{4 + abs(x)*-0.02:.1f}" x2="{x*1.12:.1f}" y2="{16 - abs(x)*0.05:.1f}" stroke="{RIM}" stroke-width="2"/>'
                     for x in range(-60, 61, 20))
    s.add(f'<g transform="translate(500,76)">{lashes}' + eye("amber", 180, style=f"animation:peek {L}s infinite cubic-bezier(.6,0,.3,1)",
                                                              stroke=2.5, look_style=f"animation:peekl {L}s infinite ease-in-out") + '</g>')
    s.add(f'<text x="500" y="136" text-anchor="middle" fill="{INK}" font-family="{SERIF}" font-style="italic" font-size="21">he fell back asleep.</text>')
    s.add(f'<text x="500" y="162" text-anchor="middle" fill="{DIM}" font-family="{MONO}" font-size="11" letter-spacing="3">'
          f'HOLD A LITTLE LONGER AT <tspan fill="{AMBER}">IMPALER.DEV</tspan></text>')
    return s.render()


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    files = {"argus.svg": header(), "w1-mint.svg": mint(), "w2-vault.svg": vault(), "w3-chain.svg": chain(),
             "w4-desk.svg": desk(), "w5-arcade.svg": arcade(), "w6-room.svg": room(), "asleep.svg": footer()}
    for name, svg in files.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(svg)
        print(f"{name:14s} {len(svg)/1024:6.1f} KB")
