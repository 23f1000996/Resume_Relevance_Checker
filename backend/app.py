from flask import Flask, request, jsonify
from parsing import extract_text
from matching import hard_match, semantic_match
from scoring import calculate_score
from database import init_db, insert_result

app = Flask(__name__)
init_db()

@app.route("/evaluate", methods=["POST"])
def evaluate_resume():
    jd_text = request.form["jd"]
    resume_file = request.files["resume"]
    student_name = request.form["name"]
    job_title = request.form["job_title"]
    skills = request.form.get("skills", "").split(",")

    resume_text = extract_text(resume_file)
    matched_skills = hard_match(resume_text, jd_text, skills)
    semantic_score = semantic_match(resume_text, jd_text)
    final_score, verdict = calculate_score(len(matched_skills), semantic_score, len(skills), matched_skills)
    
    missing_skills = [s for s in skills if s not in matched_skills]
    insert_result(job_title, student_name, final_score, verdict, missing_skills)

    return jsonify({
        "student": student_name,
        "job": job_title,
        "score": final_score,
        "verdict": verdict,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    })

if __name__ == "__main__":
    app.run(debug=True)
