Automated Resume Relevance Checker
This project is an AI-powered system designed to automate the process of evaluating resumes against job descriptions. It addresses the challenges faced by recruitment teams, such as delays in shortlisting, inconsistent judgments, and high manual workloads.

The system uses a hybrid scoring model that combines rule-based checks with a Large Language Model (LLM) to provide a comprehensive and consistent analysis. It is built with a Flask backend and a modern HTML/CSS/JS frontend.

Features
Resume & JD Upload: Easily upload job descriptions and resumes in .txt format.

Hybrid Scoring: A weighted scoring system that combines:

Hard Match: A keyword-based check for essential skills.

Soft Match: A semantic analysis using an LLM to understand context and relevance.

Evaluation Verdict: Provides a clear verdict (High, Medium, or Low suitability) based on the final relevance score.

Personalized Feedback: Highlights missing skills and offers actionable suggestions for students to improve their resumes.

Real-time Dashboard: A dynamic dashboard powered by Firestore that updates automatically with each new evaluation, providing a centralized view for the placement team.

Tech Stack
Backend

Python: The core programming language.

Flask: A micro web framework for building the backend APIs.

Firebase Admin SDK: For secure, server-side communication with Firestore.

Google Gemini API: The LLM used for the semantic analysis and personalized feedback.

Frontend

HTML: For the structure of the web application.

Tailwind CSS: A utility-first CSS framework for rapid and responsive styling.

JavaScript: Manages all client-side logic and API calls to the backend.

Database

Firestore: A NoSQL cloud database for storing and retrieving evaluation results in real-time.

Getting Started
Follow these steps to set up and run the project locally.

1. Clone the Repository

Start by cloning the project from GitHub.

git clone [https://github.com/your-username/your-repository-name.git](https://github.com/your-username/your-repository-name.git)
cd your-repository-name

2. Set up the Backend

First, you need to create a Python virtual environment and install the dependencies.

python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
pip install -r requirements.txt

3. Configure Firebase

To connect to your Firestore database, you need to set up a Firebase service account.

Go to your Firebase Project Settings > Service accounts.

Click Generate new private key and download the JSON file.

Place this JSON file in your project's root directory.

Set an environment variable in your terminal to point to this file. This command must be run in the same terminal session as your Flask app.

export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service_account_key.json"

4. Configure Gemini API

The backend requires an API key to access the Gemini API.

Obtain an API key from the Google AI Studio.

Set the API key as an environment variable in your terminal.

export GEMINI_API_KEY="your-gemini-api-key"

5. Run the Application

With all configurations in place, you can now start the Flask server.

flask run

The application will be accessible at http://127.0.0.1:5000 in your web browser.

Folder Structure
The project has a simple and clean folder structure:

.
├── app.py                  # The Flask backend
├── requirements.txt        # Python dependencies
└── templates/              # Folder for HTML templates
    └── index.html          # The frontend UI

