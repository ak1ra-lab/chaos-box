# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.0] - 2026-02-28

### Added

- Add unit tests for `halfwidth.py`, `iconv8.py`, and other utility functions

### Changed

- Rewrite `CHANGELOG.md` to follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) specification, replacing git-cliff auto-generation
- Update `README.md` tool descriptions to be consistent with actual implementations: clarify default dry-run behavior for `date-rename`, `iconv8`, `qbt-migrate`, and `qbt-tracker`; fix `deb-extract` to reflect explicit file arguments; add `--category`/`--tag` filter details for `qbt-tracker`
- Update `DebExtractor` to accept a list of files instead of a directory
- Enhance punctuation handling for half-width brackets in `halfwidth.py`
- Add badge to README.md
- Upgrade dependencies via `uv sync` and update pre-commit hooks

### Removed

- Remove `AGENTS.md`
- Remove `cliff.toml` (no longer using git-cliff for changelog generation)

### Fixed

- Fix `halfwidth.py` punctuation conversion edge cases

## [0.5.0] - 2025-11-07

### Added

- Implement `qbt_tracker.py` with `qbittorrent-api` integration
- Add docstrings to all commands
- Add `mypy` type checker configuration

### Changed

- Rename several commands for clarity and consistency
- Drop directory glob support on `date-rename` and `iconv8` commands

### Fixed

- Fix `uv` build on test-PyPI CI workflow

## [0.4.0] - 2025-11-01

### Added

- Implement `apt_lists.py` command for APT repository statistics
- Implement `iconv8` command for encoding conversion to UTF-8, with `--gitignore` and `--force` options
- Implement `prime.py` command
- Implement `.zst` decompression support in `deb_extract.py`
- Implement `TarFileZstd` class in internal tarfile utilities
- Implement `utils.py` shared utilities module
- Add test cases for `gitignore.py` and `tarfile.py`
- Enable tests session in `noxfile.py`

### Changed

- Replace `logging_config` with a `JsonFormatter` implementation
- Migrate project management from `pdm` to `uv`
- Migrate `utils` module into the separate `chaos-utils` package
- Enrich package classifiers and keywords in `pyproject.toml`

## [0.3.2] - 2025-06-16

### Changed

- Revert `deb_extract.py` to use `python-debian` instead of `unix-ar`

## [0.3.1] - 2025-06-16

### Changed

- Switch `deb_extract.py` to use `unix-ar` instead of `python-debian` (`debian.arfile`) for `.ar` archive handling

## [0.3.0] - 2025-06-15

### Added

- Add `--respect-gitignore` option to `shasum_list.py`
- Migrate `qbt_dump.py`, `qbt_migrate.py`, `qrcode_split.py`, and `qrcode_merge.py` into the project

### Changed

- Rename PyPI package to `chaos-box`
- Rename `net_stats.py` to `netstats.py`
- Rename `punc_conv.py` to `pconv.py`
- Relocate all command files under `src/chaos_box/cmd/`
- Refactor `deb_extract.py` to split `_extract_ar_member()` into a separate helper
- Update `pyproject.toml` dependencies and remove deprecated script entries

## [0.2.0] - 2025-06-12

### Added

- Implement `date-rename` command (`rename_with_date.py`)
- Implement `shasum-list` command (`shasum_list.py`)
- Implement `README.md`
- Add `MIT LICENSE`

### Changed

- Switch to `pypa/gh-action-pypi-publish` for PyPI publishing
- Rename CI workflow file from `tests.yaml` to `nox.yaml`
- Set console log output to brief format

## [0.1.0] - 2025-06-12

### Added

- Initial release
- Migrate existing scripts into the project: `sort_keys.py`, `urlencode.py`,
  `net_stats.py`, `dir_archive.py`, `merge_ip_ranges.py`, `mobi_archive.py`,
  `enc_recover.py`, `punc_conv.py`, `deb_extract.py`, `pascal.py`, `rotate_images.py`

[Unreleased]: https://github.com/ak1ra-lab/chaos-box/compare/v0.6.0...HEAD
[0.6.0]: https://github.com/ak1ra-lab/chaos-box/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/ak1ra-lab/chaos-box/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/ak1ra-lab/chaos-box/compare/v0.3.2...v0.4.0
[0.3.2]: https://github.com/ak1ra-lab/chaos-box/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/ak1ra-lab/chaos-box/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/ak1ra-lab/chaos-box/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/ak1ra-lab/chaos-box/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/ak1ra-lab/chaos-box/releases/tag/v0.1.0
