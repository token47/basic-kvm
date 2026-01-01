
import cv2
import glob
import numpy as np

class VideoSource:

    def __init__(self, source: int | str = 0) -> None:
        self.source = source
        self._cap = None

    def open(self) -> bool:
        """Open the underlying capture device. Returns True if opened."""
        self._cap = cv2.VideoCapture(self.source)
        opened = bool(self._cap.isOpened())
        if not opened:
            return False
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

    def read(self):
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

def enumerate_video_devices():

    import fcntl
    import os
    import videodev2 # type: ignore

    paths = sorted(glob.glob("/dev/video*"))
    devices = []
    for dev in paths:
        fd = os.open(dev, os.O_RDONLY | os.O_NONBLOCK)
        cap = videodev2.v4l2_capability()
        fcntl.ioctl(fd, videodev2.VIDIOC_QUERYCAP, cap)
        caps = int(cap.device_caps)
        if not (caps & videodev2.V4L2_CAP_VIDEO_CAPTURE):
            # skip non-video-capture devices (e.g., metadata-only)
            continue
        # get card name (bytes) and decode
        name = bytes(cap.card).decode("utf-8", errors="ignore").rstrip('\x00')
        # strip duplicated name after colon
        name = name.split(":")[0].strip()
        devices.append((name, dev))
        os.close(fd)

    return devices
