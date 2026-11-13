"""Pick up to two Tatoeba sentences per affix, one per sense where possible."""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from jlpt_check import LevelChecker

ROOT = Path(__file__).resolve().parent.parent
CANDIDATES = ROOT / "data/tatoeba_candidates.json"
COMPOUNDS = ROOT / "data/compounds.csv"
OUT = ROOT / "data/sentences_draft.csv"

PROPER = re.compile(r"トム|メアリー|ボストン|ジャクソン|アメリカ|フランス|インド|日本|中国")


def score(sentence: str, compound: str, used_compounds: set[str]) -> tuple:
    return (
        1 if compound in used_compounds else 0,
        1 if PROPER.search(sentence) else 0,
        abs(len(sentence) - 26),
        len(sentence),
    )


def main() -> None:
    checker = LevelChecker()
    candidates = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    compounds = list(csv.DictReader(COMPOUNDS.open(encoding="utf-8")))

    by_affix = defaultdict(list)
    for row in compounds:
        by_affix[row["affix_id"]].append(row)

    by_word = defaultdict(list)
    for row in candidates:
        if row["ok"]:
            by_word[row["word"]].append(row)

    rows = []
    for affix_id, comps in by_affix.items():
        affix = comps[0]["affix"]
        senses = sorted({int(c["sense"]) for c in comps})
        selected = []
        used_sentences = set()
        used_compounds = set()

        # one sentence per sense first
        for sense in senses:
            sense_comps = [c for c in comps if int(c["sense"]) == sense]
            pool = []
            for comp in sense_comps:
                for cand in by_word.get(comp["word"], []):
                    pool.append((comp["word"], cand))
            pool.sort(key=lambda x: score(x[1]["ja"], x[0], used_compounds))
            for word, cand in pool:
                if cand["ja"] in used_sentences:
                    continue
                selected.append(
                    {
                        "affix_id": affix_id,
                        "affix": affix,
                        "sense": sense,
                        "ja": cand["ja"],
                        "en": cand["en"],
                        "source": "Tatoeba",
                        "source_url": "",
                        "compound": word,
                        "needs_original": "",
                    }
                )
                used_sentences.add(cand["ja"])
                used_compounds.add(word)
                break

        # then add a second sentence from any sense
        if len(selected) < 2:
            pool = []
            for comp in comps:
                for cand in by_word.get(comp["word"], []):
                    if cand["ja"] in used_sentences:
                        continue
                    pool.append((comp["word"], cand, int(comp["sense"])))
            pool.sort(key=lambda x: score(x[1]["ja"], x[0], used_compounds))
            for word, cand, sense in pool:
                selected.append(
                    {
                        "affix_id": affix_id,
                        "affix": affix,
                        "sense": sense,
                        "ja": cand["ja"],
                        "en": cand["en"],
                        "source": "Tatoeba",
                        "source_url": "",
                        "compound": word,
                        "needs_original": "",
                    }
                )
                used_sentences.add(cand["ja"])
                break

        if len(selected) < 2:
            selected.append(
                {
                    "affix_id": affix_id,
                    "affix": affix,
                    "sense": selected[-1]["sense"] if selected else 1,
                    "ja": "",
                    "en": "",
                    "source": "original",
                    "source_url": "",
                    "compound": comps[0]["word"],
                    "needs_original": "yes",
                }
            )
        rows.extend(selected)

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
                "source_url",
                "compound",
                "needs_original",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} rows)")
    missing = sorted({r['affix'] for r in rows if r['needs_original']})
    print(f"affixes needing originals: {len(missing)}")
    print(", ".join(missing))


if __name__ == "__main__":
    main()
