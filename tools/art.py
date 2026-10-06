"""Isometric technical line-art generator for SIGMA site illustrations.

Run: python3 tools/art.py   (writes src/art/*.svg; no dependencies)

Every drawing is built from convex solids (boxes, tapered ingots, cylinders)
and drawn back-to-front. Faces are filled with CSS classes so one drawing
adapts to light or dark sections:
  .t top face   .l left face   .r right face   .m molten accent   .k plain stroke
"""
from math import cos, sin, pi, sqrt
from pathlib import Path

C30, S30 = cos(pi / 6), 0.5
OUT = Path(__file__).resolve().parent.parent / 'src' / 'art'


def proj(p):
    x, y, z = p
    return ((x - y) * C30, (x + y) * S30 - z)


def fmt(points):
    return ' '.join(f'{x:.1f},{y:.1f}' for x, y in points)


class Drawing:
    def __init__(self):
        self.items = []  # (depth, svg)

    def poly(self, pts3, cls, depth=None):
        pts = [proj(p) for p in pts3]
        d = depth if depth is not None else sum(sum(p) for p in pts3) / len(pts3)
        self.items.append((d, f'<polygon class="{cls}" points="{fmt(pts)}"/>'))

    def line(self, pts3, cls='k', depth=None):
        pts = [proj(p) for p in pts3]
        d = depth if depth is not None else sum(sum(p) for p in pts3) / len(pts3) + 0.01
        self.items.append((d, f'<polyline class="{cls}" points="{fmt(pts)}"/>'))

    def raw(self, svg, depth):
        self.items.append((depth, svg))

    # Convex solid from bottom and top rectangles (allows tapered ingots).
    def solid(self, bottom, top, groove=0):
        b, t = bottom, top
        base = key_of(b)
        faces = [
            ([b[1], b[2], t[2], t[1]], 'r', (1, 0, 0)),
            ([b[3], b[2], t[2], t[3]], 'l', (0, 1, 0)),
            (t, 't', (0, 0, 1)),
        ]
        for i, (face, cls, _) in enumerate(faces):
            self.poly(face, cls, depth=base + 0.001 * i)
        if groove:
            # grooves across the top face, parallel to the short edge
            for k in range(1, groove + 1):
                f = k / (groove + 1)
                a = lerp(t[0], t[1], f)
                c = lerp(t[3], t[2], f)
                self.line([a, c], 'k', depth=base + 0.01)

    def box(self, x, y, z, w, d, h, taper=0, groove=0):
        bottom = [(x, y, z), (x + w, y, z), (x + w, y + d, z), (x, y + d, z)]
        top = [(x + taper, y + taper, z + h), (x + w - taper, y + taper, z + h),
               (x + w - taper, y + d - taper, z + h), (x + taper, y + d - taper, z + h)]
        self.solid(bottom, top, groove)

    def cylinder(self, c, r, h, axis='z', cap='t', molten=False, rings=(), lip=0, key=None):
        """Cylinder whose near cap is visible. axis in {'x','y','z'}."""
        u, v, a = {'z': ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
                   'x': ((0, 1, 0), (0, 0, 1), (1, 0, 0)),
                   'y': ((1, 0, 0), (0, 0, 1), (0, 1, 0))}[axis]
        n = 72

        def circle(center, rad):
            return [tuple(center[i] + rad * (cos(2 * pi * k / n) * u[i] + sin(2 * pi * k / n) * v[i])
                          for i in range(3)) for k in range(n)]
        far = c
        near = tuple(c[i] + h * a[i] for i in range(3))
        pts = [proj(p) for p in circle(far, r) + circle(near, r)]
        hull = convex_hull(pts)
        depth = key if key is not None else c[2] * 1000 + c[0] + c[1]
        self.raw(f'<polygon class="l" points="{fmt(hull)}"/>', depth)
        self.raw(f'<polygon class="{cap}" points="{fmt([proj(p) for p in circle(near, r)])}"/>', depth + 0.002)
        for rr in rings:
            self.raw(f'<polygon class="k" points="{fmt([proj(p) for p in circle(near, rr)])}"/>', depth + 0.003)
        if molten:
            self.raw(f'<polygon class="m" points="{fmt([proj(p) for p in circle(near, r - lip)])}"/>', depth + 0.004)


