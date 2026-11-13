"""Build the N2 affix Anki deck from curated CSV data."""
from __future__ import annotations

import csv
import html
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import genanki

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "data"))
sys.path.insert(0, str(ROOT / "scripts"))

from affixes_source import AFFIXES  # noqa: E402
from furigana import SentenceRenderer  # noqa: E402

MODEL_ID = 1749202600
PARENT_DECK_ID = 1749202601
PREFIX_DECK_ID = 1749202602
SUFFIX_DECK_ID = 1749202603

DECK_DESCRIPTION = """N2 affixes with senses, compounds, and N2-level example sentences.

84 affixes (32 prefixes, 52 suffixes), 100 senses, 300 compounds, 168 sentences. One recognition card and two cloze cards per affix.

License and attribution:
- Deck data: CC BY-SA 4.0. You may redistribute and adapt the deck data under CC BY-SA 4.0 with attribution.
- Scripts: MIT.
- Tatoeba sentences: CC BY 2.0 FR, attributed by Japanese sentence ID on each card.
- JMdict readings and glosses: CC BY-SA 4.0, EDRDG.
- OpenJLPT level data: CC BY-SA 4.0.
- Source, license, and notices: https://github.com/ClemPera/n2-affixes"""

FIELDS = [
    "Affix",
    "RecognitionFront",
    "RecognitionBack",
    "Cloze1Front",
    "Cloze1Back",
    "Cloze2Front",
    "Cloze2Back",
]

CSS = """
.card {
  font-family: "Hiragino Sans", "Yu Gothic", "Noto Sans JP", system-ui, sans-serif;
  font-size: 18px;
  line-height: 1.65;
  color: #202124;
  background: #fbfaf7;
  text-align: left;
  padding: 18px;
}
.nightMode .card, .night_mode .card {
  color: #e8e6e3;
  background: #242426;
}
ruby rt {
  font-size: 0.55em;
  color: #6b6b6b;
}
.nightMode ruby rt, .night_mode ruby rt {
  color: #a8a8a8;
}
.affix {
  font-size: 64px;
  font-weight: 700;
  text-align: center;
  letter-spacing: 0.04em;
  margin: 18px 0 2px;
}
.reading {
  text-align: center;
  font-size: 22px;
  color: #666;
  margin-bottom: 10px;
}
.nightMode .reading, .night_mode .reading {
  color: #b0b0b0;
}
.badges {
  text-align: center;
  margin: 8px 0 20px;
}
.badge {
  display: inline-block;
  padding: 2px 10px;
  margin: 0 4px;
  border-radius: 999px;
  background: #e8e2d6;
  color: #4a4235;
  font-size: 13px;
  letter-spacing: 0.04em;
}
.nightMode .badge, .night_mode .badge {
  background: #3a3a3d;
  color: #d8d4cc;
}
.prompt {
  text-align: center;
  color: #777;
  font-size: 15px;
}
.affix-head {
  font-size: 34px;
  font-weight: 700;
  border-bottom: 2px solid #d9d2c5;
  padding-bottom: 8px;
  margin-bottom: 14px;
}
.nightMode .affix-head, .night_mode .affix-head {
  border-color: #444;
}
.section {
  margin: 18px 0;
}
.section-title {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #8a7f6d;
  margin-bottom: 8px;
}
.nightMode .section-title, .night_mode .section-title {
  color: #b3a894;
}
.sense {
  margin: 0 0 12px;
}
.sense-num {
  display: inline-block;
  min-width: 22px;
  font-weight: 700;
  color: #8a5a2b;
}
.sense-def {
  font-weight: 600;
}
.compounds {
  margin: 6px 0 0 22px;
  padding: 0;
}
.compounds li {
  margin: 3px 0;
}
.gloss {
  color: #555;
}
.nightMode .gloss, .night_mode .gloss {
  color: #b8b5ae;
}
.note, .contrast {
  border-left: 3px solid #c9b99a;
  padding: 8px 12px;
  margin: 14px 0;
  background: #f3efe6;
  border-radius: 0 6px 6px 0;
}
.nightMode .note, .nightMode .contrast,
.night_mode .note, .night_mode .contrast {
  background: #2f2f31;
  border-color: #5b5344;
}
.ex {
  margin: 14px 0;
  padding-bottom: 10px;
  border-bottom: 1px dashed #ddd6c8;
}
.nightMode .ex, .night_mode .ex {
  border-color: #444;
}
.ex:last-child {
  border-bottom: none;
}
.target {
  color: #8a2f1f;
  font-weight: 700;
}
.nightMode .target, .night_mode .target {
  color: #ff9a8a;
}
.en {
  color: #555;
  font-size: 15px;
}
.nightMode .en, .night_mode .en {
  color: #b8b5ae;
}
.source {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}
.source a {
  color: #7a6a55;
}
.blank {
  display: inline-block;
  min-width: 2.2em;
  text-align: center;
  border-bottom: 2px solid #8a5a2b;
  color: #8a5a2b;
  font-weight: 700;
}
.cloze-label {
  font-size: 13px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #8a7f6d;
  margin-bottom: 12px;
}
.cloze-sentence {
  font-size: 24px;
  line-height: 1.9;
  margin: 16px 0;
}
.cloze-en {
  color: #666;
  font-size: 16px;
  margin-top: 10px;
}
.nightMode .cloze-en, .night_mode .cloze-en {
  color: #b0b0b0;
}
.answer {
  font-size: 40px;
  font-weight: 700;
  margin-bottom: 4px;
}
.answer-reading {
  font-size: 20px;
  font-weight: 400;
  color: #777;
}
.full-sentence {
  font-size: 22px;
  line-height: 1.9;
  margin: 10px 0;
}
.def {
  margin-top: 10px;
  font-weight: 600;
}
"""

