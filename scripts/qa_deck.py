"""Inspect the generated .apkg and assert structural invariants."""
from __future__ import annotations

import json
import sqlite3
import sys
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APKG = ROOT / "N2_affixes.apkg"
REPORT = ROOT / "review/qa_report.txt"


def fail(message: str) -> None:
    raise SystemExit(f"QA FAIL: {message}")


def main() -> None:
    lines: list[str] = []
    with zipfile.ZipFile(APKG) as archive:
        names = archive.namelist()
        lines.append(f"package: {APKG.name} ({APKG.stat().st_size} bytes)")
        lines.append(f"entries: {', '.join(names)}")
        collection_name = "collection.anki21" if "collection.anki21" in names else "collection.anki2"
        if collection_name not in names:
            fail("no collection database in package")
        archive.extract(collection_name, ROOT / "review/.qa")
    db_path = ROOT / "review/.qa" / collection_name

    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    notes = list(con.execute("select id, guid, mid, tags, flds from notes"))
    cards = list(con.execute("select id, nid, did, ord from cards"))
    decks = json.loads(con.execute("select decks from col").fetchone()[0])
    models = json.loads(con.execute("select models from col").fetchone()[0])
    con.close()

    if len(notes) != 84:
        fail(f"expected 84 notes, got {len(notes)}")
    if len(cards) != 252:
        fail(f"expected 252 cards, got {len(cards)}")
    if len({note["guid"] for note in notes}) != len(notes):
        fail("duplicate note GUIDs")

    ords = Counter(card["ord"] for card in cards)
    for expected in (0, 1, 2):
        if ords[expected] != 84:
            fail(f"card ord {expected}: expected 84, got {ords[expected]}")
    per_note = Counter(card["nid"] for card in cards)
    if set(per_note.values()) != {3}:
        fail(f"notes do not all have 3 cards: {Counter(per_note.values())}")

    deck_names = {deck["name"] for deck in decks.values()}
    for expected in (
        "Japanese::JLPT N2::Affixes",
        "Japanese::JLPT N2::Affixes::Prefixes",
        "Japanese::JLPT N2::Affixes::Suffixes",
    ):
        if expected not in deck_names:
            fail(f"missing deck {expected}")

    model = next(iter(models.values()))
    if len(model["tmpls"]) != 3:
        fail(f"expected 3 card templates, got {len(model['tmpls'])}")
    lines.append(f"model: {model['name']} ({len(model['flds'])} fields, {len(model['tmpls'])} templates)")
    lines.append(f"decks: {sorted(deck_names)}")

    affix_values = []
    tags_ok = True
    for note in notes:
        fields = note["flds"].split("\x1f")
        if len(fields) != 7:
            fail(f"note {note['id']} has {len(fields)} fields")
        if any(not field.strip() for field in fields):
            fail(f"note {note['id']} has an empty field")
        affix, recognition_front, recognition_back, c1f, c1b, c2f, c2b = fields
        affix_values.append(affix)
        if "class=\"affix\"" not in recognition_front:
            fail(f"{affix}: recognition front missing affix block")
        if "section-title" not in recognition_back or "class=\"ex\"" not in recognition_back:
            fail(f"{affix}: recognition back missing meanings/examples")
        for label, front, back in (("cloze 1", c1f, c1b), ("cloze 2", c2f, c2b)):
            if "class=\"blank\"" not in front:
                fail(f"{affix}: {label} front has no blank")
            if "class=\"answer\"" not in back or "class=\"full-sentence\"" not in back:
                fail(f"{affix}: {label} back incomplete")
        tags = note["tags"].split()
        if "JLPT-N2" not in tags or "n2-affix" not in tags:
            tags_ok = False
    if not tags_ok:
        fail("missing core tags")
    if len(set(affix_values)) != 84:
        fail("duplicate affix values")
    if not any("type::prefix" in note["tags"] for note in notes):
        fail("no prefix tags")
    if not any("type::suffix" in note["tags"] for note in notes):
        fail("no suffix tags")

    lines.append(f"notes: {len(notes)}")
    lines.append(f"cards: {len(cards)} (ord 0={ords[0]}, ord 1={ords[1]}, ord 2={ords[2]})")
    lines.append(f"unique GUIDs: {len({note['guid'] for note in notes})}")
    lines.append(f"unique affixes: {len(set(affix_values))}")
    lines.append(f"tagged notes: {sum(1 for note in notes if 'JLPT-N2' in note['tags'])}")
    lines.append("result: PASS")

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