def key_of(bottom):
    z = min(p[2] for p in bottom)
    cx = sum(p[0] for p in bottom) / len(bottom)
    cy = sum(p[1] for p in bottom) / len(bottom)
    return z * 1000 + cx + cy


def lerp(p, q, f):
    return tuple(p[i] + (q[i] - p[i]) * f for i in range(3))


def convex_hull(points):
    pts = sorted(set((round(x, 2), round(y, 2)) for x, y in points))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def render(drawing, name, label, pad=14, extra=''):
    import re
    coords = []
    for _, svg in drawing.items:
        for pair in re.findall(r'(-?[\d.]+),(-?[\d.]+)', svg):
            coords.append((float(pair[0]), float(pair[1])))
    xs, ys = [c[0] for c in coords], [c[1] for c in coords]
    minx, miny = min(xs) - pad, min(ys) - pad
    w, h = max(xs) - min(xs) + 2 * pad, max(ys) - min(ys) + 2 * pad
    body = '\n'.join(svg for _, svg in sorted(drawing.items, key=lambda i: i[0]))
    svg = (f'<svg class="art" viewBox="{minx:.0f} {miny:.0f} {w:.0f} {h:.0f}" role="img" aria-label="{label}" '
           f'xmlns="http://www.w3.org/2000/svg">\n{body}{extra}\n</svg>\n')
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f'{name}.svg').write_text(svg)


def ingot_bundle(d, ox=0, oy=0, oz=0, layers=4):
    """Classic cross-stacked aluminium ingot bundle."""
    L, W, H, t = 132, 26, 16, 4
    for layer in range(layers):
        z = oz + layer * H
        for i in range(4):
            if layer % 2 == 0:
                d.box(ox + i * (W + 6), oy, z, W, L, H, taper=t, groove=2)
            else:
                d.box(ox, oy + i * (W + 6), z, L, W, H, taper=t, groove=2)


def art_ingots():
    d = Drawing()
    ingot_bundle(d)
    render(d, 'ingots', '交錯堆疊的鋁合金錠線稿')


def art_zinc():
    d = Drawing()
    L, W, H = 78, 30, 12
    for layer in range(3):
        for i in range(3):
            if layer % 2 == 0:
                d.box(i * (W + 4), 0, layer * H, W, L, H, taper=3, groove=3)
            else:
                d.box(0, i * (W + 4), layer * H, L, W, H, taper=3, groove=3)
    d.box(130, 10, 0, W, L, H, taper=3, groove=3)
    render(d, 'zinc', '鋅合金錠線稿')


def art_slab():
    d = Drawing()
    d.box(0, 0, 0, 70, 250, 34)
    d.box(10, 10, 34, 50, 230, 2)
    d.cylinder((120, 120, 46), 46, 92, axis='x', cap='t', rings=(32, 22, 14))
    render(d, 'slab', '軋製扁錠與鋁卷線稿')


def art_ladle():
    d = Drawing()
    d.box(-30, -30, 0, 200, 140, 10)
    d.cylinder((60, 40, 10), 58, 110, axis='z', cap='t', molten=True, lip=7)
    d.cylinder((-6, 40, 82), 9, 16, axis='x', cap='t', key=0)
    d.cylinder((118, 40, 82), 9, 16, axis='x', cap='t', key=1e9)
    render(d, 'ladle', '盛裝鋁液的保溫鋁湯包線稿')


def art_casting():
    d = Drawing()
    d.box(0, 0, 0, 150, 110, 18)
    d.box(0, 0, 18, 40, 110, 70)
    d.box(40, 50, 18, 110, 10, 40)
    for cx, cy in ((95, 22), (95, 88), (130, 22), (130, 88)):
        d.cylinder((cx, cy, 18), 9, 4, axis='z', cap='m')
    d.cylinder((-4, 55, 52), 20, 4, axis='x', cap='t', rings=(10,))
    render(d, 'casting', '鋁合金鑄件線稿')


