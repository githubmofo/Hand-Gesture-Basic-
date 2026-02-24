"""
ObjectManager — persistent single-object scene controller.

Rules:
  • Only ONE object is ever active at a time.
  • The object is NEVER auto-expired / removed on a timer.
    (Objects' own update() still runs for animation, but its return
     value is IGNORED — we never destroy the object because of age.)
  • The only way to change the object is an explicit spawn() call,
    which happens only when a NEW gesture is detected.
"""


class ObjectManager:

    def __init__(self):
        self.current_object  = None
        self.current_gesture = None    # which gesture owns the current object

    # ── public API ────────────────────────────────────────────

    def spawn(self, gesture_name, object_class):
        """
        Replace the current object ONLY if gesture_name differs from
        the gesture that produced the current object.

        Returns True if a new object was spawned, False if ignored.
        """
        if gesture_name == self.current_gesture and self.current_object is not None:
            # Same gesture re-fired — keep existing object, do nothing.
            return False

        # New gesture → replace object
        self.current_object  = object_class()
        self.current_gesture = gesture_name
        print(f"SCENE: spawned {object_class.__name__} (gesture={gesture_name})")
        return True

    def update(self, dt):
        """
        Advance animation.  NEVER removes the object — it lives forever
        until explicitly replaced by a new gesture spawn.
        """
        if self.current_object is not None:
            # Call update for animation state; ignore the returned alive-flag.
            self.current_object.update(dt)

    def draw(self):
        if self.current_object is not None:
            self.current_object.draw()

    def clear(self):
        """Force-clear (not called by normal gesture flow)."""
        self.current_object  = None
        self.current_gesture = None
