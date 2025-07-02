# PYTHON_ARGCOMPLETE_OK

from collections import defaultdict
from pathlib import Path

from chaos_box.logging import setup_logger

logger = setup_logger(__name__)


def get_repo_stats(apt_lists: Path = Path("/var/lib/apt/lists")):
    repo_stats = defaultdict(set)
    for pkg_path in apt_lists.glob("*_Packages"):
        with open(pkg_path) as f:
            for line in f:
                if not line.startswith("Package: "):
                    continue
                repo_stats[pkg_path.name].add(line.split(": ")[-1].strip())

    return repo_stats


def main():
    repo_stats = get_repo_stats()

    for repo, packages in repo_stats.items():
        logger.info(f"{len(packages):5d} | {repo}")


if __name__ == "__main__":
    main()
