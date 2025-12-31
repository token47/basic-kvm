# basic-kvm

A minimal Python project skeleton for basic-kvm. Includes quick start, development, testing, and deployment instructions you can customize.

## Purpose

Provide a small, well-structured Python project layout for experimenting with KVM-related tooling and learning. Target users are developers who want a simple starting point with tests and CI included.

## Status

Alpha

## Prerequisites

- Python 3.10+ (3.11 recommended)
- `python3` and `pip` available on PATH
- Optional: Docker for containerized runs

## Quick Start

Clone and enter the repo:

```bash
git clone <repo-url>
cd basic-kvm
```

Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the example CLI:

```bash
python -m basic_kvm.main
```

## Development

- Run tests: `pytest`
- Linting: `flake8 src` (if you add `flake8` to requirements)
- Formatting: `black .` (if you add `black`)

## Testing

Unit tests use `pytest`. Example:

```bash
pytest -q
```

## Configuration

Use environment variables or a `.env` file for secrets and runtime configuration. See `.env.example`.

## Build & Release

This project uses a simple `pyproject.toml` for metadata. Use your preferred packaging workflow to build and publish.

## Contributing

See `CONTRIBUTING.md` for guidance on branches, PRs and code style.

## License

MIT — see `LICENSE`
