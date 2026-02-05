# rag_app/core/rag/dimensions.py

import re
from typing import Dict, Optional, Tuple, List

ROOM_SYNONYMS = {
    "master bedroom": "M.BEDROOM",
    "m.bedroom": "M.BEDROOM",
    "mbedroom": "M.BEDROOM",
    "drawing room": "DRAWING",
    "drawing": "DRAWING",
    "living": "LIVING & DINING",
    "living & dining": "LIVING & DINING",
    "kitchen": "KITCHEN",
    "dining": "DINING",
    "toilet": "TOILET",
    "bathroom": "TOILET",
}

ROOM_LABEL_RE = re.compile(
    r"^(BED ROOM-\d+|M\.BEDROOM|DRAWING|KITCHEN|DINING|LIVING\s*&\s*DINING|TOILET-\d+|TOILET)\s*$",
    re.IGNORECASE,
)

FT_IN_RE = re.compile(r"(\d+)\s*'\s*(\d+)\s*\"\s*[xX]\s*(\d+)\s*'\s*(\d+)\s*\"", re.IGNORECASE)
IN_ONLY_RE = re.compile(r"(\d+)\s*[xX]\s*(\d+)\s*\"", re.IGNORECASE)


def _clean(s: str) -> str:
    return (s or "").strip().replace("°", "'")


def is_dimension_question(question: str) -> bool:
    q = (question or "").lower()
    keywords = ["dimension", "dimensions", "size", "length", "breadth", "lxb", "l x b"]
    rooms = list(ROOM_SYNONYMS.keys()) + ["bedroom", "toilet", "drawing", "kitchen", "dining"]
    return any(k in q for k in keywords) or any(r in q for r in rooms)


def normalize_room_from_question(question: str) -> Optional[str]:
    q = (question or "").lower()
    for k, v in ROOM_SYNONYMS.items():
        if k in q:
            return v
    return None


def _format_ft_in(a_ft: str, a_in: str, b_ft: str, b_in: str) -> str:
    return f"{a_ft} ft {a_in} in × {b_ft} ft {b_in} in"


def _format_in(a: str, b: str) -> str:
    return f"{a} in × {b} in"


def extract_room_dimension_from_text(text: str, wanted_room: str) -> Optional[Dict]:
    lines = [_clean(x) for x in (text or "").splitlines()]
    lines = [x for x in lines if x]

    wanted_room = wanted_room.upper().strip()
    pending = False

    for line in lines:
        if ROOM_LABEL_RE.match(line) and line.upper().strip() == wanted_room:
            pending = True
            continue

        if pending:
            line = _clean(line)

            m = FT_IN_RE.search(line)
            if m:
                a_ft, a_in, b_ft, b_in = m.groups()
                return {
                    "room": wanted_room,
                    "value": _format_ft_in(a_ft, a_in, b_ft, b_in),
                    "unit": "ft+in",
                    "raw": f"{a_ft}'{a_in}\" X {b_ft}'{b_in}\"",
                }

            m = IN_ONLY_RE.search(line)
            if m:
                a, b = m.groups()
                return {
                    "room": wanted_room,
                    "value": _format_in(a, b),
                    "unit": "in",
                    "raw": f'{a}" X {b}"',
                }

            pending = False

    return None


def best_dimension_from_retrieved(retrieved: List[dict], question: str) -> Optional[Tuple[Dict, dict]]:
    wanted = normalize_room_from_question(question)
    if not wanted:
        return None

    for r in retrieved:
        dim = extract_room_dimension_from_text(r.get("text", ""), wanted)
        if dim:
            return dim, r

    return None