TEMPLATES = [
    {
        "name": "Recognition",
        "qfmt": "{{RecognitionFront}}",
        "afmt": "{{FrontSide}}<hr id=answer>{{RecognitionBack}}",
    },
    {
        "name": "Cloze 1",
        "qfmt": "{{Cloze1Front}}",
        "afmt": "{{FrontSide}}<hr id=answer>{{Cloze1Back}}",
    },
    {
        "name": "Cloze 2",
        "qfmt": "{{Cloze2Front}}",
        "afmt": "{{FrontSide}}<hr id=answer>{{Cloze2Back}}",
    },
]

MODEL = genanki.Model(
    MODEL_ID,
    "N2 Affix (Recognition + Cloze)",
    fields=[{"name": field} for field in FIELDS],
    templates=TEMPLATES,
    css=CSS,
    sort_field_index=0,
)


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def source_html(row: dict) -> str:
    if row["source"] == "Tatoeba":
        sentence_id = row["source_id"]
        url = f"https://tatoeba.org/en/sentences/show/{sentence_id}" if sentence_id else ""
        label = f"Tatoeba #{sentence_id}" if sentence_id else "Tatoeba"
        if url:
            return f'<a href="{url}">{label}</a> · CC-BY 2.0 FR'
        return f"{label} · CC-BY 2.0 FR"
    return "Original sentence"


def source_text(row: dict) -> str:
    if row["source"] == "Tatoeba":
        sentence_id = row["source_id"]
        return f"Tatoeba #{sentence_id} (CC-BY 2.0 FR)" if sentence_id else "Tatoeba (CC-BY 2.0 FR)"
    return "Original sentence"


