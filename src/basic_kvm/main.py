
import logging

from .ui import build_and_run_gui

logger = logging.getLogger(__name__)


def main(argv=None):
    return build_and_run_gui()


if __name__ == "__main__":
    raise SystemExit(main())
