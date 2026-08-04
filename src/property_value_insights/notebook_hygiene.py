"""Remove transient execution timing metadata from committed notebooks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def sanitize_notebook(path: Path) -> bool:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    changed = False
    for cell in notebook["cells"]:
        metadata = cell.get("metadata", {})
        if "execution" in metadata:
            del metadata["execution"]
            changed = True
    if changed:
        content = json.dumps(notebook, ensure_ascii=False, indent=1) + "\n"
        path.write_text(content, encoding="utf-8")
    return changed


def sanitize_notebooks(project_root: str | Path) -> list[Path]:
    notebook_root = Path(project_root).resolve() / "notebooks"
    changed = [path for path in sorted(notebook_root.glob("*.ipynb")) if sanitize_notebook(path)]
    return changed


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    return parser


def main() -> int:
    args = _parser().parse_args()
    changed = sanitize_notebooks(args.project_root)
    print(f"Sanitized {len(changed)} notebook(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
