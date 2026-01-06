from dataclasses import dataclass
from typing import List, Optional, Tuple
from docx import Document
from PyPDF2 import PdfReader

@dataclass
class ExtractedText:
    text: str
    pages: Optional[List[Tuple[int, str]]] = None  # (page_no, page_text) for PDFs

def extract_text_from_docx(file) -> ExtractedText:
    doc = Document(file)
    full_text = "\n".join(p.text for p in doc.paragraphs if p.text is not None)
    return ExtractedText(text=full_text, pages=None)

def extract_text_from_pdf(file, max_pages: int = 120) -> ExtractedText:
    reader = PdfReader(file)
    pages_out: List[Tuple[int, str]] = []

    limit = min(len(reader.pages), max_pages)
    for i in range(limit):
        text = reader.pages[i].extract_text() or ""
        pages_out.append((i + 1, text))

    combined = "\n".join(t for _, t in pages_out).strip()
    return ExtractedText(text=combined, pages=pages_out)
