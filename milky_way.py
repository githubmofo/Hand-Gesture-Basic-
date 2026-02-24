"""
MILKY WAY GALAXY — Spiral Data-Mesh Visualisation
===================================================
Mathematical spiral-arm galaxy built with polar coordinates.
  • 3 logarithmic spiral arms with structured point distribution.
  • Dense bright core with radial gradient falloff.
  • Arm-to-arm mesh connections for futuristic topology feel.
  • Cyan → violet gradient along arms, warm white/yellow core.
  • Extremely slow rotation — feels massive and stable.
  • Max ~1400 particles for solid 60 FPS.
"""

import math
import random
from OpenGL.GL import *
import config


# ── helpers ───────────────────────────────────────────────────

def _lerp(a, b, t):
    return a + (b - a) * t


def _lerp_color(c0, c1, t):
    return (c0[0] + (c1[0] - c0[0]) * t,
            c0[1] + (c1[1] - c0[1]) * t,
            c0[2] + (c1[2] - c0[2]) * t)


# ── palette ───────────────────────────────────────────────────

CORE_COLOR   = (1.0, 0.95, 0.75)      # warm white-yellow
COL_INNER    = config.CYAN             # inner arm
COL_MID      = config.ELECTRIC         # mid arm
COL_OUTER    = config.VIOLET           # outer arm
COL_ACCENT   = config.MAGENTA          # sparse highlights


