import sqlite3

def init_db():
    conn = sqlite3.connect("results.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT,
            student_name TEXT,
            score REAL,
            verdict TEXT,
            missing_skills TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_result(job_title, student_name, score, verdict, missing_skills):
    conn = sqlite3.connect("results.db")
    c = conn.cursor()
    c.execute("INSERT INTO evaluations (job_title, student_name, score, verdict, missing_skills) VALUES (?,?,?,?,?)",
              (job_title, student_name, score, verdict, ", ".join(missing_skills)))
    conn.commit()
    conn.close()

