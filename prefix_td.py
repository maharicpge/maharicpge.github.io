#!/usr/bin/env python3
"""
Dans tous les .qmd du dossier td/, transforme les liens :

    [**Chapitre 01 : Logique et raisonnement**](../cours/mpsi-chap01.qmd)

en :

    📝 [**Chapitre 01 : Logique et raisonnement**](../cours/mpsi-chap01.qmd)

Le préfixe 📝 n'est ajouté que s'il n'est pas déjà présent (idempotent).

Usage :
    ./prefix_td.py              # corrige (avec backup .bak)
    ./prefix_td.py --dry-run    # affiche sans modifier
    ./prefix_td.py --no-backup  # corrige sans .bak
"""

import re
import sys
import shutil
from pathlib import Path

# Ligne = [**Titre**](../cours/xxx.qmd)  — éventuellement déjà préfixée par 📝
PATTERN = re.compile(
    r"^(?P<prefix>📝\s*)?"
    r"\[\*\*(?P<titre>[^\]]+)\*\*\]"
    r"\((?P<path>\.\./cours/[^)]+\.qmd)\)[ \t]*$",
    re.MULTILINE,
)


def fix_content(content: str) -> tuple[str, int]:
    count = 0

    def repl(m: re.Match) -> str:
        nonlocal count
        if m.group("prefix"):          # déjà préfixé → on ne touche pas
            return m.group(0)
        count += 1
        return f"📝 {m.group(0)}"

    return PATTERN.sub(repl, content), count


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
    td = root / "td" if (root / "td").is_dir() else root

    if not td.is_dir():
        print(f"Dossier introuvable : {td}")
        sys.exit(1)

    qmds = sorted(p for p in td.rglob("*.qmd") if p.is_file())
    if not qmds:
        print(f"Aucun .qmd trouvé dans {td}")
        sys.exit(0)

    total = 0
    changed_files = 0

    for q in qmds:
        n = process_file(q, dry_run=dry_run, backup=backup)
        if n == 0:
            continue
        changed_files += 1
        total += n
        tag = "⚠ à préfixer" if dry_run else "✓ préfixé"
        print(f"{tag} : {q.relative_to(root)}  ({n} lien(s))")

    print()
    if dry_run:
        print(f"{len(qmds)} fichiers analysés — {changed_files} à modifier, "
              f"{total} lien(s). Mode --dry-run.")
    else:
        print(f"{len(qmds)} fichiers analysés — {changed_files} modifié(s), "
              f"{total} lien(s) préfixé(s).")

    sys.exit(1 if changed_files else 0)


if __name__ == "__main__":
    main()
