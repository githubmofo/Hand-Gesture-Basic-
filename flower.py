"""
FLOWER — Radial Data-Wave Bloom
================================
Each petal is a parametric mesh surface with fine grid topology.
Gradient flows from cyan at the centre → violet at the tips.
Smooth sinusoidal wave displacement gives living-data feel.
"""

import math
import numpy as np
from OpenGL.GL import *
import config


# ── colour helpers ────────────────────────────────────────────

def _lerp_color(c0, c1, t):
    """Linearly interpolate between two RGB tuples."""
    return (
        c0[0] + (c1[0] - c0[0]) * t,
        c0[1] + (c1[1] - c0[1]) * t,
        c0[2] + (c1[2] - c0[2]) * t,
    )


# ── main class ────────────────────────────────────────────────

class Flower:
    NUM_PETALS   = 8      # radially symmetric bloom
    PETAL_U      = 14     # mesh resolution along petal length
    PETAL_V      = 10     # mesh resolution across petal width
    PETAL_LEN    = 1.05   # length from core to tip
    PETAL_WIDTH  = 0.38   # max half-width
    SCALE        = 2.6    # world-space scale

    # gradient palette: centre → tip
    COL_INNER = config.CYAN        # cyan at core
    COL_MID   = config.ELECTRIC    # electric blue mid-petal
    COL_OUTER = config.VIOLET      # violet at tips

    # secondary accent for connecting ring
    COL_RING  = config.MAGENTA

    def __init__(self):
        self.age      = 0.0
        self.rotation = 0.0      # slow world rotation (°)
        self._build_mesh()

    # ── mesh construction ─────────────────────────────────────

    def _build_mesh(self):
        """Pre-build UV grid indices for each petal (shared geometry)."""
        U = self.PETAL_U
        V = self.PETAL_V

        # Build index list for GL_LINES (grid topology)
        self._line_indices = []
        for u in range(U + 1):
            for v in range(V + 1):
                idx = u * (V + 1) + v
                if u < U:
                    self._line_indices.append((idx, idx + (V + 1)))
                if v < V:
                    self._line_indices.append((idx, idx + 1))

    # ── parametric surface ────────────────────────────────────

    def _petal_point(self, u_norm, v_norm, time):
        """
        Return (x, y, z_displaced) for a normalised UV on a single petal.
        Petal lies in the XY plane; v=0.5 is centre axis.
        """
        L   = self.PETAL_LEN
        W   = self.PETAL_WIDTH

        # envelope: narrow at base & tip, widest at 60 % length
        envelope = math.sin(u_norm * math.pi) ** 1.4
        x = (v_norm - 0.5) * 2.0 * W * envelope

        # organic tapering along length
        y = 0.18 + u_norm * L

        # wave displacement (perpendicular to petal plane = Z)
        freq  = 2.5
        phase = time * 1.2 + u_norm * math.pi * freq + v_norm * math.pi
        z = 0.08 * math.sin(phase) * envelope

        return (x, y, z)

    # ── colour at UV ──────────────────────────────────────────

    def _petal_color(self, u_norm, v_norm, alpha=1.0):
        """Gradient: cyan→electric→violet along length."""
        if u_norm < 0.5:
            t   = u_norm * 2.0
            rgb = _lerp_color(self.COL_INNER, self.COL_MID, t)
        else:
            t   = (u_norm - 0.5) * 2.0
            rgb = _lerp_color(self.COL_MID, self.COL_OUTER, t)

        # subtle brightness roll-off toward centre (base)
        brightness = 0.55 + 0.45 * u_norm
        return (rgb[0] * brightness, rgb[1] * brightness,
                rgb[2] * brightness, alpha)

    # ── update ────────────────────────────────────────────────

    def update(self, dt):
        self.age      += dt
        self.rotation += dt * 6.0    # slow, elegant rotation
        return self.age < 22.0

    # ── draw ──────────────────────────────────────────────────

    def draw(self):
        glPushMatrix()
        glScalef(self.SCALE, self.SCALE, self.SCALE)
        glRotatef(self.rotation, 0, 0, 1)

        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)   # additive for glow lines
        glLineWidth(0.9)

        t   = self.age
        U   = self.PETAL_U
        V   = self.PETAL_V

        for petal_i in range(self.NUM_PETALS):
            angle_deg = petal_i * (360.0 / self.NUM_PETALS)

            glPushMatrix()
            glRotatef(angle_deg, 0, 0, 1)

            # ── build vertex grid for this petal ──
            grid = []   # grid[u][v] = (x, y, z)
            for u in range(U + 1):
                row = []
                for v in range(V + 1):
                    u_n = u / U
                    v_n = v / V
                    row.append(self._petal_point(u_n, v_n, t))
                grid.append(row)

            # ── draw mesh lines ──
            glBegin(GL_LINES)
            for u in range(U + 1):
                for v in range(V + 1):
                    u_n = u / U
                    idx = u * (V + 1) + v
                    px, py, pz = grid[u][v]

                    # horizontal edge (along U)
                    if u < U:
                        nx, ny, nz = grid[u + 1][v]
                        c  = self._petal_color(u_n, v / V, alpha=0.80)
                        c2 = self._petal_color((u + 1) / U, v / V, alpha=0.80)
                        glColor4f(*c);  glVertex3f(px, py, pz)
                        glColor4f(*c2); glVertex3f(nx, ny, nz)

                    # vertical edge (along V)
                    if v < V:
                        nx, ny, nz = grid[u][v + 1]
                        c  = self._petal_color(u_n, v / V, alpha=0.80)
                        c2 = self._petal_color(u_n, (v + 1) / V, alpha=0.80)
                        glColor4f(*c);  glVertex3f(px, py, pz)
                        glColor4f(*c2); glVertex3f(nx, ny, nz)
            glEnd()

            glPopMatrix()

        # ── central radiant ring ──────────────────────────────
        self._draw_core_ring(t)

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_DEPTH_TEST)
        glPopMatrix()

    # ── core ring ─────────────────────────────────────────────

    def _draw_core_ring(self, t):
        """Soft luminous ring at the very centre of the bloom."""
        SEG = 80
        for ring_r, alpha in [(0.05, 0.90), (0.12, 0.55), (0.22, 0.28)]:
            pulse = 1.0 + 0.06 * math.sin(t * 3.0)
            r = ring_r * pulse
            glBegin(GL_LINE_LOOP)
            for i in range(SEG):
                angle = i * 2.0 * math.pi / SEG
                # blend cyan → magenta around ring
                t_ring = (i / SEG)
                c = _lerp_color(config.CYAN, config.MAGENTA, t_ring)
                glColor4f(c[0], c[1], c[2], alpha)
                glVertex3f(r * math.cos(angle), r * math.sin(angle), 0)
            glEnd()
