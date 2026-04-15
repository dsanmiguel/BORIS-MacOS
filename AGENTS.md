# Repository Guidelines

## Project Structure & Module Organization
`boris/` contains the application code, including the main entry point in `core.py`, Qt UI modules such as `*_ui.py`, bundled assets under `icons/` and `sounds/`, vendored interval logic in `portion/`, and analysis extensions in `analysis_plugins/`. Tests live in `tests/`, with plugin-specific coverage in `tests/plugins/` and sample fixtures in `tests/files/`. Helper scripts are under `scripts/`, including `scripts/start_macOS.command` for the macOS Docker/XQuartz launcher.

## Build, Test, and Development Commands
Use Python 3.12 or newer.

- `python -m venv .venv && source .venv/bin/activate` creates a local environment.
- `pip install -e .[dev]` installs BORIS plus developer tools from `pyproject.toml`.
- `python -m boris` starts the app from the package in the current checkout.
- `pytest -s -vv` runs the full test suite.
- `make -C tests coverage` runs `pytest -s -vv --cov` using the repository Makefile.
- `ruff check boris tests` runs the configured linter.

## Coding Style & Naming Conventions
Follow existing Python conventions: 4-space indentation, `snake_case` for functions and modules, `PascalCase` for classes, and descriptive test names such as `test_duration_events_use_stop_time_for_latency`. Keep imports explicit and local-package imports relative where the codebase already does so. Respect the Ruff configuration in `pyproject.toml`: maximum line length is 140, and generated or external files like `*_ui.py` and `mpv*` are excluded from linting.

## Testing Guidelines
This repository uses `pytest` with `pytest-cov`. Add tests beside the affected area: core behavior under `tests/`, plugin behavior under `tests/plugins/`. Prefer small fixtures and deterministic assertions against tables, exported data, or parsed project structures. Some tests expect external tools like `ffmpeg`; mention that dependency when changing related code.

## Commit & Pull Request Guidelines
Recent history uses short, direct commit subjects such as `updated citations` and `added latency plugin and relative test`. Keep commit titles brief, imperative, and scoped to one change. For pull requests, include a clear summary, list impacted modules, link the issue when applicable, and attach screenshots for UI-facing changes. Note any environment requirements or manual verification steps in the PR description.
