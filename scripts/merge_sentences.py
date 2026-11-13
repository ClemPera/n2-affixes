"""Merge Tatoeba picks with originals, guaranteeing two sentences per affix."""
from __future__ import annotations

import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "data"))
sys.path.insert(0, str(ROOT / "scripts"))
from affixes_source import AFFIXES  # noqa: E402
from jlpt_check import LevelChecker  # noqa: E402
from originals import ORIGINALS  # noqa: E402
from sentence_patches import PATCHES  # noqa: E402

DRAFT = ROOT / "data/sentences_draft.csv"
COMPOUNDS = ROOT / "data/compounds.csv"
OUT = ROOT / "data/sentences.csv"
TATOEBA = Path("/tmp/opencode/jpn.txt")


def main() -> None:
    checker = LevelChecker()
    tatoeba_ids = {}
    for line in TATOEBA.open(encoding="utf-8"):
        parts = line.rstrip("\n").split("\t")
        if len(parts) >= 3:
            ids = re.findall(r"#(\d+)", parts[2])
            if ids:
                # The attribution lists the English ID first, then the Japanese ID.
                tatoeba_ids.setdefault(parts[1], ids[-1])
    draft = list(csv.DictReader(DRAFT.open(encoding="utf-8")))
    compounds = list(csv.DictReader(COMPOUNDS.open(encoding="utf-8")))
    comp_by_affix = defaultdict(list)
    for row in compounds:
        comp_by_affix[row["affix_id"]].append(row)

    def find_compound(affix_id: str, sentence: str, sense: int) -> str:
        candidates = [
            comp["word"]
            for comp in comp_by_affix[affix_id]
            if int(comp["sense"]) == sense and comp["word"] in sentence
        ]
        if not candidates:
            candidates = [
                comp["word"] for comp in comp_by_affix[affix_id] if comp["word"] in sentence
            ]
        return candidates[0] if candidates else ""

    draft_by_affix = defaultdict(list)
    for row in draft:
        if row["source"] == "Tatoeba" and row["ja"]:
            draft_by_affix[row["affix_id"]].append(row)

    rows = []
    problems = []
    for affix in AFFIXES:
        affix_id = affix["id"]
        sense_count = len(affix["senses"])
        tat = draft_by_affix.get(affix_id, [])
        selected = []
        used_compounds = set()
        used_sentences = set()

        # forced replacements first
        for original in PATCHES.get(affix_id, []):
            if len(selected) >= 2 or original["ja"] in used_sentences:
                continue
            compound = find_compound(affix_id, original["ja"], original["sense"])
            if compound and compound in used_compounds:
                continue
            selected.append(
                {
                    "affix_id": affix_id,
                    "affix": affix["affix"],
                    "sense": original["sense"],
                    "ja": original["ja"],
                    "en": original["en"],
                    "source": "original",
                    "source_id": "",
                    "compound": compound,
                }
            )
            used_sentences.add(original["ja"])
            if compound:
                used_compounds.add(compound)

        # one distinct compound per sense first
        for sense in range(1, sense_count + 1):
            for row in tat:
                if int(row["sense"]) != sense:
                    continue
                if row["compound"] in used_compounds or row["ja"] in used_sentences:
                    continue
                selected.append(
                    {
                        "affix_id": affix_id,
                        "affix": affix["affix"],
                        "sense": sense,
                        "ja": row["ja"],
                        "en": row["en"],
                        "source": "Tatoeba",
                        "source_id": tatoeba_ids.get(row["ja"], ""),
                        "compound": row["compound"],
                    }
                )
                used_compounds.add(row["compound"])
                used_sentences.add(row["ja"])
                break

        # then an original for any sense still uncovered
        for sense in range(1, sense_count + 1):
            if len(selected) >= 2:
                break
            if any(row["sense"] == sense for row in selected):
                continue
            for original in ORIGINALS.get(affix_id, []):
                if original["sense"] != sense or original["ja"] in used_sentences:
                    continue
                selected.append(
                    {
                        "affix_id": affix_id,
                        "affix": affix["affix"],
                        "sense": sense,
                        "ja": original["ja"],
                        "en": original["en"],
                        "source": "original",
                        "source_id": "",
                        "compound": "",
                    }
                )
                used_sentences.add(original["ja"])
                break

        # then a second distinct compound from the corpus
        for row in tat:
            if len(selected) >= 2:
                break
            if row["compound"] in used_compounds or row["ja"] in used_sentences:
                continue
            selected.append(
                {
                    "affix_id": affix_id,
                    "affix": affix["affix"],
                    "sense": int(row["sense"]),
                    "ja": row["ja"],
                    "en": row["en"],
                    "source": "Tatoeba",
                    "source_id": tatoeba_ids.get(row["ja"], ""),
                    "compound": row["compound"],
                }
            )
            used_compounds.add(row["compound"])
            used_sentences.add(row["ja"])

        # finally any remaining original
        for original in ORIGINALS.get(affix_id, []):
            if len(selected) >= 2:
                break
            if original["ja"] in used_sentences:
                continue
            selected.append(
                {
                    "affix_id": affix_id,
                    "affix": affix["affix"],
                    "sense": original["sense"],
                    "ja": original["ja"],
                    "en": original["en"],
                    "source": "original",
                    "source_id": "",
                    "compound": "",
                }
            )
            used_sentences.add(original["ja"])

        if len(selected) < 2:
            problems.append((affix_id, "fewer than 2 sentences"))
            continue

        for row in selected[:2]:
            if not row["compound"]:
                candidates = [
                    c["word"]
                    for c in comp_by_affix[affix_id]
                    if int(c["sense"]) == row["sense"] and c["word"] in row["ja"]
                ]
                if not candidates:
                    candidates = [
                        c["word"] for c in comp_by_affix[affix_id] if c["word"] in row["ja"]
                    ]
                if not candidates:
                    problems.append((affix_id, f"no compound in: {row['ja']}"))
                    row["compound"] = comp_by_affix[affix_id][0]["word"]
                else:
                    row["compound"] = candidates[0]
            result = checker.check(row["ja"], allow=(row["compound"],))
            row["check"] = "ok" if result["ok"] else "|".join(
                result["unknown"] + result["n1"] + result["bad_kanji"]
            )
            rows.append(row)

    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "affix_id",
                "affix",
                "sense",
                "ja",
                "en",
                "source",
                "source_id",
                "compound",
                "check",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {OUT} ({len(rows)} rows)")
    bad = [r for r in rows if r["check"] != "ok"]
    print(f"level-check failures: {len(bad)}")
    for row in bad:
        print(f"  {row['affix']}: {row['check']} :: {row['ja']}")
    if problems:
        print("problems:")
        for problem in problems:
            print(" ", problem)


if __name__ == "__main__":
    main()
