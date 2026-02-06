def needs_images(question: str) -> bool:
    q = (question or "").lower()
    keywords = [
        "plan",
        "layout",
        "floor",
        "image",
        "show",
        "see",
        "design",
        "dimensions",
        "size",
        "drawing",
        "bedroom",
    ]
    return any(k in q for k in keywords)
