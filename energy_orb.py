"""
ENERGY ORB — Spherical Mesh Field
====================================
A mathematical field visualisation:
  • Latitude-longitude grid lines on the sphere surface.
  • Fine dot-matrix at every grid intersection.
  • Gradient colour flows across the sphere (cyan pole → violet equator → magenta south).
  • Outer faint halo mesh (slightly larger sparse grid).
  • Very slow rotation around Y axis.
  • No electric arcs. No chaotic glow.
"""

import math
from OpenGL.GL import *
import config


def _lerp_color(c0, c1, t):
    return (c0[0]+(c1[0]-c0[0])*t,
            c0[1]+(c1[1]-c0[1])*t,
            c0[2]+(c1[2]-c0[2])*t)


class EnergyOrb:
    GRID_LAT  = 20     # latitude divisions on core sphere
    GRID_LON  = 32     # longitude divisions on core sphere
    RADIUS    = 0.75   # core sphere radius
    HALO_RAD  = 1.05   # outer halo sphere radius
    HALO_LAT  = 10     # sparser halo grid
    HALO_LON  = 16
    SCALE     = 2.0
    ROT_SPEED = 10.0   # degrees/second — very slow

    def __init__(self):
        self.age      = 0.0
        self.rotation = 0.0   # Y-axis rotation angle (degrees)
        # pre-bake sphere vertices for both sphere and halo
        self._core_verts = self._sphere_verts(self.RADIUS,
                                               self.GRID_LAT, self.GRID_LON)
        self._halo_verts = self._sphere_verts(self.HALO_RAD,
                                               self.HALO_LAT, self.HALO_LON)

    # ── geometry helper ───────────────────────────────────────

    @staticmethod
    def _sphere_verts(R, lat_divs, lon_divs):
        """
        Returns a 2D array [lat_divs+1][lon_divs+1] of (x,y,z) on sphere R.
        Row 0 = south pole lat (-π/2), Row lat_divs = north pole lat (π/2).
        Called as _sphere_verts(R, GRID_LAT, GRID_LON) so:
            verts has GRID_LAT+1 rows, each with GRID_LON+1 columns.
        _draw_sphere_grid(verts, stacks=GRID_LAT, slices=GRID_LON) then safely
        accesses verts[i][j] for i in range(stacks+1), j in range(slices+1).
        """
        verts = []
        for i in range(lat_divs + 1):
            lat = math.pi * (-0.5 + i / lat_divs)   # -π/2 .. π/2
            row = []
            for j in range(lon_divs + 1):
                lon = 2.0 * math.pi * j / lon_divs
                x = R * math.cos(lat) * math.cos(lon)
                y = R * math.sin(lat)
                z = R * math.cos(lat) * math.sin(lon)
                row.append((x, y, z))
            verts.append(row)
        return verts

    # ── colour ────────────────────────────────────────────────

    def _sphere_color(self, lat_norm, alpha):
        """
        lat_norm 0=south, 1=north.
        South → magenta, equator → electric, north → cyan.
        """
        if lat_norm < 0.5:
            rgb = _lerp_color(config.MAGENTA, config.ELECTRIC, lat_norm * 2.0)
        else:
            rgb = _lerp_color(config.ELECTRIC, config.CYAN, (lat_norm - 0.5) * 2.0)
        return (rgb[0], rgb[1], rgb[2], alpha)

    # ── update ────────────────────────────────────────────────

    def update(self, dt):
        self.age      += dt
        self.rotation += self.ROT_SPEED * dt
        return self.age < 22.0

    # ── draw ──────────────────────────────────────────────────

    def draw(self):
        glPushMatrix()
        glScalef(self.SCALE, self.SCALE, self.SCALE)
        glRotatef(self.rotation, 0, 1, 0)

        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)

        # ── core sphere grid ──────────────────────────────────
        self._draw_sphere_grid(self._core_verts,
                               self.GRID_LAT, self.GRID_LON,
                               line_alpha=0.80, dot_alpha=0.90,
                               line_w=0.8, dot_size=2.0)

        # ── outer halo grid (dimmer, larger) ─────────────────
        self._draw_sphere_grid(self._halo_verts,
                               self.HALO_LAT, self.HALO_LON,
                               line_alpha=0.22, dot_alpha=0.30,
                               line_w=0.5, dot_size=1.4)

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_DEPTH_TEST)
        glPopMatrix()

    # ── sphere grid helper ────────────────────────────────────

    def _draw_sphere_grid(self, verts, stacks, slices,
                          line_alpha, dot_alpha, line_w, dot_size):
        """
        Draw a lat/lon sphere grid.

        verts  : 2D list [lat_divs+1][lon_divs+1]
        stacks : number of latitude  bands  (= lat_divs  = GRID_LAT or HALO_LAT)
        slices : number of longitude bands  (= lon_divs  = GRID_LON or HALO_LON)

        We derive actual column count from the vertex array itself so this
        method is immune to caller parameter mismatches.
        """
        if not verts or stacks == 0:
            return

        glLineWidth(line_w)
        # Derive actual column count from data (defensive)
        lon_count = len(verts[0])   # lon_divs + 1

        # ── latitude circles (ring around sphere at each lat band) ──
        for i in range(len(verts)):
            lat_norm = i / stacks if stacks > 0 else 0.0
            glBegin(GL_LINE_LOOP)
            for j in range(lon_count - 1):   # -1: LINE_LOOP closes itself
                c = self._sphere_color(lat_norm, line_alpha)
                glColor4f(*c)
                px, py, pz = verts[i][j]
                glVertex3f(px, py, pz)
            glEnd()

        # ── longitude lines (pole-to-pole strips) ──
        for j in range(lon_count - 1):
            glBegin(GL_LINE_STRIP)
            for i in range(len(verts)):
                lat_norm = i / stacks if stacks > 0 else 0.0
                c = self._sphere_color(lat_norm, line_alpha)
                glColor4f(*c)
                px, py, pz = verts[i][j]
                glVertex3f(px, py, pz)
            glEnd()

        # ── intersection dots ──
        glPointSize(dot_size)
        glBegin(GL_POINTS)
        for i in range(len(verts)):
            lat_norm = i / stacks if stacks > 0 else 0.0
            c = self._sphere_color(lat_norm, dot_alpha)
            for j in range(lon_count):
                glColor4f(*c)
                px, py, pz = verts[i][j]
                glVertex3f(px, py, pz)
        glEnd()

