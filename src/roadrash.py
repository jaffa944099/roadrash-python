"""
Road Rash 3D — Authentic retro pseudo-3D racer.

All bikes/riders drawn programmatically every frame with:
  • Animated spinning wheels with spokes
  • Rider body that leans and bobs with suspension
  • Arms gripping handlebars
  • Working headlight and tail-light
  • Dynamic exhaust flames at high speed
  • Smooth curves, hills, roadside scenery
"""
import sys, os, math, random, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pygame

W, H    = 800, 600
FPS     = 60
ROAD_W  = 2000
SEG_L   = 200
N_SEG   = 300
DRAW_D  = 150
CAM_D   = 0.84
HOR     = int(H * 0.38)


def fog(c, f):
    return tuple(max(0, min(255, int(c[i] + f * (175 - c[i])))) for i in range(3))


# ═══════════════════════════════════════════════════════════════════════════════
# ANIMATED BIKE RENDERER — draws everything in real-time each frame
# ═══════════════════════════════════════════════════════════════════════════════
def draw_bike(surf, cx, by, scale, lean, wheel_angle, speed_ratio,
              body_col=(30, 100, 220), is_player=True):
    """Draw a fully animated motorbike + rider at (cx, by) with given scale."""
    if scale < 0.06:
        return
    s = scale

    # ── Lean offset ──
    lx = int(lean * 22 * s)

    # ── Shadow ──
    sw = int(65 * s)
    sh_s = pygame.Surface((sw * 2, int(sw * 0.4)), pygame.SRCALPHA)
    pygame.draw.ellipse(sh_s, (0, 0, 0, 50), sh_s.get_rect())
    surf.blit(sh_s, (cx - sw + lx // 2, by + int(3 * s)))

    # ── Rear Wheel (with spinning spokes) ──
    wr = max(3, int(22 * s))
    wcx, wcy = cx + lx, by
    pygame.draw.circle(surf, (30, 30, 30), (wcx, wcy), wr)           # tyre
    pygame.draw.circle(surf, (50, 50, 50), (wcx, wcy), max(2, wr - int(4 * s)))  # inner
    # spokes (animated!)
    n_spokes = 6
    for sp in range(n_spokes):
        a = wheel_angle + sp * (2 * math.pi / n_spokes)
        dx = int(math.cos(a) * (wr - int(3 * s)))
        dy = int(math.sin(a) * (wr - int(3 * s)))
        pygame.draw.line(surf, (140, 140, 140), (wcx, wcy), (wcx + dx, wcy + dy),
                         max(1, int(1.5 * s)))
    # hub
    pygame.draw.circle(surf, (180, 180, 180), (wcx, wcy), max(1, int(4 * s)))

    # ── Frame / Swing-arm ──
    fa = max(1, int(4 * s))
    frame_top = by - int(40 * s)
    pygame.draw.line(surf, (80, 80, 80), (wcx, wcy), (cx + lx, frame_top), fa)

    # ── Engine block ──
    ew, eh = int(28 * s), int(18 * s)
    engine_y = by - int(18 * s)
    pygame.draw.rect(surf, (60, 60, 70),
                     (cx + lx - ew // 2, engine_y, ew, eh), border_radius=max(1, int(3 * s)))
    # Engine detail lines
    for i in range(3):
        ey = engine_y + int((i + 1) * eh / 4)
        pygame.draw.line(surf, (90, 90, 100),
                         (cx + lx - ew // 2 + int(2 * s), ey),
                         (cx + lx + ew // 2 - int(2 * s), ey), max(1, int(s)))

    # ── Exhaust pipe ──
    ex_x = cx + lx + int(22 * s)
    ex_y = engine_y + eh - int(2 * s)
    pygame.draw.line(surf, (160, 140, 100), (cx + lx + ew // 2, ex_y),
                     (ex_x + int(12 * s), by + int(5 * s)), max(1, int(4 * s)))
    # Exhaust flame at high speed
    if speed_ratio > 0.5 and is_player:
        flame_len = int(10 * s * speed_ratio)
        for fi in range(3):
            fx = ex_x + int(12 * s) + random.randint(0, flame_len)
            fy = by + int(5 * s) + random.randint(-int(3 * s), int(3 * s))
            fr = max(1, int((3 - fi) * s))
            cols = [(255, 100, 20), (255, 180, 30), (255, 220, 80)]
            pygame.draw.circle(surf, cols[fi], (fx, fy), fr)

    # ── Main body / fairing ──
    body_pts = [
        (cx - int(24 * s) + lx, by - int(18 * s)),
        (cx + int(24 * s) + lx, by - int(18 * s)),
        (cx + int(18 * s) + lx, by - int(58 * s)),
        (cx - int(18 * s) + lx, by - int(58 * s)),
    ]
    pygame.draw.polygon(surf, body_col, body_pts)
    # Fairing highlight
    hi_col = tuple(min(255, c + 50) for c in body_col)
    pygame.draw.polygon(surf, hi_col, [
        (body_pts[0][0] + int(4 * s), body_pts[0][1] - int(2 * s)),
        (body_pts[0][0] + int(14 * s), body_pts[0][1] - int(2 * s)),
        (body_pts[3][0] + int(14 * s), body_pts[3][1] + int(2 * s)),
        (body_pts[3][0] + int(4 * s), body_pts[3][1] + int(2 * s)),
    ])

    # ── Tail light ──
    tl_w = max(2, int(16 * s))
    tl_h = max(1, int(5 * s))
    tl_col = (255, 30, 30) if speed_ratio < 0.3 else (255, 80, 80)
    pygame.draw.rect(surf, tl_col,
                     (cx + lx - tl_w // 2, by - int(20 * s), tl_w, tl_h),
                     border_radius=max(1, int(2 * s)))

    # ── Windscreen ──
    ws_pts = [
        (cx - int(13 * s) + lx, by - int(58 * s)),
        (cx + int(13 * s) + lx, by - int(58 * s)),
        (cx + int(9 * s) + lx,  by - int(72 * s)),
        (cx - int(9 * s) + lx,  by - int(72 * s)),
    ]
    ws_s = pygame.Surface((int(30 * s), int(18 * s)), pygame.SRCALPHA)
    ws_s.fill((140, 200, 255, 100))
    surf.blit(ws_s, (cx - int(13 * s) + lx, by - int(72 * s)))
    pygame.draw.polygon(surf, (100, 170, 230), ws_pts, max(1, int(2 * s)))

    # ── Handlebars ──
    hb_y = by - int(68 * s)
    hb_w = int(28 * s)
    pygame.draw.line(surf, (160, 160, 160),
                     (cx - hb_w + lx, hb_y), (cx + hb_w + lx, hb_y),
                     max(1, int(3 * s)))
    # Grips
    for side in [-1, 1]:
        gx = cx + side * hb_w + lx
        pygame.draw.circle(surf, (40, 40, 40), (gx, hb_y), max(1, int(3 * s)))
    # Mirrors
    for side in [-1, 1]:
        mx = cx + side * (hb_w + int(5 * s)) + lx
        my = hb_y - int(5 * s)
        pygame.draw.line(surf, (150, 150, 150), (cx + side * hb_w + lx, hb_y),
                         (mx, my), max(1, int(1.5 * s)))
        pygame.draw.ellipse(surf, (180, 200, 220),
                            (mx - int(3 * s), my - int(2 * s), int(6 * s), int(4 * s)))

    # ── Rider ──
    # Torso
    torso_y = by - int(78 * s)
    torso_h = int(22 * s)
    torso_w = int(24 * s)
    pygame.draw.rect(surf, (40, 40, 45),
                     (cx + lx - torso_w // 2, torso_y, torso_w, torso_h),
                     border_radius=max(1, int(5 * s)))

    # Arms reaching to handlebars
    shoulder_y = torso_y + int(4 * s)
    for side in [-1, 1]:
        sx_arm = cx + side * int(12 * s) + lx
        gx = cx + side * hb_w + lx
        pygame.draw.line(surf, (35, 35, 40), (sx_arm, shoulder_y), (gx, hb_y),
                         max(1, int(4 * s)))

    # Helmet
    hx = cx + lx
    hy = torso_y - int(14 * s)
    hr = max(3, int(16 * s))
    pygame.draw.circle(surf, (40, 40, 40), (hx, hy), hr)  # base
    # Visor
    visor_rect = (hx - int(hr * 0.75), hy - int(hr * 0.3),
                  int(hr * 1.5), int(hr * 0.6))
    pygame.draw.ellipse(surf, (70, 140, 200), visor_rect)
    # Helmet stripe
    stripe_col = body_col  # match bike colour
    pygame.draw.arc(surf, stripe_col,
                    (hx - hr, hy - hr, hr * 2, hr * 2),
                    math.pi * 0.2, math.pi * 0.8, max(1, int(3 * s)))

    # ── Headlight (facing away from us, subtle glow) ──
    if is_player:
        hl_y = by - int(65 * s)
        glow_s = pygame.Surface((int(20 * s), int(10 * s)), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_s, (255, 255, 200, 40), glow_s.get_rect())
        surf.blit(glow_s, (cx + lx - int(10 * s), hl_y))


# ═══════════════════════════════════════════════════════════════════════════════
# SCENERY DRAWING
# ═══════════════════════════════════════════════════════════════════════════════
def draw_tree(s, x, y, sc, f):
    if sc < 0.02: return
    th, tw, cr = max(2, int(70*sc)), max(1, int(12*sc)), max(2, int(38*sc))
    pygame.draw.rect(s, fog((100, 60, 25), f), (x-tw//2, y-th, tw, th))
    pygame.draw.circle(s, fog((15, 110, 15), f), (x, y-th), cr)
    pygame.draw.circle(s, fog((25, 140, 25), f), (x-cr//3, y-th-cr//3), int(cr*0.6))
    pygame.draw.circle(s, fog((20, 125, 20), f), (x+cr//4, y-th+cr//4), int(cr*0.45))


def draw_lamp(s, x, y, sc, f):
    if sc < 0.03: return
    ph, pw = max(4, int(85*sc)), max(1, int(5*sc))
    arm = max(2, int(22*sc))
    pygame.draw.rect(s, fog((150, 150, 160), f), (x-pw//2, y-ph, pw, ph))
    pygame.draw.line(s, fog((150, 150, 160), f), (x, y-ph), (x+arm, y-ph), pw)
    lr = max(2, int(7*sc))
    pygame.draw.circle(s, fog((240, 220, 120), f), (x+arm, y-ph), lr)
    # Glow
    gs = pygame.Surface((lr*4, lr*4), pygame.SRCALPHA)
    pygame.draw.circle(gs, (255, 240, 150, 40), (lr*2, lr*2), lr*2)
    s.blit(gs, (x+arm-lr*2, y-ph-lr*2))


def draw_bldg(s, x, y, sc, f, ci=0):
    if sc < 0.03: return
    bw, bh = max(4, int(130*sc)), max(6, int(200*sc))
    cols = [(65, 45, 85), (85, 55, 105), (55, 65, 45), (70, 55, 45)]
    pygame.draw.rect(s, fog(cols[ci%4], f), (x-bw//2, y-bh, bw, bh))
    # Roof edge
    pygame.draw.line(s, fog((100, 80, 60), f), (x-bw//2, y-bh), (x+bw//2, y-bh),
                     max(1, int(3*sc)))
    # Windows
    wr, wh = max(1, int(11*sc)), max(1, int(14*sc))
    for wx in range(x-bw//2+wr, x+bw//2-wr, wr*3):
        for wy in range(y-bh+wh+int(4*sc), y-wh, wh*3):
            wc = (220, 210, 150) if random.random() > 0.25 else (80, 70, 50)
            pygame.draw.rect(s, fog(wc, f), (wx, wy, wr, wh))


# ═══════════════════════════════════════════════════════════════════════════════
# ROAD
# ═══════════════════════════════════════════════════════════════════════════════
class Seg:
    __slots__ = ('i','c','h','cars','obj')
    def __init__(self, i):
        self.i = i
        t = i / N_SEG
        self.c = math.sin(t * 22) * 0.55 + math.sin(t * 9.5) * 0.3
        self.h = math.sin(t * 16) * 1500 + math.sin(t * 6.2) * 700
        self.cars = []
        self.obj = []


class Road:
    def __init__(self):
        self.s = [Seg(i) for i in range(N_SEG)]
        for i in range(0, N_SEG, 3):
            self.s[i].obj += [(-1, 'T'), (1, 'T')]
        for i in range(5, N_SEG, 7):
            self.s[i].obj.append((random.choice([-1, 1]), 'L'))
        for i in range(10, N_SEG, 14):
            self.s[i].obj.append((random.choice([-1, 1]), 'B'))

    def get(self, i):
        return self.s[i % N_SEG]


# ═══════════════════════════════════════════════════════════════════════════════
# PARTICLES
# ═══════════════════════════════════════════════════════════════════════════════
class Spark:
    def __init__(self, x, y, speed_ratio):
        self.x = x + random.uniform(-15, 15)
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-4, -1) * speed_ratio
        self.life = random.randint(5, 14)
        self.col = random.choice([(255,180,40),(255,130,20),(220,220,220)])
        self.r = random.randint(1, 3)

    def step(self):
        self.x += self.vx; self.y += self.vy; self.vy += 0.18; self.life -= 1

    def draw(self, surf):
        a = max(0, int(220 * self.life / 14))
        ps = pygame.Surface((self.r*2+2, self.r*2+2), pygame.SRCALPHA)
        pygame.draw.circle(ps, (*self.col, a), (self.r+1, self.r+1), self.r)
        surf.blit(ps, (int(self.x)-self.r-1, int(self.y)-self.r-1))


# ═══════════════════════════════════════════════════════════════════════════════
# GAME
# ═══════════════════════════════════════════════════════════════════════════════
class Game:
    def __init__(self):
        pygame.init()
        self.scr = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Road Rash 3D")
        self.clk = pygame.time.Clock()
        self.fxl = pygame.font.SysFont(None, 52, bold=True)
        self.flg = pygame.font.SysFont(None, 36, bold=True)
        self.fmd = pygame.font.SysFont(None, 26, bold=True)
        self.fsm = pygame.font.SysFont(None, 20)
        self.road = Road()
        self.sparks = []
        self.clouds = [(random.randint(0, W), random.randint(8, HOR - 30),
                        random.randint(60, 160)) for _ in range(10)]
        self.wheel_angle = 0.0
        self.reset()

    def reset(self):
        self.pos = 0.0
        self.spd = 0.0
        self.mspd = SEG_L / FPS * 9
        self.px = 0.0
        self.lean = 0.0
        self.score = 0
        self.go = False
        self.dead = False
        self.t0 = 0.0
        self.bob = 0.0
        self.sparks = []
        for seg in self.road.s:
            seg.cars = []
        # Spawn 30 enemy bikers spread across the track
        for _ in range(30):
            si = random.randint(8, N_SEG - 1)
            self.road.s[si].cars.append({
                'lane': random.uniform(-0.65, 0.65),
                'col': random.choice([(200,40,40),(40,180,40),(220,160,30),(180,40,180),(40,180,180)]),
            })

    def run(self):
        while True:
            dt = self.clk.tick(FPS) / 1000.0
            if not self.go:
                self.pos = (self.pos + self.mspd * 0.35 * dt) % (N_SEG * SEG_L)
                self.wheel_angle += 3.0 * dt  # slow spin on title
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: pygame.quit(); return
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE: pygame.quit(); return
                    if ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if not self.go or self.dead:
                            self.reset()
                            self.go = True
                            self.t0 = time.time()
            if self.go and not self.dead:
                self._upd(dt)
            self._drw()
            pygame.display.flip()

    def _upd(self, dt):
        k = pygame.key.get_pressed()
        a = self.mspd * dt
        if k[pygame.K_UP] or k[pygame.K_w]:
            self.spd = min(self.spd + a * 1.5, self.mspd)
        elif k[pygame.K_DOWN] or k[pygame.K_s]:
            self.spd = max(self.spd - a * 3.0, 0)
        else:
            self.spd = max(self.spd - a * 0.5, 0)

        st = 0
        if k[pygame.K_LEFT] or k[pygame.K_a]: st = -1
        if k[pygame.K_RIGHT] or k[pygame.K_d]: st = 1

        sr = self.spd / max(self.mspd, 0.01)
        self.lean = self.lean * 0.72 + st * sr * 0.28
        self.px = max(-0.95, min(0.95, self.px + st * dt * 2.2 * (sr + 0.15)))
        if abs(self.px) > 0.85:
            self.spd *= 0.92

        self.pos = (self.pos + self.spd * dt) % (N_SEG * SEG_L)
        self.score = int((time.time() - self.t0) * 12 * sr)
        self.bob += self.spd * dt * 9
        self.wheel_angle += self.spd * dt * 18  # fast spin!

        # Sparks
        if sr > 0.4 and random.random() < sr * 0.5:
            bx = W // 2 + int(self.lean * 50)
            self.sparks.append(Spark(bx, H - 40, sr))
        self.sparks = [s for s in self.sparks if s.life > 0]
        for s in self.sparks:
            s.step()

        # Collision
        si = int(self.pos / SEG_L) % N_SEG
        for d in range(-1, 4):
            for car in self.road.get(si + d).cars:
                if abs(car['lane'] - self.px) < 0.2 and abs(d) <= 1:
                    self.dead = True
                    self.go = False

    def _drw(self):
        scr = self.scr
        scr.fill((5, 5, 15))

        # ── Sky gradient ──
        for y in range(HOR + 10):
            t = y / (HOR + 10)
            scr.fill((int(8 + t * 75), int(25 + t * 115), int(80 + t * 140)), (0, y, W, 1))

        # Clouds
        for cx, cy, cr in self.clouds:
            cs = pygame.Surface((cr * 2, int(cr * 0.55)), pygame.SRCALPHA)
            pygame.draw.ellipse(cs, (255, 255, 255, 90), cs.get_rect())
            scr.blit(cs, (cx - cr, cy))

        # Hills
        pts = [(0, HOR + 25)]
        for x in range(0, W + 20, 16):
            pts.append((x, HOR - int(18 * math.sin(x / 65 + self.pos * 0.00015))))
        pts.append((W, HOR + 25))
        pygame.draw.polygon(scr, (18, 85, 18), pts)

        # Fill below horizon with grass
        pygame.draw.rect(scr, (20, 90, 20), (0, HOR, W, H - HOR))

        # ── Road projection ──
        cz = self.pos
        si0 = int(cz / SEG_L) % N_SEG
        cam_x = self.px * ROAD_W
        sr = self.spd / max(self.mspd, 0.01)

        plx = prx = psy = None
        sprites = []
        cc = ch = 0.0

        for i in range(DRAW_D, 0, -1):
            si = (si0 + i) % N_SEG
            seg = self.road.get(si)
            cc += seg.c
            ch += seg.h
            f = min(1.0, (i / (DRAW_D * 0.85))) ** 1.1

            wz = (si - si0) * SEG_L
            if wz <= 0: wz += N_SEG * SEG_L
            if wz < 1: continue

            sc = CAM_D / wz * SEG_L
            sx = int(W / 2 + sc * (cam_x - cc * 280) * W / ROAD_W)
            sy = int(H / 2 - sc * (1500 + ch))
            sw = int(sc * ROAD_W * W / ROAD_W)

            if sy < HOR - 20 or sy > H + 20:
                continue

            alt = si % 2 == 0
            gc = fog((20, 90, 20) if alt else (30, 120, 30), f)
            rc = fog((44, 44, 44) if alt else (62, 62, 62), f)
            kc = fog((220, 30, 30) if alt else (230, 230, 230), f)

            if psy is not None and sy < psy:
                iy = int(psy)
                cy_n = int(sy)
                lx, rx = sx - sw, sx + sw

                # Grass
                pygame.draw.rect(scr, gc, (0, cy_n, W, iy - cy_n))
                # Road
                pygame.draw.polygon(scr, rc,
                    [(plx, iy), (prx, iy), (rx, cy_n), (lx, cy_n)])
                # Kerbs
                kw = max(1, sw // 10)
                pygame.draw.polygon(scr, kc,
                    [(plx, iy), (plx - kw, iy), (lx - kw, cy_n), (lx, cy_n)])
                pygame.draw.polygon(scr, kc,
                    [(prx, iy), (prx + kw, iy), (rx + kw, cy_n), (rx, cy_n)])
                # Dashes
                if alt and sw > 8:
                    dw = max(1, sw // 25)
                    wc = fog((255, 255, 255), f)
                    pygame.draw.polygon(scr, wc,
                        [(sx-dw, iy), (sx+dw, iy), (sx+dw, cy_n), (sx-dw, cy_n)])

                # Guard rails
                rlw = max(1, int(2.5 * sc * 2000))
                rl_col = fog((160, 160, 170), f)
                for side in [-1, 1]:
                    bx = sx + side * (sw + int(5 * sc * 2000))
                    pygame.draw.line(scr, rl_col, (bx, iy), (bx, cy_n), rlw)

                # Scenery
                os_ = sc * 2000
                for side, ot in seg.obj:
                    ox = sx + side * (sw + int(40 * os_))
                    oy = cy_n
                    if ot == 'T':   sprites.append((oy, 'T', ox, oy, os_, f))
                    elif ot == 'L': sprites.append((oy, 'L', ox, oy, os_, f))
                    elif ot == 'B': sprites.append((oy, 'B', ox, oy, os_, f, si % 4))

                # Enemy bikers!
                for car in seg.cars:
                    esx = sx + int(car['lane'] * sw)
                    e_scale = sc * 2000
                    if e_scale > 0.03:
                        sprites.append((cy_n, 'E', esx, cy_n, e_scale, car['col']))

            plx, prx, psy = sx - sw, sx + sw, sy

        # ── Draw sprites back-to-front ──
        sprites.sort(key=lambda x: x[0])
        for item in sprites:
            k = item[1]
            if k == 'T':
                draw_tree(scr, item[2], item[3], item[4], item[5])
            elif k == 'L':
                draw_lamp(scr, item[2], item[3], item[4], item[5])
            elif k == 'B':
                draw_bldg(scr, item[2], item[3], item[4], item[5], item[6])
            elif k == 'E':
                ex, ey, e_sc, e_col = item[2], item[3], item[4], item[5]
                # Enemy bike with spinning wheels too
                e_lean = math.sin(self.pos * 0.01 + ex * 0.1) * 0.3
                draw_bike(scr, ex, ey, e_sc * 0.8, e_lean,
                          self.wheel_angle * 0.7, sr * 0.6,
                          body_col=e_col, is_player=False)

        # ── Sparks ──
        for sp in self.sparks:
            sp.draw(scr)

        # ── Player bike (animated!) ──
        bob_y = int(math.sin(self.bob) * 3.5 * sr)
        px_scr = W // 2 + int(self.lean * 60)
        draw_bike(scr, px_scr, H - 55 + bob_y, 1.0,
                  self.lean, self.wheel_angle, sr,
                  body_col=(30, 100, 220), is_player=True)

        # ── Speed lines at high speed ──
        if sr > 0.6:
            for _ in range(int(sr * 8)):
                lx = random.randint(0, W)
                ly = random.randint(HOR, H)
                ll = int(sr * 30)
                la = int(60 * (sr - 0.6) / 0.4)
                ls = pygame.Surface((2, ll), pygame.SRCALPHA)
                ls.fill((255, 255, 255, la))
                scr.blit(ls, (lx, ly))

        # ── HUD ──
        hud = pygame.Surface((W, 48), pygame.SRCALPHA)
        hud.fill((10, 10, 30, 180))
        scr.blit(hud, (0, 0))
        kmh = int(sr * 220)
        scr.blit(self.fmd.render(f"Speed: {kmh} km/h", True, (255, 220, 50)), (12, 13))
        scr.blit(self.fmd.render(f"Score: {self.score}", True, (255, 255, 255)), (W - 200, 13))
        bw = int(sr * 200)
        pygame.draw.rect(scr, (40, 40, 40), (W//2-100, 16, 200, 16), border_radius=8)
        bc = (50, 220, 50) if sr < 0.6 else (255, 180, 0) if sr < 0.85 else (255, 60, 60)
        if bw > 0:
            pygame.draw.rect(scr, bc, (W//2-100, 16, bw, 16), border_radius=8)
        pygame.draw.rect(scr, (180, 180, 180), (W//2-100, 16, 200, 16), 1, border_radius=8)
        scr.blit(self.fsm.render("↑↓ Speed  ←→ Steer  ENTER/SPACE Start  ESC Quit",
                                 True, (140, 140, 140)), (W//2 - 195, H - 20))

        # ── Overlays ──
        if not self.go and not self.dead:
            ov = pygame.Surface((W, H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 90))
            scr.blit(ov, (0, 0))
            for txt, y, col, fn in [
                ("ROAD RASH 3D",                 H//2 - 100, (230, 50, 50),  self.fxl),
                ("Dodge enemy bikers!",           H//2 - 45,  (220, 220, 220), self.fmd),
                ("Press ENTER or SPACE to Race",  H//2 + 5,   (255, 220, 50), self.flg),
                ("ESC to Quit",                   H//2 + 60,  (150, 150, 150), self.fsm),
            ]:
                ts = fn.render(txt, True, col)
                scr.blit(ts, (W//2 - ts.get_width()//2, y))

        elif self.dead:
            ov = pygame.Surface((W, H), pygame.SRCALPHA)
            ov.fill((100, 0, 0, 110))
            scr.blit(ov, (0, 0))
            for txt, y, col, fn in [
                ("CRASHED!",                      H//2 - 80, (255, 80, 80),  self.fxl),
                (f"Score: {self.score}",           H//2 - 10, (255, 255, 255), self.flg),
                ("Press ENTER or SPACE to Retry",  H//2 + 50, (255, 220, 50), self.fmd),
            ]:
                ts = fn.render(txt, True, col)
                scr.blit(ts, (W//2 - ts.get_width()//2, y))


def main():
    Game().run()

if __name__ == "__main__":
    main()
