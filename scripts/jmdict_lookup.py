"""Build an English JMdict lookup keyed by headword."""
from __future__ import annotations

import gzip
import xml.etree.ElementTree as ET
from pathlib import Path

JMDICT_PATH = Path("/tmp/opencode/JMdict_e.gz")
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"


def load_jmdict(path: Path = JMDICT_PATH) -> dict[str, tuple[str, list[str]]]:
    root = ET.fromstring(gzip.open(path, "rb").read())
    lookup: dict[str, tuple[str, list[str]]] = {}
    for entry in root:
        kebs = [x.text for x in entry.findall("k_ele/keb") if x.text]
        rebs = [x.text for x in entry.findall("r_ele/reb") if x.text]
        senses = []
        for sense in entry.findall("sense"):
            glosses = [
                g.text
                for g in sense.findall("gloss")
                if g.text and g.get(XML_LANG) in (None, "eng")
            ]
            if glosses:
                senses.append(glosses[0])
        value = (rebs[0] if rebs else "", senses[:3])
        for key in kebs or rebs:
            lookup.setdefault(key, value)
    return lookup
