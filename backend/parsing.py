import os
import re
import pdfplumber
import docx2txt


def clean_text(text: str) -> str:
    if not text:
        return ""
    # collapse multiple blank lines
    text = re.sub(r"\n\s*\n+", "\n", text)
    # normalize whitespace
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def extract_text_from_file(path: str) -> str:
    """Extract text from PDF / DOCX / TXT. Returns plain text (string).
    Keep this lightweight — for production extend with better PDF heuristics.
    """
    ext = os.path.splitext(path)[1].lower()
    text = ""
    try:
        if ext == ".pdf":
            with pdfplumber.open(path) as pdf:
                pages = []
                for p in pdf.pages:
                    t = p.extract_text()
                    if t:
                        pages.append(t)
                text = "\n".join(pages)
        elif ext in (".docx", ".doc"):
            text = docx2txt.process(path) or ""
        else:
            # fallback: try read as text
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
    except Exception:
        # best-effort fallback
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except Exception:
            text = ""

    return clean_text(text)