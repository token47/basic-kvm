

import logging

logger = logging.getLogger(__name__)

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

