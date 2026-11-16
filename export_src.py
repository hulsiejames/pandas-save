from __future__ import annotations

import shutil
from pathlib import Path

IGNORED_DIRECTORY_NAMES = {
    "__pycache__",
}

IGNORED_DIRECTORY_SUFFIXES = (
    ".egg",
    ".egg-info",
    ".dist-info",
)

IGNORED_FILE_SUFFIXES = {
    ".pyc",
    ".pyo",
}

PROJECT_TREE_FILENAME = "proj_tree.txt"
README_FILENAME = "readme.txt"


def create_txt_src(
    repo_root: str | Path = ".",
    *,
    overwrite: bool = False,
) -> Path:
    """
    Create a flattened text copy of the Python code under ``<repo_root>/src``.

    The package name is determined from the single package directory immediately
    beneath ``src``. The output is written to:

        <repo_root>/<package_name>_txt_src

    Python source files are:

    1. discovered recursively under ``src``;
    2. copied into a single flat output directory;
    3. renamed from ``.py`` to ``.txt``;
    4. given path-based filenames to avoid collisions.

    For example, given:

        src/my_package/tools/parser.py

    the output directory will be:

        my_package_txt_src

    and the exported file will be:

        my_package__tools__parser.txt

    The output directory also contains:

    - ``proj_tree.txt``: the original Python source-tree structure;
    - ``readme.txt``: instructions explaining the exported files.

    The following directories are ignored:

    - __pycache__
    - *.egg
    - *.egg-info
    - *.dist-info

    Parameters
    ----------
    repo_root:
        Path to the repository root. Defaults to the current working directory.

    overwrite:
        If True, remove an existing ``<package_name>_txt_src`` directory before
        creating the new export. If False, raise FileExistsError if the output
        directory already exists.

    Returns
    -------
    pathlib.Path
        The absolute path to the created ``<package_name>_txt_src`` directory.

    Raises
    ------
    FileNotFoundError
        If the repository does not contain a ``src`` directory.

    ValueError
        If no package directory, or more than one package directory, is found
        immediately beneath ``src``.
    """
    repo_root = Path(repo_root).resolve()
    source_root = repo_root / "src"

    if not source_root.is_dir():
        raise FileNotFoundError(f"Source directory does not exist: {source_root}")

    package_name = _find_package_name(source_root)
    destination_root = repo_root / f"{package_name}_txt_src"

    _prepare_destination(
        destination_root=destination_root,
        overwrite=overwrite,
    )

    python_files = _discover_python_files(source_root)

    copied_files: dict[Path, str] = {}

    for source_path in python_files:
        relative_path = source_path.relative_to(source_root)
        exported_filename = _create_exported_filename(relative_path)
        destination_path = destination_root / exported_filename

        if destination_path.exists():
            raise FileExistsError(
                "Two source files produced the same flattened filename:\n"
                f"  Source: {source_path}\n"
                f"  Destination: {destination_path}"
            )

        shutil.copy2(source_path, destination_path)
        copied_files[relative_path] = exported_filename

    project_tree = _create_project_tree(copied_files)
    readme = _create_readme(
        source_root=source_root,
        destination_root=destination_root,
        package_name=package_name,
        copied_files=copied_files,
    )

    (destination_root / PROJECT_TREE_FILENAME).write_text(
        project_tree,
        encoding="utf-8",
    )

    (destination_root / README_FILENAME).write_text(
        readme,
        encoding="utf-8",
    )

    return destination_root


def _find_package_name(source_root: Path) -> str:
    """
    Find the package directory immediately beneath ``source_root``.

    A valid package directory:

    - is a direct child of ``source_root``;
    - is a directory;
    - is not an ignored generated or installation-related directory;
    - contains at least one Python file somewhere within it.

    Exactly one package directory is expected.
    """
    package_directories = sorted(
        (
            path
            for path in source_root.iterdir()
            if path.is_dir()
            and not _is_ignored_directory(path.name)
            and any(
                candidate.is_file()
                for candidate in path.rglob("*.py")
                if not any(
                    _is_ignored_directory(part)
                    for part in candidate.relative_to(path).parts[:-1]
                )
            )
        ),
        key=lambda path: path.name.lower(),
    )

    if not package_directories:
        raise ValueError(
            "Could not find a Python package directory immediately beneath:\n"
            f"  {source_root}\n"
            "Expected a structure such as:\n"
            "  src/<package_name>/"
        )

    if len(package_directories) > 1:
        package_list = "\n".join(f"  - {path.name}" for path in package_directories)

        raise ValueError(
            "More than one Python package directory was found immediately "
            f"beneath:\n  {source_root}\n\n"
            f"Packages found:\n{package_list}\n\n"
            "The package name cannot be determined unambiguously."
        )

    return package_directories[0].name


