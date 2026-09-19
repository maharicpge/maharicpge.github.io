#!/usr/bin/env python3
"""
Corrige uniquement le motif collé :

    ....qmd)## Navigation {-}

en :

    ....qmd)

    ## Navigation {-}

Usage :
    ./verif_fix.py              # corrige (avec backup .bak)
    ./verif_fix.py --dry-run    # affiche sans modifier
    ./verif_fix.py --no-backup  # corrige sans .bak
"""

import re
import sys
import shutil
from pathlib import Path

# Motif exact : "qmd)" immédiatement suivi de "## Navigation {-}"
PATTERN = re.compile(r"(qmd\))(## Navigation \{-})")


def fix_content(content: str) -> tuple[str, int]:
    """Retourne (nouveau_contenu, nombre_de_remplacements)."""
    new_content, n = PATTERN.subn(r"\1\n\n\2", content)
    return new_content, n


def process_file(path: Path, dry_run: bool, backup: bool) -> int:
    content = path.read_text(encoding="utf-8")
    new_content, n = fix_content(content)
    if n == 0:
        return 0
    if not dry_run:
        if backup:
            shutil.copy2(path, str(path) + ".bak")
        path.write_text(new_content, encoding="utf-8")
    return n


def main() -> None:
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    backup = "--no-backup" not in args
    paths = [a for a in args if not a.startswith("--")]

    root = Path(paths[0]).resolve() if paths else Path.cwd()
    cours = root / "cours" if (root / "cours").is_dir() else root

    qmds = sorted(p for p in cours.rglob("*.qmd") if p.is_file())
    if not qmds:
        print(f"Aucun .qmd trouvé dans {cours}")
        sys.exit(0)

    total = 0
    bad_files = 0

    for q in qmds:
        n = process_file(q, dry_run=dry_run, backup=backup)
        if n == 0:
            continue
        bad_files += 1
        total += n
        tag = "⚠ à corriger" if dry_run else "✓ corrigé"
        print(f"{tag} : {q.relative_to(root)}  ({n} occurrence(s))")

    print()
    if dry_run:
        print(f"{len(qmds)} fichiers analysés — {bad_files} à corriger, "
              f"{total} occurrence(s). Mode --dry-run.")
    else:
        print(f"{len(qmds)} fichiers analysés — {bad_files} corrigé(s), "
              f"{total} occurrence(s).")

    sys.exit(1 if bad_files else 0)


if __name__ == "__main__":
    main()
