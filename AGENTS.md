# AGENTS.md — chaos-box

Collection of handy CLI utilities written in Python 3. See [README.md](README.md)
for the full tool list and installation instructions.

## Environment & Tooling — CRITICAL

This project is managed with **uv**. Never use `pip`, `pip install`, or `python -m venv`.

| Task                | Command                                                                 |
| ------------------- | ----------------------------------------------------------------------- |
| Install / sync deps | `uv sync --group dev --all-extras`                                      |
| Run tests           | `uv run pytest -v tests/`                                               |
| Lint + format       | `uv run ruff check --fix src/ tests/ && uv run ruff format src/ tests/` |
| Type check          | `uv run ty check src/`                                                  |
| Build               | `uv build -v`                                                           |

Prefer `just <recipe>` when `just` is available — see `justfile` for all recipes.

Do **NOT** run `pip`, `pip install`, `python setup.py`, or `conda` commands.
Do **NOT** bypass linting with `# noqa` without a specific rule ID and comment.

## Conventions

- All CLI entry points live in `src/chaos_box/cmd/` and are registered in
  `[project.scripts]` inside `pyproject.toml`. When adding a new command,
  add its entry point there.
- Commands follow the pattern: `parse_args()` → `main()`. Keep argument parsing
  separate from business logic.
- Use `chaos_utils.logging.setup_logger(__name__)` for logging; do not use
  `print()` in command modules.
- Use `argcomplete.autocomplete(parser)` and the `# PYTHON_ARGCOMPLETE_OK`
  comment at the top of every command module.
- Default actions are **dry-run**; destructive or mutating operations require
  an explicit `--apply` flag (see `date-rename`, `iconv8`, `qbt-migrate`).

## Testing Guidelines

- Tests live in `tests/` and map to `src/chaos_box/cmd/` by name
  (`test_<module>.py`).
- Do **not** perform real network I/O or filesystem writes to paths outside
  `tmp_path` in tests; mock or use `pytest` fixtures.
- When changing a function signature, update all call sites **and** the
  corresponding test file in the same commit.

## Common Operations

```sh
just sync          # uv sync --group dev --all-extras
just test          # uv run pytest -v tests/
just test -k foo   # run tests matching "foo"
just lint          # ruff check + format
just typecheck     # ty check src/
just build         # uv build -v
```
