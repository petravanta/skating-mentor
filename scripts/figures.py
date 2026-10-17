#!/usr/bin/env python3
"""Draw the skill illustrations in data/illustrations/ from simple pose descriptions.

Figures are stick figures placed by joint positions. Knees and elbows are solved
from hip/ankle and shoulder/hand positions so limbs keep the same lengths.
The SVGs use currentColor for the figure and var(--accent) for what to notice,
so they follow the app's light and dark themes when inlined.
Run `python3 scripts/figures.py` after editing a pose.
"""
import math, os, re

OUT = os.path.join(os.path.dirname(__file__), '..', 'data', 'illustrations')
W, H, FLOOR = 240, 180, 164
THIGH, SHIN, UPPER, FORE, HEAD = 42, 42, 28, 26, 10
SKATE_ANKLE = FLOOR - 24   # ankle height when standing on skates
SHOE_ANKLE = FLOOR - 5

STYLE = """<style>
.fig{fill:none;stroke:currentColor;stroke-width:6;stroke-linecap:round;stroke-linejoin:round}
.far{opacity:.4}
.head{fill:currentColor}
.floor{stroke:currentColor;stroke-width:1.5;opacity:.3}
.wall{stroke:currentColor;stroke-width:3;opacity:.3}
.boot{fill:none;stroke:currentColor;stroke-width:3;stroke-linejoin:round}
.wheel{fill:currentColor}
.prop{fill:none;stroke:currentColor;stroke-width:2;stroke-dasharray:3 3;opacity:.7}
.hl{fill:var(--accent,#c2306f);opacity:.28}
.acc{fill:none;stroke:var(--accent,#c2306f);stroke-width:2.5;stroke-linecap:round}
.dash{stroke-dasharray:5 5}
.pad{fill:var(--accent,#c2306f)}
.lbl{fill:var(--accent,#c2306f);font:600 11px system-ui,-apple-system,sans-serif}
.top{fill:none;stroke:currentColor;stroke-width:3}
.wtop{fill:currentColor;opacity:.55}
</style>
<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="var(--accent,#c2306f)"/></marker></defs>"""

def add(a, b): return (a[0] + b[0], a[1] + b[1])
def sub(a, b): return (a[0] - b[0], a[1] - b[1])
def mul(a, k): return (a[0] * k, a[1] * k)
def norm(a): l = math.hypot(*a) or 1; return (a[0] / l, a[1] / l)
def mid(a, b): return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
def at(p, ang, l): r = math.radians(ang); return (p[0] + math.cos(r) * l, p[1] + math.sin(r) * l)

def joint(a, b, l1, l2, hint):
    """Middle joint (knee/elbow) between a and b, bending toward the hint direction."""
    v = sub(b, a); d = math.hypot(*v)
    if d >= l1 + l2 - 0.5:                      # can't reach: straight limb pointing at b
        return add(a, mul(norm(v), l1))
    x = (l1 * l1 - l2 * l2 + d * d) / (2 * d); y = math.sqrt(max(0, l1 * l1 - x * x))
    u = norm(v); p = (-u[1], u[0])
    if p[0] * hint[0] + p[1] * hint[1] < 0: p = mul(p, -1)
    return add(add(a, mul(u, x)), mul(p, y))

def f(p): return f'{p[0]:.1f},{p[1]:.1f}'

