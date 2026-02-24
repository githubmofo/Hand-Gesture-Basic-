import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import config

class Renderer:
    def __init__(self):
        pygame.init()

        info = pygame.display.Info()
        self.width, self.height = info.current_w, info.current_h

        pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL | FULLSCREEN)
        pygame.display.set_caption("Futuristic Data Visualisation Engine")

        # ── base OpenGL state ─────────────────────────────────
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Deep navy: #0b0f1a
        glClearColor(*config.COLOR_BG)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_POINT_SMOOTH)
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)

        # Projection
        self.setup_projection()
        self.camera_pos = config.CAMERA_POS

        print(f"Renderer: {self.width}x{self.height}", flush=True)

    def setup_projection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(config.FOV, self.width / self.height, config.NEAR_PLANE, config.FAR_PLANE)
        glMatrixMode(GL_MODELVIEW)

    def pre_render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(*self.camera_pos)

    def post_render(self):
        pygame.display.flip()
