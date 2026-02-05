from pathlib import Path

def pdf_page_file_url(pdf_path: str, page_num: int) -> str:
    """
    Builds a link like:
    file:///E:/.../My-Home.pdf#page=10
    """
    p = Path(pdf_path).resolve()
    return p.as_uri() + f"#page={page_num}"