class Fig:
    def __init__(self): self.far, self.near, self.top = [], [], []
    def line(self, pts, far=False):
        (self.far if far else self.near).append(f'<polyline class="fig{" far" if far else ""}" points="{" ".join(f(p) for p in pts)}"/>')
    def leg(self, hip, ankle, hint=(1, 0), toe=0, far=False, skate=None, knee=None):
        """skate: None, 'side' (inline seen from the side, tilted by toe degrees) or 'front'."""
        k = knee or joint(hip, ankle, THIGH, SHIN, hint)
        if skate == 'side': self.side_skate(ankle, toe, far)
        elif skate == 'front': self.front_skate(ankle, toe, far)
        else: self.line([hip, k, ankle, at(ankle, toe, 12)], far); return k
        self.line([hip, k, ankle], far); return k
    def arm(self, sh, hand, hint=(0, 1), far=False):
        e = joint(sh, hand, UPPER, FORE, hint); self.line([sh, e, hand], far); return e
    def body(self, hip, shoulder, head):
        self.near.insert(0, f'<polyline class="fig" points="{f(hip)} {f(shoulder)}"/>')
        self.top.append(f'<circle class="head" cx="{head[0]:.1f}" cy="{head[1]:.1f}" r="{HEAD}"/>')
    def side_skate(self, a, toe=0, far=False):
        u = (math.cos(math.radians(toe)), math.sin(math.radians(toe))); n = (-u[1], u[0])
        if n[1] < 0: n = mul(n, -1)
        P = lambda along, down: add(add(a, mul(u, along)), mul(n, down))
        c = ' far' if far else ''
        pts = [P(-9, -10), P(-9, 6), P(22, 6), P(22, 0), P(4, -4), P(2, -12)]
        out = [f'<path class="boot{c}" d="M{" L".join(f(p) for p in pts)}Z"/>',
               f'<line class="boot{c}" x1="{P(-7,10)[0]:.1f}" y1="{P(-7,10)[1]:.1f}" x2="{P(20,10)[0]:.1f}" y2="{P(20,10)[1]:.1f}"/>']
        out += [f'<circle class="wheel{c}" cx="{P(t,15)[0]:.1f}" cy="{P(t,15)[1]:.1f}" r="4"/>' for t in (-6, 3, 12, 21)]
        (self.far if far else self.near).extend(out)
        self.contact = max(getattr(self, 'contact', 0), max(P(t, 19)[1] for t in (-6, 21)))
    def front_skate(self, a, tilt=0, far=False):
        c = ' far' if far else ''
        g = f'<g transform="rotate({tilt} {a[0]:.1f} {a[1]:.1f})"><rect class="boot{c}" x="{a[0]-7:.1f}" y="{a[1]-8:.1f}" width="14" height="16" rx="3"/>' \
            f'<rect class="wheel{c}" x="{a[0]-2.5:.1f}" y="{a[1]+9:.1f}" width="5" height="14" rx="2.5"/></g>'
        (self.far if far else self.near).append(g)
    def svg(self): return self.far + self.near + self.top

def hl(p, rx=16, ry=8, rot=0):
    return f'<ellipse class="hl" cx="{p[0]:.1f}" cy="{p[1]:.1f}" rx="{rx}" ry="{ry}" transform="rotate({rot} {p[0]:.1f} {p[1]:.1f})"/>'

def arrow(a, b, bend=0):
    if bend:
        m = mid(a, b); dx, dy = b[0] - a[0], b[1] - a[1]; c = (m[0] - dy * bend, m[1] + dx * bend)
        return f'<path class="acc" d="M{a[0]:.1f} {a[1]:.1f}Q{c[0]:.1f} {c[1]:.1f} {b[0]:.1f} {b[1]:.1f}" marker-end="url(#ah)"/>'
    return f'<line class="acc" x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" marker-end="url(#ah)"/>'

def label(x, y, *lines, anchor='start'):
    return ''.join(f'<text class="lbl" x="{x}" y="{y + i * 13}" text-anchor="{anchor}">{t}</text>' for i, t in enumerate(lines))

def vline(x, y0, y1, cls='acc dash'): return f'<line class="{cls}" x1="{x:.1f}" y1="{y0:.1f}" x2="{x:.1f}" y2="{y1:.1f}"/>'
def floor(): return f'<line class="floor" x1="10" y1="{FLOOR}" x2="{W-10}" y2="{FLOOR}"/>'

def head_from(hip, shoulder):
    u = norm(sub(shoulder, hip)); return add(shoulder, mul(u, 15))

def scoped(text):
    """Prefix class names with il- and scope the rules to .illu, so an inlined SVG's styles can't touch the app's."""
    text = re.sub(r'class="([^"]+)"', lambda m: 'class="' + ' '.join('il-' + c for c in m.group(1).split()) + '"', text)
    return re.sub(r'^\.([a-z]+)((?:\.[a-z]+)*)\{', lambda m: '.illu .il-' + m.group(1) + m.group(2).replace('.', '.il-') + '{', text, flags=re.M)

def save(name, title, parts):
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" class="illu" viewBox="0 0 {W} {H}" role="img" aria-label="{title}">\n'
         f'<title>{title}</title>\n' + scoped(STYLE + '\n' + '\n'.join(parts)) + '\n</svg>\n')
    open(os.path.join(OUT, name + '.svg'), 'w').write(s)

def top_skate(cx, cy, ang, far=False):
    """A skate from above. The toe end (toward +x before rotation) is wider, the heel narrower."""
    o = ' style="opacity:.4"' if far else ''
    return (f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({ang})"{o}>'
            '<path class="top" d="M-20 -5Q-24 0 -20 5L14 8Q24 7 24 0Q24 -7 14 -8Z"/>'
            + ''.join(f'<rect class="wtop" x="{x}" y="-1.5" width="7" height="3" rx="1.5"/>' for x in (-17, -7, 3, 13)) + '</g>')

