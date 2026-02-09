from pathlib import Path

def pdf_page_file_url(doc_id: str, page: int) -> str:
    """
    Build a PDF link from doc_id and page number.
    Updated to use the public URL for the My Home Tridasa brochure.
    """
    # Public URL provided by the user
    base_url = "https://www.myhomeconstructions.com/wp-content/themes/sdna/broucher/My-Home-Tridasa-E-Brochure.pdf"
    
    # Appending the page fragment for direct navigation
    return f"{base_url}#page={page}"
