"""Tkinter UI helpers for basic-kvm.

Provides a `VideoWidget` that can display frames from a `VideoSource`.
"""
from __future__ import annotations

from typing import Optional

try:
    import tkinter as tk
except Exception:  # pragma: no cover - tkinter may not be available in CI
    tk = None

from .video import VideoSource, bgr_to_photoimage


class VideoWidget(tk.Frame):
    """A simple Tkinter widget that displays frames from a VideoSource.

    Call `start()` to begin polling frames and `stop()` to stop. The widget
    keeps a reference to the PhotoImage to avoid garbage collection.
    """

    def __init__(self, master=None, source: Optional[VideoSource] = None, interval: int = 30, **kwargs):
        if tk is None:
            raise RuntimeError("Tkinter is required for VideoWidget")
        super().__init__(master, **kwargs)
        self.source = source or VideoSource(0)
        self.interval = interval
        self._label = tk.Label(self)
        self._label.pack(fill=tk.BOTH, expand=True)
        self._photo = None
        self._running = False

    def set_source(self, source: VideoSource) -> None:
        """Replace the current VideoSource with a new one at runtime.

        If the widget is running, this will stop polling, release the old
        source, set the new one and resume polling.
        """
        was_running = self._running
        if was_running:
            self._running = False
        # release old
        try:
            if self.source is not None:
                self.source.release()
        except Exception:
            pass
        self.source = source
        if was_running:
            # try to open new source; errors propagate to caller via exceptions
            try:
                self.source.open()
            except Exception:
                # do not crash the UI; just log and keep widget stopped
                return
            self._running = True
            self._poll()

    def start(self) -> None:
        opened = self.source.open()
        if not opened:
            raise RuntimeError(f"Failed to open video source: {self.source.source}")
        self._running = True
        self._poll()

    def _poll(self) -> None:
        if not self._running:
            return
        frame = self.source.read()
        if frame is not None:
            try:
                # record last frame size for external UI use
                try:
                    h, w = frame.shape[:2]
                    self._last_frame_size = (w, h)
                except Exception:
                    self._last_frame_size = None

                photo = bgr_to_photoimage(frame)
                self._photo = photo
                self._label.configure(image=photo)
            except Exception:
                # If conversion fails, ignore for now; higher-level code should log
                pass
        self.after(self.interval, self._poll)

    def stop(self) -> None:
        self._running = False
        try:
            self.source.release()
        except Exception:
            pass

    def last_frame_size(self) -> Optional[tuple[int, int]]:
        """Return last captured frame size as (width, height) or None."""
        return getattr(self, "_last_frame_size", None)
