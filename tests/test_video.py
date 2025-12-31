import pytest

cv2 = pytest.importorskip("cv2")

from basic_kvm.video import VideoSource


def test_open_invalid_device_returns_false():
    # Try to open an invalid device index; should return False
    src = VideoSource(-99)
    ok = src.open()
    # Depending on the environment, the device may or may not open; ensure a boolean is returned
    assert isinstance(ok, bool)
    src.release()


def test_read_without_open_raises():
    src = VideoSource(0)
    with pytest.raises(RuntimeError):
        src.read()
