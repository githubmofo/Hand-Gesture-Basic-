# Camera & Window
CAMERA_ID = 0
FPS = 60

# Hand Tracking
MIN_DETECTION_CONFIDENCE = 0.8
MIN_TRACKING_CONFIDENCE = 0.5

# Gesture State Machine
GESTURE_COOLDOWN = 0.25
DEBOUNCE_FRAMES = 3

# Gesture Types
GESTURE_IDLE = "IDLE"
GESTURE_THREE_FINGERS = "THREE_FINGERS"
GESTURE_OPEN_PALM = "OPEN_PALM"
GESTURE_FIST = "FIST"
GESTURE_PEACE = "PEACE"

# Thresholds
PINCH_THRESHOLD = 0.05
FIST_THRESHOLD = 0.08

# Visuals
MAX_OBJECTS = 1

# Deep navy background: #0b0f1a → normalized RGB
COLOR_BG = (0.043, 0.059, 0.102, 1.0)

# Projection
FOV = 55
NEAR_PLANE = 0.1
FAR_PLANE = 100.0
CAMERA_POS = (0, 0, -8.0)

# ── Unified Futuristic Gradient Palette ──────────────────────
# All RGB tuples are normalized [0..1]
CYAN        = (0.0,  0.85, 1.0)
ELECTRIC    = (0.15, 0.45, 1.0)
VIOLET      = (0.5,  0.2,  1.0)
MAGENTA     = (0.9,  0.1,  0.7)
WHITE_GLOW  = (0.85, 0.92, 1.0)
