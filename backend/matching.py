import re
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nlp = spacy.load("en_core_web_sm")

def hard_match(resume_text, jd_text, skills):
    matches = []
    for skill in skills:
        if re.search(skill.lower(), resume_text.lower()):
            matches.append(skill)
    return matches

def semantic_match(resume_text, jd_text):
    vectorizer = TfidfVectorizer().fit([resume_text, jd_text])
    vectors = vectorizer.transform([resume_text, jd_text])
    score = cosine_similarity(vectors[0], vectors[1])[0][0]
    return round(score * 100, 2)
