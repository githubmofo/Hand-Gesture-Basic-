"""
NEBULA — Volumetric Particle-Wave Cloud
========================================
Centered 3D object following the futuristic data-mesh aesthetic.
  • Layers of concentric dot-matrix shells.
  • Points displaced via 3D noise/sine-waves for cloud-like movement.
  • Nearby points connected with faint lines for mesh topology.
  • Cyan → violet gradient flow.
"""

import math
import random
from OpenGL.GL import *
import config

# ── helpers ───────────────────────────────────────────────────

def _lerp_color(c0, c1, t):
    t = max(0.0, min(1.0, t))
    return (c0[0] + (c1[0] - c0[0]) * t,
            c0[1] + (c1[1] - c0[1]) * t,
            c0[2] + (c1[2] - c0[2]) * t)

class Nebula:
    SHELLS = 15
    POINTS_PER_SHELL = 400
    BASE_RADIUS = 4.5
    ROT_SPEED = 5.0
    DISPLACEMENT = 0.20

    def __init__(self):
        self.age = 0.0
        self.rotation = 0.0
        self._points = []
        random.seed(42)
        self._build()

    def _build(self):
        # Create concentric shells of points
        for s in range(self.SHELLS):
            shell_r = self.BASE_RADIUS * (0.4 + 0.6 * (s / self.SHELLS))
            shell_pts = []
            for i in range(self.POINTS_PER_SHELL):
                # Distribute points on a sphere/shell
                phi = math.acos(1 - 2 * (i / self.POINTS_PER_SHELL))
                theta = math.pi * (1 + 5**0.5) * i
                
                x = shell_r * math.sin(phi) * math.cos(theta)
                y = shell_r * math.sin(phi) * math.sin(theta)
                z = shell_r * math.cos(phi)
                
                norm_r = s / self.SHELLS
                shell_pts.append({'bx': x, 'by': y, 'bz': z, 'norm_r': norm_r, 'phase': random.uniform(0, 10)})
            self._points.append(shell_pts)

    def update(self, dt):
        self.age += dt
        self.rotation += self.ROT_SPEED * dt
        return True

    def draw(self):
        glPushMatrix()
        glRotatef(self.rotation * 0.5, 0, 1, 0)
        glRotatef(self.rotation * 0.3, 1, 0, 0)

        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)

        t = self.age

        # ── 1. Draw Points with Displacement ──
        glPointSize(2.0)
        glBegin(GL_POINTS)
        for shell in self._points:
            for p in shell:
                # 3D displacement wave
                offset = math.sin(t * 1.5 + p['phase']) * self.DISPLACEMENT
                px = p['bx'] * (1.0 + offset)
                py = p['by'] * (1.0 + offset)
                pz = p['bz'] * (1.0 + offset)
                
                alpha = 0.6 * (1.1 - p['norm_r'])
                c = _lerp_color(config.CYAN, config.VIOLET, p['norm_r'])
                glColor4f(c[0], c[1], c[2], alpha)
                glVertex3f(px, py, pz)
        glEnd()

        # ── 2. Draw Mesh Lines (connecting shell segments) ──
        glLineWidth(0.5)
        for shell in self._points:
            glBegin(GL_LINE_STRIP)
            for i in range(0, self.POINTS_PER_SHELL, 15): # sparse lines
                p = shell[i]
                offset = math.sin(t * 1.5 + p['phase']) * self.DISPLACEMENT
                px = p['bx'] * (1.0 + offset)
                py = p['by'] * (1.0 + offset)
                pz = p['bz'] * (1.0 + offset)
                
                alpha = 0.15 * (1.0 - p['norm_r'])
                c = _lerp_color(config.CYAN, config.VIOLET, p['norm_r'])
                glColor4f(c[0], c[1], c[2], alpha)
                glVertex3f(px, py, pz)
            glEnd()

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_DEPTH_TEST)
        glPopMatrix()
