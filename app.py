from flask import Flask, request, jsonify, render_template
import requests
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Flask app
app = Flask(__name__)

# --- Firebase Initialization ---
# The Firebase Admin SDK will automatically look for the file path in the GOOGLE_APPLICATION_CREDENTIALS environment variable
try:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase Admin SDK initialized successfully.")
except Exception as e:
    print(f"Error initializing Firebase Admin SDK: {e}")
    # Fallback for local testing without proper credentials, but functionality will be limited
    db = None

# --- Gemini API Config ---
# For this example, we assume the API key is set as an environment variable
# In a real-world scenario, you would use a secure method to store the API key.
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"
# --- End of Gemini API Config ---

# Function to call the LLM for semantic analysis
def get_llm_analysis(jd, resume):
    system_prompt = """You are an AI-powered resume evaluation engine. Your task is to analyze a given resume against a job description. You must provide a "soft" relevance score (0-100), identify missing skills, and give personalized improvement suggestions for the student. The soft score should reflect semantic fit and overall relevance, not just keyword presence. Missing skills should be based on the JD. Respond ONLY with a JSON object.
    
    JSON schema:
    {
      "softMatchScore": number,
      "missingSkills": string[],
      "suggestions": string
    }
    """
    
    user_query = f"Job Description:\n{jd}\n\nResume:\n{resume}"
    
    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {"responseMimeType": "application/json"}
    }

    headers = {'Content-Type': 'application/json'}
    params = {'key': GEMINI_API_KEY}

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, params=params, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        json_string = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text')
        if json_string:
            return json.loads(json_string)
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error calling LLM API: {e}")
        return None

@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/analyze_resume', methods=['POST'])
def analyze_resume():
    data = request.json
    jd_text = data.get('jdText', '')
    resume_text = data.get('resumeText', '')
    hard_skills = data.get('hardSkills', [])
    
    if not jd_text or not resume_text:
        return jsonify({"error": "Please provide both JD and resume text."}), 400

    # Step 1: Hard Match
    hard_match_count = sum(1 for skill in hard_skills if skill.lower() in resume_text.lower())
    hard_match_score = (hard_match_count / len(hard_skills)) * 100 if hard_skills else 0

    # Step 2: Semantic Match (LLM)
    llm_result = get_llm_analysis(jd_text, resume_text)
    if not llm_result:
        return jsonify({"error": "Failed to get analysis from the AI."}), 500
    
    soft_match_score = llm_result.get('softMatchScore', 0)
    
    # Step 3: Weighted Scoring
    final_score = (hard_match_score * 0.4) + (soft_match_score * 0.6)
    
    verdict = 'Low Suitability'
    if final_score >= 80:
        verdict = 'High Suitability'
    elif final_score >= 50:
        verdict = 'Medium Suitability'
        
    # Store results in Firestore
    if db:
        try:
            doc_ref = db.collection('evaluations').add({
                'jd_text': jd_text,
                'resume_text': resume_text,
                'score': round(final_score),
                'verdict': verdict,
                'missing_skills': llm_result.get('missingSkills', []),
                'suggestions': llm_result.get('suggestions', ''),
                'timestamp': firestore.SERVER_TIMESTAMP
            })
            print(f"Evaluation saved to Firestore with ID: {doc_ref[1].id}")
        except Exception as e:
            print(f"Error saving to Firestore: {e}")
    
    return jsonify({
        "score": round(final_score),
        "verdict": verdict,
        "missingSkills": llm_result.get('missingSkills', []),
        "suggestions": llm_result.get('suggestions', '')
    })

@app.route('/evaluations', methods=['GET'])
def get_evaluations():
    if not db:
        return jsonify({"error": "Database not configured."}), 500
    try:
        evaluations_ref = db.collection('evaluations').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(50)
        docs = evaluations_ref.stream()
        results = []
        for doc in docs:
            data = doc.to_dict()
            if 'timestamp' in data:
                data['timestamp'] = data['timestamp'].isoformat()
            results.append(data)
        return jsonify(results)
    except Exception as e:
        print(f"Error fetching evaluations from Firestore: {e}")
        return jsonify({"error": "Failed to fetch evaluations"}), 500

if __name__ == '__main__':
    app.run(debug=True)
