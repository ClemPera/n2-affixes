"""Enrich every curated compound with a JMdict reading and gloss."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "data"))
sys.path.insert(0, str(ROOT / "scripts"))
from affixes_source import AFFIXES  # noqa: E402
from jmdict_lookup import load_jmdict  # noqa: E402

OVERRIDES = {
    "各学校": ("かくがっこう", "each school"),
    "各地域": ("かくちいき", "each region"),
    "各分野": ("かくぶんや", "each field"),
    "諸費用": ("しょひよう", "various expenses"),
    "現市長": ("げんしちょう", "current mayor"),
    "元歌手": ("もとかしゅ", "former singer"),
    "前社長": ("ぜんしゃちょう", "former president"),
    "別方向": ("べつほうこう", "different direction"),
    "異分野": ("いぶんや", "different field"),
    "20代": ("にじゅうだい", "twenties"),
    "30代": ("さんじゅうだい", "thirties"),
    "50代": ("ごじゅうだい", "fifties"),
    "洗面具": ("せんめんぐ", "washing utensils"),
    "活用法": ("かつようほう", "usage method"),
    "地域別": ("ちいきべつ", "by region"),
    "年齢別": ("ねんれいべつ", "by age"),
    "男女差": ("だんじょさ", "gender difference"),
    "海外向け": ("かいがいむけ", "aimed at overseas"),
    "完売済み": ("かんばいずみ", "sold out"),
    "遅れがち": ("おくれがち", "tends to be late"),
    "疲れ気味": ("つかれぎみ", "slightly tired"),
    "通り沿い": ("とおりぞい", "along the street"),
    "海岸沿い": ("かいがんぞい", "along the coast"),
    "成長ぶり": ("せいちょうぶり", "growth pattern"),
    "三年ぶり": ("さんねんぶり", "first in three years"),
    "十年ぶり": ("じゅうねんぶり", "first in ten years"),
}


def main() -> None:
    lookup = load_jmdict()
    rows = []
    missing = []
    for affix in AFFIXES:
        for sense_index, sense in enumerate(affix["senses"], 1):
            for word in sense["compounds"]:
                value = lookup.get(word) or OVERRIDES.get(word)
                if not value:
                    missing.append(word)
                    continue
                reading, glosses = value
                if isinstance(glosses, str):
                    gloss = glosses
                else:
                    gloss = "; ".join(glosses)
                rows.append(
                    (
                        affix["id"],
                        affix["affix"],
                        sense_index,
                        word,
                        reading,
                        gloss,
                    )
                )
    if missing:
        raise SystemExit(f"missing readings/glosses: {missing}")
    with (ROOT / "data/compounds.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["affix_id", "affix", "sense", "word", "reading", "gloss"])
        writer.writerows(rows)
    print(f"wrote {len(rows)} compounds")


if __name__ == "__main__":
    main()
