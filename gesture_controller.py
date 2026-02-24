import math
import time
import config

# ── MediaPipe landmark indices ───────────────────────────────
# Wrist = 0
# Thumb:  CMC=1  MCP=2  IP=3   TIP=4
# Index:  MCP=5  PIP=6  DIP=7  TIP=8
# Middle: MCP=9  PIP=10 DIP=11 TIP=12
# Ring:   MCP=13 PIP=14 DIP=15 TIP=16
# Pinky:  MCP=17 PIP=18 DIP=19 TIP=20

# Tolerance: a finger counts as extended even if tip is only
# this many normalised units above PIP/MCP (handles slight curl).
EXTENSION_TOLERANCE = 0.03

# ── GESTURE LOCK SYSTEM ──────────────────────────────────────
# How many CONSECUTIVE identical frames before a gesture is confirmed.
# 6 frames ≈ 100 ms at 60 FPS — filters all flickers reliably.
GESTURE_STABILITY_FRAMES = 6

# Minimum seconds between ANY two gesture switches.
SWITCH_COOLDOWN = 0.35


class GestureController:
    """
    Gesture FSM with hard stability lock.

    Rules:
      - A gesture must be held for GESTURE_STABILITY_FRAMES consecutive
        frames before it is considered confirmed.
      - A confirmed gesture is ONLY emitted if it DIFFERS from the
        currently active gesture (the one whose object is on screen).
      - IDLE / None / flickers are completely ignored — they never
        clear the active gesture.
      - SWITCH_COOLDOWN prevents rapid oscillation.
    """

    def __init__(self):
        self._gesture_hold   = config.GESTURE_IDLE   # what raw gesture we're seeing
        self._hold_frames    = 0                      # consecutive frame counter
        self._active_gesture = None                   # what's on screen RIGHT NOW
        self._last_switch    = 0.0                    # timestamp of last switch
        self._frame_count    = 0

    # ── public: called after a successful spawn ───────────────

    def set_active_gesture(self, gesture_name):
        """Inform the controller what gesture/object is currently displayed."""
        self._active_gesture = gesture_name

    # ── public API ────────────────────────────────────────────

    def update(self, landmarks, width, height, dt):
        self._frame_count += 1

        # ── no hand → IDLE, but do NOT reset hold counter ──
        # (brief hand dropout should not kill accumulated stability)
        if not landmarks or len(landmarks) < 21:
            return config.GESTURE_IDLE

        # ── detect raw gesture this frame ──
        raw_gesture = self._detect(landmarks)

        # ── frame-stability counter ──
        if raw_gesture == self._gesture_hold:
            self._hold_frames += 1
        else:
            self._gesture_hold = raw_gesture
            self._hold_frames  = 1

        # ── IDLE is never actionable ──
        if raw_gesture == config.GESTURE_IDLE:
            return config.GESTURE_IDLE

        # ── only emit after GESTURE_STABILITY_FRAMES consecutive frames ──
        if self._hold_frames < GESTURE_STABILITY_FRAMES:
            return config.GESTURE_IDLE

        # ── if same gesture already on screen → ignore completely ──
        if raw_gesture == self._active_gesture:
            return config.GESTURE_IDLE

        # ── cooldown guard (prevents rapid oscillation) ──
        now = time.time()
        if now - self._last_switch < SWITCH_COOLDOWN:
            return config.GESTURE_IDLE

        # ── CONFIRMED: new, stable, different gesture ──
        self._last_switch    = now
        self._active_gesture = raw_gesture
        print(f"GESTURE DETECTED: {raw_gesture}")
        return raw_gesture

    # ── internal helpers ──────────────────────────────────────

    def _y(self, landmarks, idx):
        return landmarks[idx][1]

    def _x(self, landmarks, idx):
        return landmarks[idx][0]

    # ── per-finger extension checks ───────────────────────────

    def _thumb_extended(self, lm):
        tip_x  = self._x(lm, 4)
        ip_x   = self._x(lm, 3)
        mcp_x  = self._x(lm, 2)
        wrist_x = self._x(lm, 0)
        middle_mcp_x = self._x(lm, 9)

        hand_side = wrist_x - middle_mcp_x

        if hand_side >= 0:
            extended = (ip_x - tip_x) > -EXTENSION_TOLERANCE
        else:
            extended = (tip_x - ip_x) > -EXTENSION_TOLERANCE

        tip_y = self._y(lm, 4)
        mcp_y = self._y(lm, 2)
        not_curled_under = tip_y < mcp_y + 0.12

        return extended and not_curled_under

    def _finger_extended(self, lm, tip, pip, mcp):
        tip_y = self._y(lm, tip)
        pip_y = self._y(lm, pip)
        mcp_y = self._y(lm, mcp)
        return (tip_y < pip_y - EXTENSION_TOLERANCE) and (tip_y < mcp_y)

    def _finger_closed(self, lm, tip, pip, mcp):
        return self._y(lm, tip) > self._y(lm, pip) - EXTENSION_TOLERANCE * 0.5

    # ── main detection ────────────────────────────────────────

    def _detect(self, lm):
        thumb  = self._thumb_extended(lm)
        index  = self._finger_extended(lm, 8,  6,  5)
        middle = self._finger_extended(lm, 12, 10, 9)
        ring   = self._finger_extended(lm, 16, 14, 13)
        pinky  = self._finger_extended(lm, 20, 18, 17)

        # closed variants for strict checks
        index_closed  = self._finger_closed(lm, 8,  6,  5)
        middle_closed = self._finger_closed(lm, 12, 10, 9)
        ring_closed   = self._finger_closed(lm, 16, 14, 13)
        pinky_closed  = self._finger_closed(lm, 20, 18, 17)

        # ── OPEN PALM: all five fingers extended ──
        # Checked FIRST (most specific — superset of three-fingers)
        is_open_palm = thumb and index and middle and ring and pinky
        if is_open_palm:
            return config.GESTURE_OPEN_PALM

        # ── THREE FINGERS: index + middle + ring ──
        # Very loose: just needs index, middle, and ring up. Ignore pinky/thumb.
        is_three = index and middle and ring
        if is_three:
            return config.GESTURE_THREE_FINGERS

        # ── PEACE: index + middle, ring + pinky closed ──
        is_peace = index and middle and ring_closed and pinky_closed
        if is_peace:
            return config.GESTURE_PEACE

        # ── FIST: all four main fingers closed ──
        is_fist = index_closed and middle_closed and ring_closed and pinky_closed
        if is_fist:
            return config.GESTURE_FIST

        return config.GESTURE_IDLE
