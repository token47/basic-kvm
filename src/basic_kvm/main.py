"""Command-line entrypoint and simple Tkinter application for basic-kvm.

This module exposes `greet()` (kept for tests) and a `main()` that
launches a simple Tkinter GUI integrating `VideoWidget` from
`basic_kvm.ui`. The GUI is not started on import; call `main()` to run it.
"""
from __future__ import annotations

import argparse
import glob
import logging

from typing import List, Tuple
from typing import Optional

try:
    import tkinter as tk
except Exception:  # pragma: no cover - tkinter may not be available in CI
    tk = None

from .video import VideoSource
from .ui import VideoWidget

logger = logging.getLogger(__name__)
def enumerate_video_devices() -> List[Tuple[str, str]]:
    """Return a list of (display_name, device_path) for available video devices.

    Display name is a human-friendly card/driver name when available; the
    second element is the device path (e.g. /dev/video0). If capabilities
    cannot be queried, the basename is used as the display name. Always
    returns a non-empty list with fallback entries.
    """
    # Strict mode: require the `v4l2` Python bindings and use VIDIOC_QUERYCAP only.
    try:
        import fcntl
        import os
        import v4l2
    except Exception as exc:
        # fail early — preferred method unavailable
        raise ImportError("v4l2 Python bindings are required for device enumeration") from exc

    paths = sorted(glob.glob("/dev/video*"))
    devices = []
    for dev in paths:
        try:
            fd = os.open(dev, os.O_RDONLY | os.O_NONBLOCK)
        except Exception:
            continue
        try:
            cap = v4l2.struct_v4l2_capability()
            fcntl.ioctl(fd, v4l2.VIDIOC_QUERYCAP, cap)
            caps = int(cap.capabilities)
            if not (caps & v4l2.V4L2_CAP_VIDEO_CAPTURE):
                # skip non-video-capture devices (e.g., metadata-only)
                continue
            # get card name (bytes) and decode
            name = getattr(cap, "card", b"")
            if isinstance(name, bytes):
                name = name.split(b"\x00", 1)[0].decode(errors="ignore")
            display = f"{name} ({dev})" if name else dev
            devices.append((display, dev))
        except Exception:
            # on ioctl failure, skip device
            continue
        finally:
            try:
                os.close(fd)
            except Exception:
                pass

    return devices


def greet(name: Optional[str] = None) -> str:
    if name:
        return f"Hello, {name}! Welcome to basic-kvm."
    return "Hello! Welcome to basic-kvm."


class SerialSender:
    """Simple optional serial sender.

    If `pyserial` is installed this will use a real serial port, otherwise
    it will log the sent text (useful for development).
    """

    def __init__(self, device: str = "/dev/ttyUSB0", baud: int = 9600) -> None:
        self.device = device
        self.baud = baud
        try:
            import serial

            self._serial = serial.Serial
        except Exception:
            self._serial = None

        self._conn = None

    def open(self) -> None:
        if self._serial is None:
            logger.info("pyserial not available; SerialSender will log messages")
            return
        try:
            self._conn = self._serial(self.device, self.baud, timeout=1)
        except Exception as exc:
            logger.exception("Failed to open serial device %s: %s", self.device, exc)

    def send_text(self, text: str) -> None:
        if self._conn is not None:
            try:
                # Convert to bytes and write; real devices may expect different encoding
                self._conn.write(text.encode("utf-8"))
            except Exception:
                logger.exception("Failed to write to serial device")
        else:
            logger.info("SerialSender (dry): %s", text)

    def close(self) -> None:
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception:
                pass