def standing(hip, lean, near, far, arms, skate=None, hip_w=0, sh_w=0):
    """Common upright figure. lean: torso angle from vertical in degrees (+ = forward/right).
    near/far: dict(ankle=, hint=, toe=, knee=). arms: ((hand, hint), (hand, hint)) near then far."""
    F = Fig()
    sh_c = at(hip, -90 + lean, 52)
    hipN, hipF = add(hip, (hip_w, 0)), add(hip, (-hip_w, 0))
    shN, shF = add(sh_c, (sh_w, 0)), add(sh_c, (-sh_w, 0))
    K = {}
    K['knee'] = F.leg(hipN, near['ankle'], near.get('hint', (1, 0)), near.get('toe', 0), False, near.get('skate', skate), near.get('knee'))
    K['knee2'] = F.leg(hipF, far['ankle'], far.get('hint', (1, 0)), far.get('toe', 0), True, far.get('skate', skate), far.get('knee'))
    K['elbow'] = F.arm(shN, arms[0][0], arms[0][1]); K['elbow2'] = F.arm(shF, arms[1][0], arms[1][1], True)
    if hip_w: F.near.insert(0, f'<polyline class="fig" points="{f(hipF)} {f(hipN)}"/>')
    if sh_w: F.near.insert(0, f'<polyline class="fig" points="{f(shF)} {f(shN)}"/>')
    hd = head_from(hip, sh_c); F.body(hip, sh_c, hd)
    K.update(hip=hip, hipN=hipN, hipF=hipF, sh=sh_c, head=hd)
    return F, K

S = SKATE_ANKLE

# ---------------------------------------------------------------- foundations, side view, facing right
F, K = standing((96, 82), 26, dict(ankle=(112, S)), dict(ankle=(102, S)),
                (((150, 72), (0, 1)), ((144, 76), (0, 1))), skate='side')
save('stance', 'Ready stance: knees bent, chest up, weight over the middle of the skates', [floor(), *F.svg(),
     vline(K['knee'][0] + 4, 30, FLOOR), hl(K['knee'], 9, 9),
     label(14, 26, 'nose over knees', 'over toes'), label(14, 150, 'soft knees')])

F, K = standing((112, 78), 14, dict(ankle=(118, S)), dict(ankle=(104, S - 18), hint=(1, 0), toe=5),
                (((146, 76), (0, 1)), ((140, 84), (0, 1))), skate='side')
save('glide1', 'One-foot glide: hips stacked over the gliding skate, free foot lifted', [floor(), *F.svg(),
     vline(K['hip'][0], K['hip'][1], FLOOR), label(14, 26, 'hips stacked over', 'the gliding skate'),
     arrow((22, 150), (64, 150)), label(22, 140, 'glide'), label(150, 120, 'free foot', 'by the ankle')])

F, K = standing((104, 80), 12, dict(ankle=(150, FLOOR - 26), toe=-22, hint=(1, -0.3)), dict(ankle=(92, S), hint=(1, 0)),
                (((146, 66), (0, 1)), ((140, 72), (0, 1))), skate='side')
brake = at((150, FLOOR - 26), 180 - 22, 13)
save('heelstop', 'Heel brake stop: brake foot forward, toes lifted, heel brake pressing the ground', [floor(), *F.svg(),
     f'<rect class="pad" x="{brake[0]-6:.1f}" y="{FLOOR-9}" width="10" height="9" rx="2"/>', hl((brake[0] - 1, FLOOR - 5), 14, 9),
     label(14, 26, 'scissor the brake', 'foot forward'), label(160, 104, 'lift toes,', 'press heel')])

F, K = standing((100, 112), 30, dict(ankle=(100, S), hint=(1, 0)), dict(ankle=(176, S - 32), skate='side', toe=-8, hint=(0, -1)),
                (((150, 92), (0, 1)), ((146, 98), (0, 1))), skate='side')
save('shootduck', 'Shoot the duck: glide on one deeply bent leg, the other straight out in front', [floor(), *F.svg(),
     hl(mid(K['hip'], K['knee']), 18, 8, 10), label(14, 26, 'sink low on one leg'), label(138, 26, 'other leg straight,', 'heel up')])

# ---------------------------------------------------------------- foundations, front view
F, K = standing((126, 80), -6, dict(ankle=(128, S), hint=(1, 0), skate='front'), dict(ankle=(64, S + 6), hint=(-0.2, -1), skate='front', toe=-25),
                (((150, 72), (1, 0.4)), ((92, 72), (-1, 0.4))), hip_w=9, sh_w=14)
