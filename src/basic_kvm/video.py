"""Video handling utilities for basic-kvm.

This module provides a small wrapper around OpenCV's VideoCapture
to open v4l2 devices and read frames. It keeps dependencies optional
and provides a helper to convert BGR frames to a Tkinter-compatible
PhotoImage if Pillow is available.
"""
from __future__ import annotations

from typing import Optional, Any

try:
    import cv2
    import numpy as np
except Exception:  # pragma: no cover - cv2 may not be present in all environments
    cv2 = None
    np = None


class VideoSource:
    """Simple video source wrapper.

    Usage:
        src = VideoSource(0)
        ok = src.open()
        if ok:
            frame = src.read()
            src.release()
    """

    def __init__(self, source: int | str = 0) -> None:
        self.source = source
        self._cap = None

    def open(self) -> bool:
        """Open the underlying capture device. Returns True if opened."""
        if cv2 is None:
            raise ImportError("opencv-python (cv2) is required for video capture")
        self._cap = cv2.VideoCapture(self.source)
        opened = bool(self._cap.isOpened())
        if not opened:
            return False

        # Probe and set the maximum available resolution when opening.
        try:
            # Common resolutions, from largest to smallest
            candidates = [
                (3840, 2160),
                (2560, 1440),
                (1920, 1080),
                (1600, 900),
                (1280, 720),
                (1024, 768),
                (800, 600),
                (640, 480),
            ]

            for w, h in candidates:
                try:
                    self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, float(w))
                    self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, float(h))
                except Exception:
                    continue

                # read a few frames to let the device settle
                got = False
                for _ in range(3):
                    ret, frame = self._cap.read()
                    if not ret or frame is None:
                        continue
                    fh, fw = frame.shape[:2]
                    if fw == w and fh == h:
                        got = True
                        break
                if got:
                    # found the highest supported resolution
                    break
        except Exception:
            # ignore probing failures and continue
            pass

        return True

    def _choose_max_resolution(self) -> None:
        """Probe common resolutions from largest to smallest and select the
        highest one that the device actually delivers.

        This will attempt to set the capture properties and verify by reading
        a frame. It is robust to drivers that ignore property sets.
        """
        if self._cap is None:
            return

        # Common resolutions, from largest to smallest
        candidates = [
            (3840, 2160),
            (2560, 1440),
            (1920, 1080),
            (1600, 900),
            (1280, 720),
            (1024, 768),
            (800, 600),
            (640, 480),
        ]

        # Save current settings
        try:
            cur_w = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
            cur_h = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
        except Exception:
            cur_w = cur_h = 0

        for w, h in candidates:
            # attempt to set
            try:
                self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, float(w))
                self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, float(h))
            except Exception:
                continue

            # read a few frames to let the device settle
            got = False
            for _ in range(3):
                ret, frame = self._cap.read()
                if not ret or frame is None:
                    continue
                fh, fw = frame.shape[:2]
                if fw == w and fh == h:
                    got = True
                    break
            if got:
                return

        # none matched; try to restore previous settings if available
        try:
            if cur_w and cur_h:
                self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, float(cur_w))
                self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, float(cur_h))
        except Exception:
            pass

    def read(self) -> Optional[Any]:
        """Read one BGR frame from the device. Returns None if no frame."""
        if self._cap is None:
            raise RuntimeError("Video source is not opened")
        ret, frame = self._cap.read()
        if not ret:
            return None
        return frame

    def release(self) -> None:
        if self._cap is not None:
            try:
                self._cap.release()
            except Exception:
                pass
            self._cap = None


def bgr_to_photoimage(frame):
    """Convert a BGR NumPy frame to a Tkinter PhotoImage using Pillow.

    Raises ImportError if Pillow is not installed.
    """
    try:
        from PIL import Image, ImageTk
    except Exception as exc:  # pragma: no cover - optional dependency
        raise ImportError("Pillow is required to convert frames to PhotoImage") from exc

    if np is None:
        raise RuntimeError("NumPy is required for frame conversion")

    # Convert BGR (OpenCV) to RGB
    rgb = frame[..., ::-1]
    img = Image.fromarray(rgb)
    return ImageTk.PhotoImage(image=img)