def build() -> None:
    renderer = SentenceRenderer()

    compounds = list(csv.DictReader((ROOT / "data/compounds.csv").open(encoding="utf-8")))
    sentences = list(csv.DictReader((ROOT / "data/sentences.csv").open(encoding="utf-8")))

    compounds_by_affix: dict[str, list[dict]] = defaultdict(list)
    reading_by_word: dict[str, str] = {}
    for row in compounds:
        compounds_by_affix[row["affix_id"]].append(row)
        reading_by_word.setdefault(row["word"], row["reading"])

    sentences_by_affix: dict[str, list[dict]] = defaultdict(list)
    for row in sentences:
        sentences_by_affix[row["affix_id"]].append(row)

    parent = genanki.Deck(
        PARENT_DECK_ID,
        "Japanese::JLPT N2::Affixes",
        description=DECK_DESCRIPTION,
    )
    prefix_deck = genanki.Deck(
        PREFIX_DECK_ID,
        "Japanese::JLPT N2::Affixes::Prefixes",
        description="N2 prefixes.",
    )
    suffix_deck = genanki.Deck(
        SUFFIX_DECK_ID,
        "Japanese::JLPT N2::Affixes::Suffixes",
        description="N2 suffixes.",
    )

    review_rows = []
    manifest = {"affixes": 0, "prefixes": 0, "suffixes": 0, "notes": 0, "cards": 0}

    for affix in AFFIXES:
        affix_id = affix["id"]
        rows = sentences_by_affix[affix_id]
        if len(rows) != 2:
            raise SystemExit(f"{affix_id}: expected 2 sentences, got {len(rows)}")

        comps = compounds_by_affix[affix_id]
        comps_by_sense: dict[int, list[dict]] = defaultdict(list)
        for comp in comps:
            comps_by_sense[int(comp["sense"])].append(comp)

        sense_parts = []
        sense_def_parts = []
        for index, sense in enumerate(affix["senses"], 1):
            items = []
            for comp in comps_by_sense[index]:
                word = renderer.furigana.word(comp["word"], comp["reading"])
                items.append(
                    f'<li><span class="word">{word}</span> '
                    f'<span class="gloss">— {esc(comp["gloss"])}</span></li>'
                )
            sense_parts.append(
                f'<div class="sense"><span class="sense-num">{index}</span>'
                f'<span class="sense-def">{esc(sense["en"])}</span>'
                f'<ul class="compounds">{"".join(items)}</ul></div>'
            )
            sense_def_parts.append(
                f'<div class="sense"><span class="sense-num">{index}</span>'
                f'<span class="sense-def">{esc(sense["en"])}</span></div>'
            )
        senses_html = "".join(sense_parts)
        sense_defs_html = "".join(sense_def_parts)

        example_by_index = []
        for row in rows:
            reading = reading_by_word.get(row["compound"], "")
            ja = renderer.render(
                row["ja"],
                row["compound"],
                affix["affix"],
                reading=reading,
                bold=True,
            )
            example_by_index.append(
                f'<div class="ex"><div class="ja">{ja}</div>'
                f'<div class="en">{esc(row["en"])}</div>'
                f'<div class="source">{source_html(row)}</div></div>'
            )
        examples_html = "".join(example_by_index)

        notes_html = ""
        if affix.get("notes"):
            notes_html += f'<div class="note"><b>Usage:</b> {esc(affix["notes"])}</div>'
        if affix.get("contrast"):
            notes_html += f'<div class="contrast"><b>Contrast:</b> {esc(affix["contrast"])}</div>'

        recognition_front = (
            f'<div class="affix">{esc(affix["affix"])}</div>'
            f'<div class="reading">{esc(affix["reading"])}</div>'
            f'<div class="badges"><span class="badge">N2</span>'
            f'<span class="badge">{affix["type"]}</span></div>'
            f'<div class="prompt">Recall the meanings and common compounds.</div>'
        )
        recognition_back = (
            f'<div class="affix-head">{esc(affix["affix"])} '
            f'<span class="reading">({esc(affix["reading"])})</span></div>'
            f'<div class="section"><div class="section-title">Meanings</div>{senses_html}</div>'
            f'{notes_html}'
            f'<div class="section"><div class="section-title">Examples</div>{examples_html}</div>'
        )

        cloze_fields = []
        for index, row in enumerate(rows):
            reading = reading_by_word.get(row["compound"], "")
            blanked = renderer.render(
                row["ja"],
                row["compound"],
                affix["affix"],
                blank=True,
            )
            full = renderer.render(
                row["ja"],
                row["compound"],
                affix["affix"],
                reading=reading,
                bold=True,
            )
            sense_index = int(row["sense"]) - 1
            definition = affix["senses"][sense_index]["en"]
            cloze_fields.append(
                f'<div class="cloze-label">Fill in the missing affix · N2 '
                f'{affix["type"]}</div>'
                f'<div class="cloze-sentence">{blanked}</div>'
                f'<div class="cloze-en">{esc(row["en"])}</div>'
            )
            other = example_by_index[1 - index]
            cloze_fields.append(
                f'<div class="answer">{esc(affix["affix"])} '
                f'<span class="answer-reading">{esc(affix["reading"])}</span></div>'
                f'<div class="full-sentence">{full}</div>'
                f'<div class="en">{esc(row["en"])}</div>'
                f'<div class="def">{esc(definition)}</div>'
                f'<div class="source">{source_html(row)}</div>'
                f'<div class="section"><div class="section-title">All meanings</div>'
                f'{sense_defs_html}</div>'
                f'<div class="section"><div class="section-title">Another example</div>'
                f'{other}</div>'
            )

        tags = ["JLPT-N2", "n2-affix", "affix", f"type::{affix['type']}"]
        tags.extend(f"topic::{tag}" for tag in affix.get("tags", []))
        if any(row["source"] == "Tatoeba" for row in rows):
            tags.append("source::tatoeba")
        if any(row["source"] == "original" for row in rows):
            tags.append("source::original")

        note = genanki.Note(
            model=MODEL,
            fields=[
                affix["affix"],
                recognition_front,
                recognition_back,
                cloze_fields[0],
                cloze_fields[1],
                cloze_fields[2],
                cloze_fields[3],
            ],
            tags=tags,
            guid=genanki.guid_for("n2-affix", affix_id),
        )
        if affix["type"] == "prefix":
            prefix_deck.add_note(note)
            manifest["prefixes"] += 1
        else:
            suffix_deck.add_note(note)
            manifest["suffixes"] += 1

        manifest["affixes"] += 1
        manifest["notes"] += 1
        manifest["cards"] += 3

        compound_text = " | ".join(
            f'{index}: ' + "; ".join(
                f'{comp["word"]} ({comp["reading"]}) {comp["gloss"]}'
                for comp in comps_by_sense[index]
            )
            for index in sorted(comps_by_sense)
        )
        review_rows.append(
            {
                "id": affix_id,
                "affix": affix["affix"],
                "reading": affix["reading"],
                "type": affix["type"],
                "senses": " | ".join(
                    f'{index}: {sense["en"]}'
                    for index, sense in enumerate(affix["senses"], 1)
                ),
                "compounds": compound_text,
                "sentence_1": rows[0]["ja"],
                "english_1": rows[0]["en"],
                "source_1": source_text(rows[0]),
                "sentence_2": rows[1]["ja"],
                "english_2": rows[1]["en"],
                "source_2": source_text(rows[1]),
                "level_check": "ok" if all(row["check"] == "ok" for row in rows) else "FAIL",
            }
        )

    package = genanki.Package([parent, prefix_deck, suffix_deck])
    output = ROOT / "N2_affixes.apkg"
    package.write_to_file(str(output))

    review_csv = ROOT / "review/affixes_review.csv"
    with review_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(review_rows[0]))
        writer.writeheader()
        writer.writerows(review_rows)

    review_html = ROOT / "review/affixes_review.html"
    body = []
    for row in review_rows:
        body.append(
            f'<details><summary><b>{esc(row["affix"])}</b> '
            f'({esc(row["reading"])}) · {row["type"]} · {row["level_check"]}</summary>'
            f'<p><b>Meanings:</b> {esc(row["senses"])}</p>'
            f'<p><b>Compounds:</b> {esc(row["compounds"])}</p>'
            f'<p><b>1.</b> {esc(row["sentence_1"])}<br><i>{esc(row["english_1"])}</i>'
            f'<br><small>{esc(row["source_1"])}</small></p>'
            f'<p><b>2.</b> {esc(row["sentence_2"])}<br><i>{esc(row["english_2"])}</i>'
            f'<br><small>{esc(row["source_2"])}</small></p></details>'
        )
    review_html.write_text(
        "<!doctype html><meta charset='utf-8'><title>N2 affix review</title>"
        "<style>body{font-family:system-ui,sans-serif;max-width:1000px;margin:2rem auto;"
        "line-height:1.6;padding:0 1rem}details{margin:0.6rem 0;padding:0.6rem;"
        "border:1px solid #ddd;border-radius:6px}summary{cursor:pointer}</style>"
        f"<h1>N2 affix review ({len(review_rows)} affixes)</h1>"
        + "".join(body),
        encoding="utf-8",
    )

    (ROOT / "review/deck_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {output}")
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    build()
