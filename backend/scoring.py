# backend/scoring.py

def calculate_score(matched_count: int, total_skills: int, semantic_score: float, hard_weight: float = 0.6):
    """Combine hard-skill match percent and semantic score into final 0-100 score.

    hard_weight — fraction weight for skills (0..1). remainder goes to semantic.
    """
    skill_pct = (matched_count / total_skills) * 100 if total_skills and total_skills > 0 else 0.0
    final = round(hard_weight * skill_pct + (1 - hard_weight) * float(semantic_score), 2)

    if final >= 75:
        verdict = "High"
    elif final >= 50:
        verdict = "Medium"
    else:
        verdict = "Low"

    return final, verdict