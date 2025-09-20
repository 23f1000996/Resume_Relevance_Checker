import streamlit as st
import requests
import json
from io import StringIO

# Set page config
st.set_page_config(page_title="Resume Relevance Checker", layout="wide")

st.title("Automated Resume Relevance Checker")
st.write("Upload a job description and resume to evaluate their match")

# File uploaders
jd_file = st.file_uploader("Upload Job Description (TXT)", type="txt")
resume_file = st.file_uploader("Upload Resume (TXT)", type="txt")

if st.button("Analyze") and jd_file and resume_file:
    # Read files
    jd_text = str(jd_file.read(), "utf-8")
    resume_text = str(resume_file.read(), "utf-8")
    
    # Prepare data for API (you'll need to set up a separate API endpoint)
    data = {
        "job_description": jd_text,
        "resume_text": resume_text
    }
    
    # Show loading
    with st.spinner("Analyzing resume..."):
        # Call your analysis API
        # You'll need to deploy your Flask app separately first
        response = requests.post("YOUR_FLASK_API_URL/analyze", json=data)
        
        if response.status_code == 200:
            result = response.json()
            
            # Display results
            st.subheader(f"Match Score: {result['score']}%")
            st.subheader(f"Verdict: {result['verdict']}")
            
            # Display matched skills
            st.subheader("Matched Skills")
            for skill in result['matched_skills']:
                st.success(f"✓ {skill}")
                
            # Display missing skills
            if result['missing_skills']:
                st.subheader("Missing Skills")
                for skill in result['missing_skills']:
                    st.error(f"✗ {skill}")
                    
            # Display feedback
            st.subheader("Personalized Feedback")
            st.info(result['feedback'])
        else:
            st.error("Error analyzing resume. Please try again.")
