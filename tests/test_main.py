from basic_kvm.main import greet


def test_greet_default():
    assert "Welcome to basic-kvm" in greet()


def test_greet_name():
    assert "Alice" in greet("Alice")