class MilkyWay:
    NUM_ARMS       = 3
    ARM_POINTS     = 500       # increased for density
    CORE_POINTS    = 600       # bright dense core
    HALO_POINTS    = 250       
    MAX_RADIUS     = 2.2       
    CORE_RADIUS    = 0.45      
    SCALE          = 4.8       # increased for full-screen immersion
    ROT_SPEED      = 2.2       

    # spiral shape:  r = A * e^(B * θ)
    SPIRAL_A = 0.08
    SPIRAL_B = 0.18
    SPIRAL_WINDS = 2.8         # number of full turns per arm

    def __init__(self):
        self.age      = 0.0
        self.rotation = 0.0
        self._arms    = []     # list of list-of-dict per arm
        self._core    = []     # list of dict
        self._halo    = []     # faint outer points
        random.seed(77)        # deterministic layout
        self._build()

    # ── construction ──────────────────────────────────────────

    def _build(self):
        # ── spiral arms ──
        for arm_i in range(self.NUM_ARMS):
            arm_offset = arm_i * (2.0 * math.pi / self.NUM_ARMS)
            arm = []
            for k in range(self.ARM_POINTS):
                t = k / self.ARM_POINTS                   # 0 → 1
                theta = t * self.SPIRAL_WINDS * 2.0 * math.pi + arm_offset
                r = self.SPIRAL_A * math.exp(self.SPIRAL_B * (theta - arm_offset))
                r = min(r, self.MAX_RADIUS)

                # jitter for natural look (tighter near core)
                jitter_r = r * random.uniform(-0.12, 0.12) * (0.3 + 0.7 * t)
                jitter_a = random.uniform(-0.08, 0.08)

                x = (r + jitter_r) * math.cos(theta + jitter_a)
                y = (r + jitter_r) * math.sin(theta + jitter_a)
                z = random.gauss(0, 0.015 * (1.0 + t))  # thin disk

                norm_r = min(1.0, r / self.MAX_RADIUS)
                arm.append({'x': x, 'y': y, 'z': z, 'norm_r': norm_r,
                            'arm': arm_i, 't': t})
            self._arms.append(arm)

        # ── dense core ──
        for _ in range(self.CORE_POINTS):
            angle = random.uniform(0, 2 * math.pi)
            r     = random.expovariate(8.0)            # exponential → dense centre
            r     = min(r, self.CORE_RADIUS * 1.2)
            x = r * math.cos(angle)
            y = r * math.sin(angle)
            z = random.gauss(0, 0.008)
            norm_r = min(1.0, r / self.CORE_RADIUS)
            self._core.append({'x': x, 'y': y, 'z': z, 'norm_r': norm_r})

        # ── outer halo (very faint scattered stars) ──
        for _ in range(self.HALO_POINTS):
            angle = random.uniform(0, 2 * math.pi)
            r     = random.uniform(self.MAX_RADIUS * 0.7, self.MAX_RADIUS * 1.25)
            x = r * math.cos(angle) + random.gauss(0, 0.15)
            y = r * math.sin(angle) + random.gauss(0, 0.15)
            z = random.gauss(0, 0.03)
            self._halo.append({'x': x, 'y': y, 'z': z})

    # ── colour helpers ────────────────────────────────────────

    @staticmethod
    def _arm_color(norm_r, alpha):
        """Gradient along arm radius: cyan inner → electric mid → violet outer."""
        if norm_r < 0.45:
            rgb = _lerp_color(COL_INNER, COL_MID, norm_r / 0.45)
        else:
            rgb = _lerp_color(COL_MID, COL_OUTER, (norm_r - 0.45) / 0.55)
        return (rgb[0], rgb[1], rgb[2], alpha)

    @staticmethod
    def _core_color(norm_r, alpha):
        """Core: warm white centre → cyan edge."""
        rgb = _lerp_color(CORE_COLOR, COL_INNER, norm_r)
        return (rgb[0], rgb[1], rgb[2], alpha)

    # ── update ────────────────────────────────────────────────

    def update(self, dt):
        self.age      += dt
        self.rotation += self.ROT_SPEED * dt
        return True   # always alive

    # ── draw ──────────────────────────────────────────────────

    def draw(self):
        glPushMatrix()
        glScalef(self.SCALE, self.SCALE, self.SCALE)
        # tilt galaxy ~25° toward viewer for depth
        glRotatef(25.0, 1, 0, 0)
        glRotatef(self.rotation, 0, 0, 1)

        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)   # additive glow

        # ── 1. core glow rings (radial gradient disk) ─────────
        self._draw_core_glow()

        # ── 2. core star points ───────────────────────────────
        glPointSize(5.0)  # larger core stars
        glBegin(GL_POINTS)
        for p in self._core:
            c = self._core_color(p['norm_r'], 0.95 - p['norm_r'] * 0.30)
            glColor4f(*c)
            glVertex3f(p['x'], p['y'], p['z'])
        glEnd()

        # ── 3. spiral arm points ─────────────────────────────
        glPointSize(3.5)  # increased for visibility
        glBegin(GL_POINTS)
        for arm in self._arms:
            for p in arm:
                alpha = 0.90 - p['norm_r'] * 0.40
                c = self._arm_color(p['norm_r'], alpha)
                glColor4f(*c)
                glVertex3f(p['x'], p['y'], p['z'])
        glEnd()

        # ── 4. arm mesh lines (connect adjacent arm points) ──
        glLineWidth(0.6)
        for arm in self._arms:
            glBegin(GL_LINE_STRIP)
            step = 2   # every 2nd point for cleaner lines
            for i in range(0, len(arm), step):
                p = arm[i]
                alpha = (0.45 - p['norm_r'] * 0.30)
                c = self._arm_color(p['norm_r'], alpha)
                glColor4f(*c)
                glVertex3f(p['x'], p['y'], p['z'])
            glEnd()

        # ── 5. inter-arm radial spokes (subtle mesh topology) ─
        glLineWidth(0.45)
        glBegin(GL_LINES)
        spoke_step = 18
        for k in range(0, self.ARM_POINTS, spoke_step):
            for a in range(self.NUM_ARMS):
                b = (a + 1) % self.NUM_ARMS
                if k < len(self._arms[a]) and k < len(self._arms[b]):
                    pa = self._arms[a][k]
                    pb = self._arms[b][k]
                    alpha = 0.12 * (1.0 - pa['norm_r'])
                    if alpha > 0.01:
                        c = self._arm_color(pa['norm_r'], alpha)
                        glColor4f(*c)
                        glVertex3f(pa['x'], pa['y'], pa['z'])
                        glColor4f(c[0], c[1], c[2], 0.0)
                        glVertex3f(pb['x'], pb['y'], pb['z'])
        glEnd()

        # ── 6. outer halo scatter ─────────────────────────────
        glPointSize(1.0)
        glBegin(GL_POINTS)
        for p in self._halo:
            glColor4f(0.6, 0.7, 1.0, 0.18)
            glVertex3f(p['x'], p['y'], p['z'])
        glEnd()

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_DEPTH_TEST)
        glPopMatrix()

    # ── core glow (concentric soft rings) ─────────────────────

    def _draw_core_glow(self):
        SEG  = 48
        RINGS = 6
        for ri in range(RINGS):
            t = ri / RINGS
            r = self.CORE_RADIUS * (0.15 + 0.85 * t)
            alpha = (1.0 - t) * 0.50
            glBegin(GL_LINE_LOOP)
            for i in range(SEG):
                angle = i * 2.0 * math.pi / SEG
                c = self._core_color(t, alpha)
                glColor4f(*c)
                glVertex3f(r * math.cos(angle), r * math.sin(angle), 0.0)
            glEnd()
