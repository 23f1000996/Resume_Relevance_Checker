import re
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def hard_match(resume_text: str, skills: List[str]) -> Tuple[List[str], List[str]]:
    """Return (matched_skills, missing_skills).
    Uses simple word-boundary checks and a fallback 'all words present' check for multi-word skills.
    """
    resume_lower = (resume_text or "").lower()
    matched = []
    missing = []

    for s in skills:
        s_clean = s.strip()
        if not s_clean:
            continue
        # exact word boundary match
        pattern = r"\b" + re.escape(s_clean.lower()) + r"\b"
        if re.search(pattern, resume_lower):
            matched.append(s_clean)
            continue
        # fallback: check if all non-trivial tokens of skill appear in resume
        tokens = [t for t in re.findall(r"\w+", s_clean.lower()) if len(t) > 2]
        if tokens and all(tok in resume_lower for tok in tokens):
            matched.append(s_clean)
        else:
            missing.append(s_clean)

    return matched, missing


def semantic_match(resume_text: str, jd_text: str) -> float:
    """Return semantic similarity percent (0-100) using TF-IDF cosine similarity.
    This is a light-weight semantic proxy; for stronger semantics use embeddings.
    """
    try:
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
        vecs = vectorizer.fit_transform([resume_text or "", jd_text or ""])  # shape (2, n_features)
        score = float(cosine_similarity(vecs[0], vecs[1])[0][0])
        return round(score * 100, 2)
    except Exception:
        return 0.0