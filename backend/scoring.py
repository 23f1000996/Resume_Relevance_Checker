def calculate_score(hard_score, semantic_score, total_skills, matched_skills):
    hard_weight, semantic_weight = 0.6, 0.4
    skill_score = (len(matched_skills) / total_skills) * 100 if total_skills > 0 else 0
    
    final_score = (hard_weight * skill_score) + (semantic_weight * semantic_score)
    
    if final_score > 75:
        verdict = "High"
    elif final_score > 50:
        verdict = "Medium"
    else:
        verdict = "Low"
    
    return round(final_score, 2), verdict

