import streamlit as st
import requests
import json
import os
import time

# Function to get Firebase credentials from a JSON file path
def get_firebase_credentials():
    """Reads Firebase credentials from a file path provided via an environment variable."""
    try:
        # Assumes the path to the service account key is set as a secret in Streamlit Cloud
        cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not cred_path:
            st.error("Environment variable GOOGLE_APPLICATION_CREDENTIALS not found.")
            return None, None
        
        with open(cred_path, "r") as f:
            creds = json.load(f)
            return creds, creds.get('project_id')
    except Exception as e:
        st.error(f"Error loading Firebase credentials: {e}")
        return None, None

# Try to initialize Firebase Admin SDK
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    
    # Check if Firebase app is already initialized
    if not firebase_admin._apps:
        creds, project_id = get_firebase_credentials()
        if creds:
            cred = credentials.Certificate(creds)
            firebase_admin.initialize_app(cred, {'projectId': project_id})
    
    db = firestore.client()
    st.success("Connected to Firestore successfully!")
except Exception as e:
    st.error(f"Error connecting to Firestore: {e}")
    db = None

# --- Gemini API Config ---
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"

# Function to call the LLM for semantic analysis
def get_llm_analysis(jd, resume):
    """
    Calls the Gemini API to get a soft match score and personalized feedback.
    """
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
        st.error(f"Error calling LLM API: {e}")
        return None

# --- Streamlit UI ---

st.set_page_config(
    page_title="Resume Relevance Checker",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Automated Resume Relevance Checker")
st.markdown("Automate resume evaluation against job requirements with an AI-powered system.")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.header("Upload & Analysis")
    st.subheader("Job Description")
    jd_file = st.file_uploader("Upload Job Description (.txt)", type=["txt"], key="jd_uploader")
    
    st.subheader("Resume")
    resume_file = st.file_uploader("Upload Resume (.txt)", type=["txt"], key="resume_uploader")
    
    hard_skills_input = st.text_input("Must-have Skills (for Hard Match)", placeholder="e.g., Python, SQL, Machine Learning")
    hard_skills = [s.strip() for s in hard_skills_input.split(',') if s.strip()]

    if st.button("Analyze Resume"):
        if not jd_file or not resume_file:
            st.error("Please upload both Job Description and Resume files.")
            st.stop()

        with st.spinner('Analyzing...'):
            jd_text = jd_file.read().decode("utf-8")
            resume_text = resume_file.read().decode("utf-8")
            
            # Step 1: Hard Match
            hard_match_count = sum(1 for skill in hard_skills if skill.lower() in resume_text.lower())
            hard_match_score = (hard_match_count / len(hard_skills)) * 100 if hard_skills else 0

            # Step 2: Semantic Match (LLM)
            llm_result = get_llm_analysis(jd_text, resume_text)
            
            if llm_result:
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
                        db.collection('evaluations').add({
                            'jd_text': jd_text,
                            'resume_text': resume_text,
                            'score': round(final_score),
                            'verdict': verdict,
                            'missing_skills': llm_result.get('missingSkills', []),
                            'suggestions': llm_result.get('suggestions', ''),
                            'timestamp': firestore.SERVER_TIMESTAMP
                        })
                        st.success("Analysis complete and saved to the dashboard!")
                    except Exception as e:
                        st.error(f"Failed to save to Firestore: {e}")
                
                # Store results in session state to display on the page
                st.session_state.result = {
                    "score": round(final_score),
                    "verdict": verdict,
                    "missingSkills": llm_result.get('missingSkills', []),
                    "suggestions": llm_result.get('suggestions', '')
                }
            else:
                st.session_state.result = None
                st.error("Failed to get analysis from the AI. Please try again.")

with col2:
    st.header("Evaluation Results")
    if "result" in st.session_state and st.session_state.result:
        result = st.session_state.result
        
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.metric(label="Relevance Score", value=f"{result['score']} / 100")
        
        with col_res2:
            verdict_color = "green" if "High" in result['verdict'] else "orange" if "Medium" in result['verdict'] else "red"
            st.subheader(f"Verdict: :{verdict_color}[{result['verdict']}]")

        st.subheader("Missing Key Elements")
        if result['missingSkills']:
            for skill in result['missingSkills']:
                st.markdown(f"- {skill}")
        else:
            st.markdown("All key skills found!")
            
        st.subheader("Suggestions for Improvement")
        st.markdown(result['suggestions'])
    else:
        st.info("Run an analysis to see results here.")

st.markdown("---")

# --- Dashboard Section ---
st.header("Placement Team Dashboard")
st.markdown("Live feed of all resume evaluations.")

if db:
    # Use a real-time listener or a cached function to get data
    @st.cache_data(ttl=10) # Cache for 10 seconds to reduce reads
    def get_evaluations():
        try:
            evaluations_ref = db.collection('evaluations').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(50)
            docs = evaluations_ref.stream()
            results = []
            for doc in docs:
                data = doc.to_dict()
                if 'timestamp' in data:
                    data['timestamp'] = data['timestamp'].isoformat()
                results.append(data)
            return results
        except Exception as e:
            st.error(f"Error fetching evaluations from Firestore: {e}")
            return []

    evals = get_evaluations()
    if evals:
        st.dataframe(evals, use_container_width=True)
    else:
        st.info("No evaluations found. Run an analysis to populate the dashboard.")
else:
    st.warning("Dashboard is not connected to Firestore.")
