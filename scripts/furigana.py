"""Render Japanese text as Anki ruby HTML."""
from __future__ import annotations

import re

import fugashi

KANJI = re.compile(r"[\u4e00-\u9fff々]")
KATAKANA = "ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶ"
HIRAGANA = "ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをんゔヵヶ"
KANA_MAP = str.maketrans(KATAKANA, HIRAGANA)


class Furigana:
    def __init__(self) -> None:
        self.tagger = fugashi.Tagger()

    @staticmethod
    def _hiragana(reading: str | None) -> str:
        return reading.translate(KANA_MAP) if reading else ""

    def word(self, surface: str, reading: str | None) -> str:
        """Ruby for one word, using its full dictionary reading."""
        if not surface or not reading:
            return surface
        if not KANJI.search(surface):
            return surface
        if surface == reading:
            return surface
        return self._ruby(surface, reading)

    def _ruby(self, surface: str, reading: str) -> str:
        out: list[str] = []
        si = 0
        ri = 0
        while si < len(surface):
            if not KANJI.match(surface[si]):
                out.append(surface[si])
                if ri < len(reading) and reading[ri] == surface[si]:
                    ri += 1
                si += 1
                continue
            end = si
            while end < len(surface) and KANJI.match(surface[end]):
                end += 1
            run = surface[si:end]
            if end < len(surface):
                anchor = surface[end]
                found = reading.find(anchor, ri)
                if found == -1:
                    out.append(f"{run}[{reading[ri:]}]" if reading[ri:] else run)
                    return "".join(out) + surface[end:]
                segment = reading[ri:found]
                out.append(f"{run}[{segment}]" if segment else run)
                ri = found
            else:
                segment = reading[ri:]
                out.append(f"{run}[{segment}]" if segment else run)
                ri = len(reading)
            si = end
        return "".join(out)

    def text(self, text: str) -> str:
        """Ruby for a whole sentence, token by token."""
        parts: list[str] = []
        for token in self.tagger(text):
            if any(ch.isascii() and (ch.isdigit() or ch.isalpha()) for ch in token.surface):
                parts.append(token.surface)
                continue
            feature = token.feature
            reading = self._hiragana(getattr(feature, "kana", None))
            parts.append(self.word(token.surface, reading))
        return "".join(parts)


class SentenceRenderer:
    """Render example sentences, optionally bolding or blanking the target affix."""

    def __init__(self) -> None:
        self.furigana = Furigana()

    def _segment(self, text: str) -> str:
        return self.furigana.text(text) if text else ""

    def render(
        self,
        sentence: str,
        compound: str,
        affix: str,
        *,
        reading: str | None = None,
        bold: bool = False,
        blank: bool = False,
    ) -> str:
        start = sentence.find(compound)
        if start == -1:
            raise ValueError(f"compound {compound!r} not found in {sentence!r}")
        end = start + len(compound)

        key = affix.replace("〜", "")
        relative = compound.rfind(key) if affix.startswith("〜") else compound.find(key)
        if relative == -1:
            raise ValueError(f"affix {affix!r} not found in {compound!r}")

        if blank:
            blank_start = start + relative
            return (
                sentence[:blank_start]
                + '<span class="blank">〔　〕</span>'
                + sentence[blank_start + len(key) :]
            )

        body = self.furigana.word(compound, reading) if reading else self._segment(compound)
        if bold:
            body = f'<b class="target">{body}</b>'
        before = self._segment(sentence[:start])
        after = self._segment(sentence[end:])
        return before + body + after