def art_furnace():
    d = Drawing()
    d.box(0, 0, 0, 170, 120, 70)
    d.box(10, 10, 70, 150, 100, 22, taper=10)
    d.cylinder((120, 30, 92), 14, 90, axis='z', cap='t', rings=(9,))
    # charging door on the left (y-facing) face
    y = 120
    d.line([(30, y, 12), (30, y, 52), (90, y, 52), (90, y, 12), (30, y, 12)], 'k', depth=10_000_000)
    d.line([(30, y, 22), (90, y, 22)], 'm-line', depth=10_000_000)
    render(d, 'furnace', '熔煉爐線稿')


def art_bale():
    d = Drawing()
    for x, y in ((0, 0), (0, 110), (110, 0), (110, 110)):
        d.box(x, y, 0, 96, 96, 80)
        k0 = x + 48 + y + 48 + 0.5
        for k in (0.3, 0.7):
            z = 80 * k
            d.line([(x + 96, y, z), (x + 96, y + 96, z), (x, y + 96, z)], 'k', depth=k0)
        d.line([(x + 30, y + 8, 80), (x + 48, y + 40, 80), (x + 38, y + 70, 80), (x + 70, y + 86, 80)], 'k', depth=k0)
    render(d, 'bale', '打包廢鋁原料線稿')


def art_lab():
    d = Drawing()
    d.box(0, 0, 0, 160, 90, 64)
    d.box(20, 0, 64, 70, 60, 46)
    x = 90
    d.line([(x, 8, 76), (x, 8, 100), (x, 52, 100), (x, 52, 76), (x, 8, 76)], 'k', depth=10_000_000)
    d.cylinder((126, 40, 64), 16, 10, axis='z', cap='m')
    d.line([(18, 90, 12), (18, 90, 50), (66, 90, 50), (66, 90, 12), (18, 90, 12)], 'k', depth=10_000_000)
    render(d, 'lab', '光譜分析檢驗設備線稿')


def art_cycle():
    d = Drawing()
    n, r = 96, 120
    ring = [(r * cos(2 * pi * k / n), r * sin(2 * pi * k / n), 0) for k in range(n)]
    for start in (0, 32, 64):
        seg = ring[start + 3:start + 30]
        d.line(seg, 'k cycle', depth=-1000)
        tip = ring[start + 30]
        back = ring[start + 26]
        side = (tip[0] - back[0], tip[1] - back[1])
        ortho = (-side[1] * 0.6, side[0] * 0.6)
        d.poly([tip, (back[0] + ortho[0], back[1] + ortho[1], 0), (back[0] - ortho[0], back[1] - ortho[1], 0)], 'm', depth=-999)
    d.box(-60, -18, 0, 30, 70, 12, taper=3, groove=1)
    d.box(10, -40, 0, 40, 40, 34)
    d.cylinder((-10, 40, 0), 22, 34, axis='z', cap='t', molten=True, lip=4)
    render(d, 'cycle', '回收、熔煉、再製造的循環線稿')


def art_map():
    d = Drawing()
    g = 40
    for i in range(7):
        d.line([(i * g, 0, 0), (i * g, 6 * g, 0)], 'k grid', depth=-1000)
        d.line([(0, i * g, 0), (6 * g, i * g, 0)], 'k grid', depth=-1000)
    for (x, y, h, hot) in ((40, 60, 70, True), (150, 40, 50, False), (200, 150, 46, False),
                           (90, 190, 56, False), (180, 220, 40, False), (60, 130, 36, False)):
        d.line([(x, y, 0), (x, y, h)], 'k', depth=x + y)
        d.cylinder((x, y, h), 9 if hot else 6, 3, axis='z', cap='m' if hot else 't', key=x + y + 0.1)
    render(d, 'map', '生產基地網絡示意線稿')


def art_hero():
    d = Drawing()
    ingot_bundle(d, 0, 0, 0, layers=5)
    d.cylinder((250, -40, 0), 56, 120, axis='z', cap='t', molten=True, lip=7, key=-1)
    render(d, 'hero', '鋁錠、鋁湯包與扁錠組成的工業線稿')


if __name__ == '__main__':
    for fn in (art_ingots, art_zinc, art_slab, art_ladle, art_casting, art_furnace,
               art_bale, art_lab, art_cycle, art_map, art_hero):
        fn()
    print('Wrote', len(list(OUT.glob('*.svg'))), 'illustrations to', OUT)
