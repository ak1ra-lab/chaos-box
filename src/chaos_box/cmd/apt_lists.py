# PYTHON_ARGCOMPLETE_OK

import argparse
from collections import defaultdict
from pathlib import Path

import argcomplete
from chaos_utils.logging import setup_logger

logger = setup_logger(__name__)


def get_repo_stats(apt_lists: Path = Path("/var/lib/apt/lists")) -> defaultdict:
    repo_stats = defaultdict(set)
    for pkg_path in apt_lists.glob("*_Packages"):
        with open(pkg_path) as f:
            for line in f:
                if not line.startswith("Package: "):
                    continue
                repo_stats[pkg_path.name].add(line.split(": ")[-1].strip())
    return repo_stats


def sorted_repo_stats(repo_stats: defaultdict, sort_by: str = "name") -> list:
    if sort_by == "name":
        return sorted(repo_stats.items(), key=lambda x: x[0])
    elif sort_by == "count":
        return sorted(repo_stats.items(), key=lambda x: len(x[1]), reverse=False)
    else:
        return list(repo_stats.items())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sort-by-name",
        action="store_const",
        dest="sort_by",
        const="name",
        help="Sort repositories by name (default)",
    )
    parser.add_argument(
        "--sort-by-count",
        action="store_const",
        dest="sort_by",
        const="count",
        help="Sort repositories by package count",
    )
    parser.set_defaults(sort_by="name")
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    repo_stats = sorted_repo_stats(get_repo_stats(), sort_by=args.sort_by)

    for repo, packages in repo_stats:
        logger.info(f"{len(packages):5d} | {repo}")


if __name__ == "__main__":
    main()
