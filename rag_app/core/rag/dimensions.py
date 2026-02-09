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

# Robust regex for dimensions
FT_IN_RE = re.compile(
    r"(\d+)\s*['1°]\s*(\d+)\s*[\"''\s1]*\s*[xX*]\s*(\d+)\s*['1°]\s*(\d+)\s*[\"''\s1]*", 
    re.IGNORECASE
)

IN_ONLY_RE = re.compile(r"(\d+)\s*[xX*]\s*(\d+)\s*[\"''\s]*", re.IGNORECASE)


def _clean(s: str) -> str:
    if not s:
        return ""
    s = s.replace("°", "'").replace("’", "'").replace("”", '"').replace("“", '"')
    s = s.replace("''", '"')
    return s.strip()


def is_dimension_question(question: str) -> bool:
    q = (question or "").lower()
    keywords = ["dimension", "dimensions", "size", "length", "breadth", "lxb", "l x b", "how big", "area", "measurement"]
    rooms = list(ROOM_SYNONYMS.keys()) + ["bedroom", "toilet", "drawing", "kitchen", "dining", "flat"]
    return any(k in q for k in keywords) or any(r in q for r in rooms)


def normalize_room_from_question(question: str) -> Optional[str]:
    q = (question or "").lower()
    for k, v in ROOM_SYNONYMS.items():
        if k in q:
            return v
    m = re.search(r"(bedroom\s*\d+)", q)
    if m:
        return m.group(1).upper()
    return None


def _format_ft_in(a_ft: str, a_in: str, b_ft: str, b_in: str) -> str:
    return f"{a_ft}' {a_in}\" x {b_ft}' {b_in}\""


def _format_in(a: str, b: str) -> str:
    return f"{a}\" x {b}\""


def extract_room_dimension_from_text(text: str, wanted_room: str) -> Optional[Dict]:
    lines = (text or "").splitlines()
    cleaned_lines = [_clean(line) for line in lines]
    
    wanted_room = wanted_room.upper().strip()
    
    for i, line in enumerate(cleaned_lines):
        # Check for room name or flat number in the line
        if wanted_room in line.upper() or wanted_room.replace(".", "") in line.upper():
            # Search current and next 3 lines
            for j in range(i, min(i + 4, len(cleaned_lines))):
                search_line = cleaned_lines[j]
                
                m = FT_IN_RE.search(search_line)
                if m:
                    a_ft, a_in, b_ft, b_in = m.groups()
                    return {
                        "room": wanted_room,
                        "value": _format_ft_in(a_ft, a_in, b_ft, b_in),
                        "unit": "ft+in",
                        "raw": search_line,
                    }

                m = IN_ONLY_RE.search(search_line)
                if m:
                    a, b = m.groups()
                    if int(a) > 0 and int(b) > 0:
                        return {
                            "room": wanted_room,
                            "value": _format_in(a, b),
                            "unit": "in",
                            "raw": search_line,
                        }

    return None


def best_dimension_from_retrieved(retrieved: List[dict], question: str) -> Optional[Tuple[Dict, dict]]:
    """
    Finds the best dimension match, prioritizing specific flat numbers if mentioned.
    """
    q = question.upper()
    
    # Check if a specific flat number is mentioned (e.g., "FLAT NO. 2")
    flat_match = re.search(r"(FLAT\s*NO\.?\s*\d+)", q)
    wanted_flat = flat_match.group(1) if flat_match else None
    
    wanted_room = normalize_room_from_question(question)
    
    for r in retrieved:
        text = r.get("text", "")
        
        # If user asked for a specific flat, prioritize chunks that mention it
        if wanted_flat and wanted_flat not in text.upper():
            continue
            
        if wanted_room:
            dim = extract_room_dimension_from_text(text, wanted_room)
            if dim:
                return dim, r
        else:
            # If no specific room, try common rooms
            for room in ["M.BEDROOM", "DRAWING", "KITCHEN", "LIVING & DINING"]:
                dim = extract_room_dimension_from_text(text, room)
                if dim:
                    return dim, r

    # Fallback: if we didn't find the flat-specific chunk, try without the flat filter
    if wanted_flat and wanted_room:
        for r in retrieved:
            dim = extract_room_dimension_from_text(r.get("text", ""), wanted_room)
            if dim:
                return dim, r

    return None