def _prepare_destination(
    destination_root: Path,
    *,
    overwrite: bool,
) -> None:
    """Create an empty destination directory."""
    if destination_root.exists():
        if not overwrite:
            raise FileExistsError(
                f"Destination already exists: {destination_root}\n"
                "Pass overwrite=True to replace it."
            )

        if destination_root.is_dir():
            shutil.rmtree(destination_root)
        else:
            destination_root.unlink()

    destination_root.mkdir(parents=True)


def _discover_python_files(source_root: Path) -> list:
    """
    Find Python files under ``source_root``, excluding ignored directories.
    """
    python_files: list[Path] = []

    for path in source_root.rglob("*.py"):
        relative_path = path.relative_to(source_root)

        if any(_is_ignored_directory(part) for part in relative_path.parts[:-1]):
            continue

        if path.suffix.lower() in IGNORED_FILE_SUFFIXES:
            continue

        if path.is_file():
            python_files.append(path)

    return sorted(
        python_files,
        key=lambda path: path.relative_to(source_root).as_posix().lower(),
    )


def _is_ignored_directory(name: str) -> bool:
    """Return whether a directory should be excluded."""
    name_lower = name.lower()

    return name_lower in IGNORED_DIRECTORY_NAMES or name_lower.endswith(
        IGNORED_DIRECTORY_SUFFIXES
    )


def _create_exported_filename(relative_path: Path) -> str:
    """
    Create a flat exported filename from a source-relative path.

    Example
    -------
    ``my_package/tools/parser.py`` becomes
    ``my_package__tools__parser.txt``.
    """
    path_without_suffix = relative_path.with_suffix("")
    flattened_name = "__".join(path_without_suffix.parts)

    return f"{flattened_name}.txt"


def _create_project_tree(copied_files: dict[Path, str]) -> str:
    """
    Create a visual tree of the original Python package structure.

    Each Python file includes the name of its corresponding exported text file.
    """
    tree: dict[str, object] = {}

    for relative_path, exported_filename in copied_files.items():
        current_level = tree

        for directory_name in relative_path.parts[:-1]:
            current_level = current_level.setdefault(directory_name, {})

        current_level[relative_path.name] = exported_filename

    lines = [
        "src/",
        *_render_tree(tree),
    ]

    return "\n".join(lines) + "\n"


def _render_tree(
    tree: dict[str, object],
    prefix: str = "",
) -> list:
    """Recursively render a nested dictionary as a directory tree."""
    lines: list[str] = []

    sorted_items = sorted(
        tree.items(),
        key=lambda item: (
            not isinstance(item[1], dict),
            item[0].lower(),
        ),
    )

    for index, (name, value) in enumerate(sorted_items):
        is_last = index == len(sorted_items) - 1
        branch = "└── " if is_last else "├── "
        child_prefix = "    " if is_last else "│   "

        if isinstance(value, dict):
            lines.append(f"{prefix}{branch}{name}/")
            lines.extend(
                _render_tree(
                    tree=value,
                    prefix=prefix + child_prefix,
                )
            )
        else:
            lines.append(f"{prefix}{branch}{name} -> {value}")

    return lines


def _create_readme(
    source_root: Path,
    destination_root: Path,
    package_name: str,
    copied_files: dict[Path, str],
) -> str:
    """Create instructions for Copilot or another code reviewer."""
    return f"""SOURCE CODE TEXT EXPORT
=======================

Package name:

{package_name}

This directory contains a text-based export of the Python source code from:

{source_root}

The export directory is:

{destination_root}

The original Python files have not been modified.

HOW TO USE THIS EXPORT
----------------------

1. Read {PROJECT_TREE_FILENAME} first.

2. {PROJECT_TREE_FILENAME} shows the original directory and package structure
   under the repository's src directory.

3. Each original .py file is shown alongside the corresponding exported .txt
   filename.

4. The exported source files are all stored in this single directory so that
   they can be uploaded individually to Copilot.

5. Each exported filename contains its original path components, separated by
   double underscores.

For example:

    Original:
        src/my_package/tools/parser.py

    Exported:
        my_package__tools__parser.txt

6. Treat each .txt file as Python source code. Its contents are an unchanged
   copy of the corresponding original .py file.

7. Use {PROJECT_TREE_FILENAME} to understand package relationships, relative
   locations, imports, and the role of each source file.

FILES EXPORTED
--------------

Python source files exported: {len(copied_files)}

IGNORED CONTENT
---------------

The export excludes generated or installation-related directories, including:

- __pycache__
- *.egg
- *.egg-info
- *.dist-info

Compiled Python files such as .pyc and .pyo are also excluded.
"""


if __name__ == "__main__":
    output_directory = create_txt_src(overwrite=True)
    print(f"Created text source export at: {output_directory}")
