Here’s a concise version of your **Automated Resume Relevance Checker** README in Markdown:

````markdown
# Automated Resume Relevance Checker

An AI-powered system to evaluate resumes against job descriptions, combining **rule-based keyword matching** with a **Large Language Model (LLM)** for semantic analysis.

---

## Features
- **Resume & JD Upload** (.txt format)  
- **Hybrid Scoring**: Hard (keywords) + Soft (LLM semantic relevance)  
- **Evaluation Verdict**: High / Medium / Low suitability  
- **Personalized Feedback**: Highlights missing skills & suggestions  
- **Real-time Dashboard**: Firestore-based live updates for placement teams  

---

## Tech Stack

| Layer     | Technologies |
|-----------|-------------|
| Backend   | Python, Flask, Firebase Admin SDK, Google Gemini API |
| Frontend  | HTML, Tailwind CSS, JavaScript |
| Database  | Firestore (NoSQL) |

---

## Quick Start

1. **Clone Repo**  
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
````

2. **Setup Python Environment**

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure Firebase & Gemini API**

```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service_account.json"
export GEMINI_API_KEY="your-gemini-api-key"
```

4. **Run App**

```bash
flask run
```

Access at [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## Folder Structure

```
.
├── app.py
├── requirements.txt
├── backend/
│   ├── matching.py
│   ├── parsing.py
│   └── scoring.py
└── templates/
    └── index.html
```

---

## How It Works

* **matching.py** → Hard & semantic matching
* **parsing.py** → Extract text from resumes/JDs
* **scoring.py** → Combines matches into final relevance score

A full **AI-powered resume evaluation** system in a modern, easy-to-use package.
