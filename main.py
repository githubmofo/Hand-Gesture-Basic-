import os
import warnings
import numpy as np

# ── SUPPRESS WARNINGS ─────────────────────────────────────────
# 1. Suppress Protobuf SymbolDatabase.GetPrototype() deprecation
warnings.filterwarnings("ignore", category=UserWarning, module='google.protobuf.symbol_database')

# 2. Suppress TensorFlow/MediaPipe C++ logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['GLOG_minloglevel'] = '3'
os.environ['GLOG_logtostderr'] = '0'
os.environ['GLOG_stderrthreshold'] = '3'
os.environ['XNNPACK_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# 3. Suppress absl logging (used by MediaPipe internal)
try:
    import absl.logging
    absl.logging.set_verbosity(absl.logging.ERROR)
except ImportError:
    pass

# ── SILENCE C++ STDERR (Aggressive fix for stubborn logs) ─────
class SilenceStderr:
    def __enter__(self):
        self.err_fd = sys.stderr.fileno()
        self.save_fd = os.dup(self.err_fd)
        self.devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(self.devnull, self.err_fd)
    def __exit__(self, *args):
        os.dup2(self.save_fd, self.err_fd)
        os.close(self.devnull)
        os.close(self.save_fd)

import pygame
import cv2
import sys
import time

import config
from camera import Camera
from hand_tracker import HandTracker
from gesture_controller import GestureController
from object_manager import ObjectManager
from renderer import Renderer

from flower import Flower
from milky_way import MilkyWay
from nebula import Nebula
from energy_orb import EnergyOrb

class CinematicUniverse3D:
    def __init__(self):
        # OpenGL Renderer
        self.renderer = Renderer()
        
        # Core Systems (Inside SilenceStderr to block startup logs)
        with SilenceStderr():
            self.camera = Camera(config.CAMERA_ID, self.renderer.width, self.renderer.height)
            self.hand_tracker = HandTracker(config.MIN_DETECTION_CONFIDENCE, config.MIN_TRACKING_CONFIDENCE)
        
        self.object_manager = ObjectManager()
        self.gesture_controller = GestureController()
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.last_time = time.time()
        
        # Gesture Mapping
        self.gesture_map = {
            config.GESTURE_THREE_FINGERS: MilkyWay,
            config.GESTURE_OPEN_PALM: Nebula,
            config.GESTURE_FIST: EnergyOrb,
            config.GESTURE_PEACE: Flower
        }
        
        print("Engine started", flush=True)

    def handle_gestures(self, dt, landmarks):
        gesture = self.gesture_controller.update(landmarks, self.renderer.width, self.renderer.height, dt)

        # IDLE or unrecognised → do absolutely nothing; keep current object alive
        if gesture == config.GESTURE_IDLE or gesture not in self.gesture_map:
            return

        obj_class = self.gesture_map[gesture]
        print(f"ACTION: Triggering {obj_class.__name__}")
        # spawn() internally ignores the call if the same gesture is still active
        self.object_manager.spawn(gesture, obj_class)

    def run(self):
        try:
            while self.running:
                now = time.time()
                dt = now - self.last_time
                self.last_time = now
                
                # Events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        self.running = False

                # Input Processing
                frame = self.camera.get_frame()
                if frame is not None:
                    landmarks = self.hand_tracker.process_frame(frame)
                    self.handle_gestures(dt, landmarks)
                
                # Update
                self.object_manager.update(dt)
                
                # Render
                self.renderer.pre_render()
                self.object_manager.draw()
                self.renderer.post_render()
                
                # Cap FPS
                self.clock.tick(config.FPS)

        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.camera.release()
            self.hand_tracker.release()
            pygame.quit()

def main():
    app = CinematicUniverse3D()
    app.run()

if __name__ == "__main__":
    main()
