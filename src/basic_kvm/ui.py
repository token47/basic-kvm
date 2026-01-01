
import logging
import tkinter as tk

from .video import VideoSource, bgr_to_photoimage, enumerate_video_devices
from .serial import SerialSender

logger = logging.getLogger(__name__)


class VideoWidget(tk.Frame):
    """A simple Tkinter widget that displays frames from a VideoSource.

    Call `start()` to begin polling frames and `stop()` to stop. The widget
    keeps a reference to the PhotoImage to avoid garbage collection.
    """

    def __init__(self, master=None, source=None, interval=30, **kwargs):
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

    def last_frame_size(self):
        """Return last captured frame size as (width, height) or None."""
        return getattr(self, "_last_frame_size", None)


def build_and_run_gui(video_device: str | int = 0, serial_device: str = "/dev/ttyUSB0", baud: int = 9600) -> int:

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
        from tkinter import simpledialog
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
