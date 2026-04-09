#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from collections import Counter
from pathlib import Path


def human_size(value: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = float(value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


def iter_files(root: Path, include_hidden: bool) -> list[Path]:
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        if not include_hidden:
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            filenames = [f for f in filenames if not f.startswith(".")]
        for filename in filenames:
            files.append(Path(dirpath) / filename)
    return files


def extension_label(path: Path) -> str:
    suffix = path.suffix.lower()
    return suffix if suffix else "<none>"


def gather_stats(root: Path, include_hidden: bool) -> dict[str, object]:
    if root.is_file():
        try:
            size = root.stat().st_size
        except OSError:
            size = 0
        return {
            "root": root,
            "files": [root],
            "file_count": 1,
            "dir_count": 0,
            "total_size": size,
            "extensions": Counter({extension_label(root): 1}),
            "skipped": 0,
        }

    files = iter_files(root, include_hidden)
    extensions: Counter[str] = Counter()
    total_size = 0
    skipped = 0
    for path in files:
        try:
            stat = path.stat()
        except OSError:
            skipped += 1
            continue
        total_size += stat.st_size
        extensions[extension_label(path)] += 1

    dir_count = 1
    for _, dirnames, _ in os.walk(root):
        dir_count += len(dirnames)

    return {
        "root": root,
        "files": files,
        "file_count": len(files),
        "dir_count": dir_count,
        "total_size": total_size,
        "extensions": extensions,
        "skipped": skipped,
    }


def print_extension_summary(extensions: Counter[str]) -> None:
    print("Extensions:")
    if not extensions:
        print("  (none)")
        return
    for ext, count in extensions.most_common():
        print(f"  {ext}: {count}")


def print_top_files(files: list[Path], top: int, root: Path) -> None:
    if top <= 0:
        return
    sizes: list[tuple[int, Path]] = []
    for path in files:
        try:
            size = path.stat().st_size
        except OSError:
            continue
        sizes.append((size, path))
    sizes.sort(reverse=True, key=lambda item: item[0])
    if not sizes:
        print("\nTop files:")
        print("  (none)")
        return
    print("\nTop files:")
    for size, path in sizes[:top]:
        rel_path = path.relative_to(root) if path.is_relative_to(root) else path
        print(f"  {human_size(size):>10}  {rel_path}")


def print_tree(root: Path, max_depth: int, include_hidden: bool) -> None:
    print("\nTree:")
    print(root)
    if root.is_file() or max_depth <= 0:
        return

    def walk(path: Path, prefix: str, depth: int) -> None:
        if depth <= 0:
            return
        try:
            entries = sorted(
                path.iterdir(), key=lambda p: (p.is_file(), p.name.lower())
            )
        except OSError:
            print(f"{prefix}└── [permission denied]")
            return
        if not include_hidden:
            entries = [entry for entry in entries if not entry.name.startswith(".")]
        for index, entry in enumerate(entries):
            connector = "└── " if index == len(entries) - 1 else "├── "
            print(f"{prefix}{connector}{entry.name}")
            if entry.is_dir():
                extension = "    " if index == len(entries) - 1 else "│   "
                walk(entry, prefix + extension, depth - 1)

    walk(root, "", max_depth)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a quick summary report for a directory."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to summarize (default: current directory).",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="Show the N largest files (default: 5, 0 to disable).",
    )
    parser.add_argument(
        "--tree",
        action="store_true",
        help="Print a directory tree snapshot.",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=2,
        help="Maximum tree depth when using --tree (default: 2).",
    )
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden files and directories.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.path).expanduser().resolve()
    if not root.exists():
        print(f"Path not found: {root}")
        return 1

    stats = gather_stats(root, include_hidden=args.include_hidden)
    total_size = int(stats["total_size"])

    print("Summary:")
    print(f"  Path: {root}")
    print(f"  Files: {stats['file_count']}")
    print(f"  Directories: {stats['dir_count']}")
    print(f"  Total size: {human_size(total_size)} ({total_size} bytes)")
    if stats["skipped"]:
        print(f"  Skipped (errors): {stats['skipped']}")

    print()
    print_extension_summary(stats["extensions"])
    print_top_files(stats["files"], args.top, root)

    if args.tree:
        print_tree(root, args.max_depth, args.include_hidden)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
