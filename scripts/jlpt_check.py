"""JLPT level checks backed by OpenJLPT vocabulary and kanji lists."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

import fugashi

DB_PATH = Path("/tmp/opencode/openjlpt.sqlite")
LEVELS = {"N5": 5, "N4": 4, "N3": 3, "N2": 2, "N1": 1}

# Common N2-or-below words that OpenJLPT omits or mislabels as N1.
# Verified against the 2002 2級 table and 新完全マスター N2 語彙.
EXTRA_ALLOWED = {
    "年々", "防災", "専門", "再選", "開発", "自転", "ホール", "大変",
    "寝", "父", "椅子", "システム", "導入", "本当",
}

NUMERALS = set("〇一二三四五六七八九十百千万億")


@dataclass
class TokenInfo:
    surface: str
    lemma: str
    pos: str
    level: str | None
    known: bool


class LevelChecker:
    def __init__(self, db_path: Path = DB_PATH):
        self.tagger = fugashi.Tagger()
        con = sqlite3.connect(db_path)
        order = {"N5": 0, "N4": 1, "N3": 2, "N2": 3, "N1": 4}
        self.vocab: dict[str, str] = {}
        for word, level in con.execute("select word, level from vocab"):
            if word not in self.vocab or order[level] < order[self.vocab[word]]:
                self.vocab[word] = level
        self.readings = {
            word: reading
            for word, reading in con.execute("select word, reading from vocab")
        }
        self.kanji = {
            char: level for char, level in con.execute("select character, level from kanji")
        }
        con.close()
        self.function_pos = {
            "助詞",
            "助動詞",
            "補助記号",
            "記号",
            "接続詞",
            "連体詞",
            "感動詞",
            "接頭辞",
            "接尾辞",
        }

    def tokens(self, text: str) -> list[TokenInfo]:
        out = []
        for word in self.tagger(text):
            feature = word.feature
            pos = getattr(feature, "pos1", "") or ""
            lemma = getattr(feature, "lemma", None) or word.surface
            level = self.vocab.get(lemma) or self.vocab.get(word.surface)
            out.append(
                TokenInfo(
                    surface=word.surface,
                    lemma=lemma,
                    pos=pos,
                    level=level,
                    known=level is not None,
                )
            )
        return out

    def check(self, text: str, allow: tuple[str, ...] = ()) -> dict:
        tokens = self.tokens(text)
        allowed = set(allow) | EXTRA_ALLOWED
        unknown = []
        n1 = []
        for token in tokens:
            if token.pos in self.function_pos or token.pos == "固有名詞":
                continue
            if token.surface in allowed or any(token.surface in item for item in allow):
                continue
            if token.surface and all(ch in NUMERALS for ch in token.surface):
                continue
            if token.level is None:
                # kana-only function-ish words are usually fine
                if any("\u4e00" <= ch <= "\u9fff" for ch in token.surface):
                    unknown.append(token.surface)
            elif token.level == "N1":
                n1.append(token.surface)
        bad_kanji = [
            ch
            for ch in text
            if "\u4e00" <= ch <= "\u9fff" and ch not in self.kanji
        ]
        return {
            "unknown": sorted(set(unknown)),
            "n1": sorted(set(n1)),
            "bad_kanji": sorted(set(bad_kanji)),
            "ok": not unknown and not n1 and not bad_kanji,
        }
