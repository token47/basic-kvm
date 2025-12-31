# Identity

You are a Senior Python Developer.

# Project Context

`basic-kvm` is a KVM (keyboard, video, mouse) client application that uses external USB hardware to connect to the main console of controlled machines. It uses an HDMI encoder device for video capture (exposed as a v4l2 input) and a CH9329 serial-to-HID bridge to send keyboard and mouse events to the controlled machine.

# Architecture

- Platform: Linux desktop (X11 or Wayland), tested on mainstream distributions.
- Language: Python 3.10+.
- GUI toolkit: Tkinter (use `tkinter` for portability and minimal dependencies).
- UI: single main window showing the video capture; while the mouse is over the view, mouse movements and clicks are forwarded to the controlled machine; keystrokes typed in the app are forwarded as well.
- Video: scale to maintain aspect ratio; fit the whole frame inside the view (letterbox/pillarbox behavior).
- Configuration icons on the top with dropdown menus where you can change serial baud rate (with the default baudrate being 9600) and video input device. Also one for pasting text (sent as keyboard strokes).

External libraries are acceptable; when multiple options exist, prefer the most widely adopted one.

# Project conventions

- Style: follow existing `src/` conventions (type hints, short functions, clear names).
- Imports: prefer explicit imports; list third-party dependencies in `requirements.txt`.
- Errors & logging: use the `logging` module for runtime messages; print to console only when running in a terminal or when verbose/debug mode is enabled. Minimize the exception handling; it's acceptable for the application to fail when dependencies are missing.
- Robustness: choose the approach that best solves the problem and avoid chasing many fallback strategies for external utilities.
- Docs: update `README.md` for user-visible behavior changes.
- Modules: separate reasonably distinct functions in different modules (like main UI, video handling, keyboard and/or mouse, etc.).

# Copilot acceptance checklist

Before accepting any suggestion from Copilot or similar assistants, confirm these items:

- Correctness: the code is functionally correct and matches the intended behavior.
- Scope: prefer accepting small, focused suggestions (single function or small refactor). Do not accept large multi-file changes without manual review.
- Style: code follows project formatting and typing conventions (run `black`, `flake8`, `mypy` if available).
- Dependencies: new dependencies are justified and added to `requirements.txt`.
- Licensing: because this project is GPL v2, ensure copied snippets are license-compatible and attribute external code as needed.

# Decisions for this repo

- GUI toolkit: Tkinter.
- Dependency approval: maintainers should review dependency additions in PRs, but explicit pre-approval is not required.
- AI disclosure: contributors are not required to declare Copilot/AI usage in PRs (optional best practice).

# Device & environment notes (important)

- Video capture: devices appear as `/dev/video*` (v4l2). Use `v4l2`-based APIs or wrappers (e.g., OpenCV `cv2.VideoCapture`) and handle unavailable devices gracefully.
- Serial/USB HID: controlled device may appear as `/dev/ttyUSB*` or via libusb; the CH9329 may present as a serial device — ensure correct baud/format and permission handling.
- Permissions: recommend udev rules for device access or instruct users to run with appropriate group membership (e.g., `dialout`, `video`).
- Wayland vs X11: windowing/input behavior differs; design the UI to degrade gracefully and handle input focus correctly. Document any Wayland-specific limitations.

# Tooling recommendations

- Formatting: `black`.
- Linting: `flake8`.
- Static types: `mypy`.

Run linters and formatters locally before accepting suggestions:

```bash
black --check .
flake8 src
```

# PR checklist snippet (optional to include in PRs)

- Branch from `master` and name it `feat/...` or `fix/...`.
- Run linters and formatters locally.
- Update `requirements.txt` if dependencies change.

# Identity

You are a Senior Python Developer.

# Project Context

`basic-kvm` is a KVM (keyboard, video, mouse) client application that uses external USB hardware to connect to the main console of controlled machines. It uses an HDMI encoder device for video capture (exposed as a v4l2 input) and a CH9329 serial-to-HID bridge to send keyboard and mouse events to the controlled machine.

# Architecture

- Platform: Linux desktop (X11 or Wayland), tested on mainstream distributions.
- Language: Python 3.10+.
- GUI toolkit: Tkinter (use `tkinter` for portability and minimal dependencies).
- UI: single main window showing the video capture; while the mouse is over the view, mouse movements and clicks are forwarded to the controlled machine; keystrokes typed in the app are forwarded as well.
- Video: scale to maintain aspect ratio; fit the whole frame inside the view (letterbox/pillarbox behavior).
- Configuration icons on the top with dropdown menus where you can change serial baud rate (with the default baudrate being 9600) and video input device. Also one for pasting text (sent as keyboard strokes).

External libraries are acceptable; when multiple options exist, prefer the most widely adopted one.

# Project conventions

- Style: follow existing `src/` conventions (type hints, short functions, clear names).
- Tests: we don't need tests.
- Imports: prefer explicit imports; list third-party dependencies in `requirements.txt`.
- Errors & logging: use the `logging` module for runtime messages; print to console only when running in a terminal or when verbose/debug mode is enabled. Minimize the exception handling, there is no problem if the application breaks because of missing dependencies.
- Robustness: there is not need to try different approaches for external utilities or libraries, chose the one that best solves the problem and let the application break if it is not there.
- Docs: update `README.md` for user-visible behavior changes.
- Modules: separate reasonably distinct functions in different modules (like main UI, video handling, keyboard and/or mouse, etc.)

# Copilot acceptance checklist

Before accepting any suggestion from Copilot or similar assistants, confirm all items below:

- Correctness: the code is functionally correct and matches the intended behavior.
- Scope: prefer accepting small, focused suggestions (single function or small refactor). Do not accept large multi-file changes without manual review.
- Tests: the change includes new or updated tests where behavior changed, or you run existing tests locally.
- Style: code follows project formatting and typing conventions (run `black`, `flake8`, `mypy` if available).
- Dependencies: new dependencies are justified in the PR description and added to `requirements.txt`.
- Licensing: because this project is GPL v2, ensure copied snippets are license-compatible and attribute external code as needed.

# Decisions for this repo

- GUI toolkit: Tkinter.
- Dependency approval: not required — maintainers should review dependency additions in PRs, but explicit pre-approval is not required.
- AI disclosure: contributors are not required to declare Copilot/AI usage in PRs (optional best practice).

# Device & environment notes (important)

- Video capture: devices appear as `/dev/video*` (v4l2). Use `v4l2`-based APIs or wrappers (e.g., OpenCV `cv2.VideoCapture`) and handle unavailable devices gracefully.
- Serial/USB HID: controlled device may appear as `/dev/ttyUSB*` or via libusb; the CH9329 may present as a serial device — ensure correct baud/format and permission handling.
- Permissions: recommend udev rules for device access or instruct users to run with appropriate group membership (e.g., `dialout`, `video`).
- Wayland vs X11: windowing/input behavior differs; design the UI to degrade gracefully and handle input focus correctly. Document any Wayland-specific limitations.

# Tooling recommendations

- Formatting: `black`.
- Linting: `flake8`
- Static types: `mypy`
- Tests: `pytest`.

Run tests and linters locally before accepting suggestions:

```bash
PYTHONPATH=src pytest -q
black --check .
flake8 src tests
```

# PR checklist snippet (optional to include in PRs)

- Branch from `master` and name it `feat/...` or `fix/...`.
- Run tests and linters locally.
- Add or update tests for behavior changes.
- Update `requirements.txt` if dependencies change.
