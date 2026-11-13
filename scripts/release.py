"""Bump the deck version, rebuild the package, and run QA."""

from __future__ import annotations

import argparse
import datetime
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = ROOT / "VERSION"
CHANGELOG = ROOT / "CHANGELOG.md"
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


def run(script: str) -> None:
    subprocess.run([sys.executable, str(ROOT / "scripts" / script)], check=True, cwd=ROOT)


def update_changelog(version: str, note: str) -> None:
    today = datetime.date.today().isoformat()
    entry = f"## {version} - {today}\n\n- {note}\n"

    if CHANGELOG.exists():
        text = CHANGELOG.read_text(encoding="utf-8")
    else:
        text = "# Changelog\n"

    if f"## {version} " in text:
        raise SystemExit(f"Version {version} already exists in CHANGELOG.md")

    if text.startswith("# Changelog"):
        header, _, rest = text.partition("\n")
        text = f"{header}\n\n{entry}\n{rest.lstrip()}"
    else:
        text = f"# Changelog\n\n{entry}\n{text}"

    CHANGELOG.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="new version, for example 1.1.0")
    parser.add_argument("--note", default="Deck update.", help="changelog entry")
    args = parser.parse_args()

    if not VERSION_PATTERN.match(args.version):
        raise SystemExit("Version must look like 1.1.0")

    update_changelog(args.version, args.note)
    VERSION_FILE.write_text(args.version + "\n", encoding="utf-8")

    run("build_deck.py")
    run("qa_deck.py")

    print()
    print(f"Built N2_affixes.apkg version {args.version}.")
    print("Next steps:")
    print("1. Import N2_affixes.apkg into Anki.")
    print("2. Sync to AnkiWeb.")
    print("3. On AnkiWeb, share the same deck name again.")
    print("4. Commit and push the repository.")


if __name__ == "__main__":
    main()