save('stride', 'Forward stride from the front: push out to the side, then bring the foot back under you', [floor(), *F.svg(),
     arrow((88, 104), (52, 112)), label(14, 26, 'push out', 'to the side'),
     arrow((60, 128), (114, 156), 0.35), label(150, 26, 'then recover', 'under your hips')])

F, K = standing((150, 104), -10, dict(ankle=(160, SHOE_ANKLE), hint=(1, 0)), dict(ankle=(64, SHOE_ANKLE), hint=(0, -1), toe=180),
                (((138, 82), (1, 0.6)), ((138, 82), (-1, 0.6))), hip_w=9, sh_w=14)
lateral = [floor(), *F.svg(), hl(mid(K['hipF'], (64, SHOE_ANKLE)), 26, 7, -27)]
save('lateral', 'Lateral lunge from the front: sit back into one bent leg, the other straight', lateral +
     [label(14, 26, 'straight leg,', 'toes forward'), label(230, 26, 'sit into', 'this knee', anchor='end')])

# ---------------------------------------------------------------- from above
save('tstop', 'T-stop from above: the back skate drags at a right angle behind the glide skate', [
     label(14, 26, 'seen from above'), top_skate(130, 76, 0), top_skate(106, 102, 90),
     arrow((40, 76), (92, 76)), label(40, 66, 'glide'), hl((106, 104), 11, 23),
     label(14, 150, 'back skate at 90°,'), label(14, 163, 'drag behind the heel')])

save('plow', 'Plow stop from above: skates in a wide V, heels pushing out', [
     label(14, 26, 'seen from above'), top_skate(100, 92, -62), top_skate(140, 92, -118),
     arrow((120, 46), (120, 24)), label(128, 34, 'travel'),
     arrow((86, 126), (60, 146)), arrow((154, 126), (180, 146)), label(120, 168, 'heels push out', anchor='middle')])

save('swizzle', 'Forward swizzles from above: start heels together, push the skates apart, then squeeze them back in', [
     label(14, 26, 'seen from above'), '<path class="acc dash" d="M108 166C68 132 68 70 108 34"/>', '<path class="acc dash" d="M132 166C172 132 172 70 132 34"/>',
     top_skate(100, 146, -118, True), top_skate(140, 146, -62, True), top_skate(80, 100, -90), top_skate(160, 100, -90),
     top_skate(100, 54, -62, True), top_skate(140, 54, -118, True),
     label(14, 146, 'heels in,', 'toes out'), label(14, 104, 'push out'), label(14, 50, 'squeeze in'), arrow((214, 150), (214, 60)), label(206, 166, 'travel')])

# ---------------------------------------------------------------- off-skate
F, K = standing((84, 112), 40, dict(ankle=(112, SHOE_ANKLE)), dict(ankle=(106, SHOE_ANKLE)),
                (((156, 80), (0, 1)), ((150, 84), (0, 1))))
save('squat', 'Bodyweight squat: hips back and down, chest up, knees over toes', [floor(), *F.svg(),
     hl(mid(K['hip'], K['knee']), 18, 8, -15), arrow((60, 70), (60, 104)), label(14, 26, 'hips back', 'and down'), label(150, 26, 'chest up')])

F, K = standing((62, 110), 0, dict(ankle=(104, SHOE_ANKLE)), dict(ankle=(100, SHOE_ANKLE)),
                (((76, 110), (1, 0)), ((72, 110), (1, 0))))
save('wallsit', 'Wall sit: back flat on the wall, thighs near parallel to the floor', [floor(),
     f'<line class="wall" x1="{K["hip"][0]-6:.1f}" y1="16" x2="{K["hip"][0]-6:.1f}" y2="{FLOOR}"/>', *F.svg(),
     hl(mid(K['hip'], K['knee']), 20, 8), label(130, 26, 'thighs near', 'parallel'), label(130, 66, 'hold 45 s')])

F, K = standing((120, 84), 0, dict(ankle=(122, SHOE_ANKLE)), dict(ankle=(96, 122), hint=(1, 0), toe=10),
                (((72, 84), (0, 1)), ((168, 84), (0, 1))))
save('balance', 'Single-leg balance: soft standing knee, hips level', [floor(), *F.svg(),
     f'<line class="acc dash" x1="86" y1="{K["hip"][1]:.1f}" x2="156" y2="{K["hip"][1]:.1f}"/>', label(162, 88, 'hips level'),
     label(14, 26, '30 s each side,', 'then eyes closed')])