def build_and_run_gui(video_device: str | int = 0, serial_device: str = "/dev/ttyUSB0", baud: int = 9600) -> int:
    if tk is None:
        logger.error("Tkinter is not available in this environment")
        return 2

    root = tk.Tk()
    root.title("basic-kvm")

    sender = SerialSender(device=str(serial_device), baud=baud)
    sender.open()

    video_src = VideoSource(video_device)
    widget = VideoWidget(root, source=video_src)
    widget.pack(fill=tk.BOTH, expand=True)

    # Top controls: device and baud selectors, and paste text
    top = tk.Frame(root)
    top.pack(side=tk.TOP, fill=tk.X)

    tk.Label(top, text="Baud:").pack(side=tk.LEFT)
    baud_var = tk.StringVar(value=str(baud))
    baud_menu = tk.OptionMenu(top, baud_var, "9600", "19200", "38400", "57600", "115200")
    baud_menu.pack(side=tk.LEFT)

    tk.Label(top, text="Video:").pack(side=tk.LEFT)
    dev_var = tk.StringVar(value=str(video_device))
    devices = enumerate_video_devices()
    dev_menu = tk.OptionMenu(top, dev_var, *devices)
    dev_menu.pack(side=tk.LEFT)

    tk.Label(top, text="Serial:").pack(side=tk.LEFT)
    serial_var = tk.StringVar(value=str(serial_device))
    serial_menu = tk.OptionMenu(top, serial_var, "/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/serial/by-id/usb-CH9329", "none")
    serial_menu.pack(side=tk.LEFT)

    serial_status = tk.Label(top, text="Serial: closed")
    serial_status.pack(side=tk.LEFT, padx=(6, 0))

    # Resolution display on the right
    res_label = tk.Label(top, text="Resolution: N/A")
    res_label.pack(side=tk.RIGHT)

    def update_serial_status():
        nonlocal sender
        state = "open" if getattr(sender, "_conn", None) is not None else "closed"
        serial_status.configure(text=f"Serial: {state}")
        open_close_btn.configure(text="Close Serial" if state == "open" else "Open Serial")

    def serial_changed(*_args):
        nonlocal sender
        new_dev = serial_var.get()
        if new_dev == "none":
            sender.close()
            sender = SerialSender(device="/dev/ttyUSB0", baud=int(baud_var.get()))
            update_serial_status()
            return
        sender.close()
        sender = SerialSender(device=new_dev, baud=int(baud_var.get()))
        sender.open()
        update_serial_status()

    serial_var.trace("w", serial_changed)

    def toggle_serial():
        nonlocal sender
        if getattr(sender, "_conn", None) is not None:
            sender.close()
        else:
            sender.open()
        update_serial_status()

    open_close_btn = tk.Button(top, text="Open Serial", command=toggle_serial)
    open_close_btn.pack(side=tk.LEFT)

    def paste_and_send():
        # Simple dialog for text to send
        try:
            from tkinter import simpledialog
        except Exception:
            simpledialog = None
        if simpledialog is None:
            logger.warning("simpledialog not available; cannot paste text")
            return
        text = simpledialog.askstring("Paste text", "Text to send as keystrokes:")
        if text:
            sender.send_text(text)

    paste_btn = tk.Button(top, text="Paste & Send", command=paste_and_send)
    paste_btn.pack(side=tk.LEFT)

    def video_changed(*_args):
        new_dev = dev_var.get()
        # interpret numeric device indices
        try:
            new_src = int(new_dev)
        except Exception:
            new_src = new_dev
        try:
            widget.set_source(VideoSource(new_src))
        except Exception:
            logger.exception("Failed to switch video source to %s", new_dev)

    dev_var.trace("w", video_changed)

    try:
        widget.start()

        def update_resolution():
            size = widget.last_frame_size()
            if size is None:
                res_text = "Resolution: N/A"
            else:
                w, h = size
                res_text = f"Resolution: {w}x{h}"
            try:
                res_label.configure(text=res_text)
            except Exception:
                pass
            root.after(500, update_resolution)

        root.after(500, update_resolution)
        root.mainloop()
    finally:
        widget.stop()
        sender.close()

    return 0


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="basic-kvm GUI application")
    parser.add_argument("--name", help="Your name (for a simple greeting)", default=None)
    parser.add_argument("--device", help="Video device index or path", default=0)
    parser.add_argument("--serial", help="Serial device path (or 'none')", default="/dev/ttyUSB0")
    parser.add_argument("--baud", help="Serial baud rate", type=int, default=9600)
    # GUI-only application: do not offer a --nogui option
    args = parser.parse_args(argv)

    # Always run GUI

    return build_and_run_gui(video_device=args.device, serial_device=args.serial, baud=args.baud)


if __name__ == "__main__":
    raise SystemExit(main())