# ---------------------------------------------------------------- hip & hamstring routine (one panel per step)
F = Fig()
hip = (112, 104); sh = at(hip, -90, 52)
F.leg(hip, (152, SHOE_ANKLE), (1, -1))                                   # front leg, knee at about 90°
F.line([hip, (92, FLOOR - 6), (52, FLOOR - 6), (44, FLOOR - 4)], True)  # back knee on the floor, shin flat
F.arm(sh, (142, 110), (1, 0)); F.arm(sh, (140, 112), (1, 0), True)
F.body(hip, sh, head_from(hip, sh))
save('stretch-1', 'Kneeling hip flexor stretch: back knee down, hips tucked and shifted forward', [floor(), *F.svg(),
     hl(mid(hip, (92, FLOOR - 6)), 18, 8, 63), arrow((118, 88), (140, 88)), label(14, 26, 'tuck the hips under,', 'shift forward')])

F = Fig()
hip = (124, FLOOR - 6); sh = (72, FLOOR - 6)
F.line([hip, (166, FLOOR - 6), (208, FLOOR - 6), (214, FLOOR - 16)], True)       # far leg flat on the floor
F.line([hip, at(hip, -80, 84), at(at(hip, -80, 84), -10, 12)])                   # near leg straight up
foot = at(hip, -80, 84)
hand = (108, 120); F.arm(sh, hand, (0, 1)); F.arm(sh, add(hand, (-4, 2)), (0, 1), True)
F.body(hip, sh, (56, FLOOR - 10))
save('stretch-2', 'Hamstring stretch on your back: straight leg raised, towel looped round the foot', [floor(), *F.svg(),
     f'<path class="prop" d="M{f(hand)}L{foot[0]+2:.1f} {foot[1]-3:.1f}"/>', hl(mid(hip, foot), 22, 7, -80),
     label(14, 26, 'keep the raised leg', 'straight'), label(160, 66, 'towel or', 'strap')])

F = Fig()
hipN, hipF = (132, FLOOR - 8), (108, FLOOR - 8); sh = (120, FLOOR - 58)
kN, kF = (172, FLOOR - 22), (68, FLOOR - 22); feet = (120, FLOOR - 6)
F.line([hipF, hipN]); F.line([hipN, kN, (124, FLOOR - 6)]); F.line([hipF, kF, (116, FLOOR - 6)], True)
F.line([(106, sh[1]), (134, sh[1])]); F.arm((134, sh[1]), (125, FLOOR - 8), (1, 0)); F.arm((106, sh[1]), (115, FLOOR - 8), (-1, 0), True)
F.body((120, FLOOR - 8), sh, (120, sh[1] - 15))
save('stretch-3', 'Butterfly stretch from the front: soles together, knees out, back tall', [floor(), *F.svg(),
     hl(mid(hipN, kN), 18, 6, -20), hl(mid(hipF, kF), 18, 6, 20), arrow((120, 20), (120, 32)),
     label(14, 26, 'tall back,', 'lean from the hips'), label(160, 26, 'knees fall', 'outward')])

F, K = standing((150, 104), -10, dict(ankle=(160, SHOE_ANKLE)), dict(ankle=(64, SHOE_ANKLE - 4), hint=(0, -1), toe=-80),
                (((138, 82), (1, 0.6)), ((138, 82), (-1, 0.6))), hip_w=9, sh_w=14)
save('stretch-4', 'Side lunge hold from the front: stretch along the inside of the straight leg', [floor(), *F.svg(),
     hl(mid(K['hipF'], (64, SHOE_ANKLE)), 26, 7, -27), label(14, 26, 'straight leg,', 'toes up'), label(230, 26, 'sit back', 'into this knee', anchor='end')])

F = Fig()
hip = (120, FLOOR - 6); sh = (74, FLOOR - 6)
kF = (150, FLOOR - 44); F.line([hip, kF, (176, FLOOR - 6), (186, FLOOR - 6)], True)   # far foot on the floor
kN = (140, FLOOR - 78); aN = (162, FLOOR - 50)                                         # near ankle crossed over the far knee
F.line([hip, kN]); F.line([kN, (154, FLOOR - 44), (164, FLOOR - 46)])
F.arm(sh, (116, FLOOR - 30), (0, 1)); F.arm(sh, (112, FLOOR - 28), (0, 1), True)
F.body(hip, sh, (58, FLOOR - 10))
save('stretch-5', 'Figure-4 stretch on your back: ankle crossed over the other knee, thigh pulled toward the chest', [floor(), *F.svg(),
     hl(hip, 16, 10), arrow((182, 90), (160, 80), 0.3), label(14, 26, 'ankle over the', 'other knee'), label(172, 70, 'pull in')])

print('wrote', len([n for n in os.listdir(OUT) if n.endswith('.svg')]), 'illustrations')
