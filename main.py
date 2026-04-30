from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil, os, json

from tools.resume_parser import parse_resume
from agents.resume_analyzer import analyze_resume
from agents.question_generator import generate_questions
from agents.evaluator import evaluate_full_interview
from tools.report_generator import generate_report

app = FastAPI(title="AI Interview Coach")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# In-memory session store
session = {}

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    os.makedirs("data", exist_ok=True)
    path = f"data/{file.filename}"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    parsed = parse_resume(path)
    if parsed["status"] != "success":
        return {"error": parsed["error"]}

    resume_data = analyze_resume(parsed["raw_text"])
    questions = generate_questions(resume_data)

    # Flatten all questions into a list
    all_questions = []
    for category in ["technical", "project", "hr", "scenario"]:
        for q in questions.get(category, []):
            all_questions.append({"category": category, "question": q["question"], "difficulty": q["difficulty"]})

    session["resume_data"] = resume_data
    session["questions"] = all_questions
    session["answers"] = []

    return {
        "status": "success",
        "candidate": resume_data["name"],
        "role": resume_data["role"],
        "total_questions": len(all_questions),
        "questions": all_questions
    }

@app.post("/submit-answers")
async def submit_answers(payload: dict):
    answers = payload.get("answers", [])
    resume_data = payload.get("resume_data", session.get("resume_data", {}))
    question_texts = payload.get("questions", [q["question"] for q in session.get("questions", [])])
    role = resume_data.get("role", "General")

    result = evaluate_full_interview(question_texts, answers, role)
    report_path = generate_report(resume_data, result)

    session["result"] = result

    return {
        "status": "success",
        "average_score": result["average_score"],
        "verdict": result["verdict"],
        "role": role,
        "report_path": report_path,
        "evaluations": result.get("evaluations", [])
    }

@app.post("/upload-resume-jd")
async def upload_resume_jd(file: UploadFile = File(...), jd_url: str = ""):
    from agents.jd_question_generator import generate_jd_questions
    from tools.jd_scraper import scrape_job_description

    os.makedirs("data", exist_ok=True)
    path = f"data/{file.filename}"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    parsed = parse_resume(path)
    if parsed["status"] != "success":
        return {"error": parsed["error"]}

    resume_data = analyze_resume(parsed["raw_text"])

    # Scrape JD
    jd = scrape_job_description(jd_url)
    if jd["status"] != "success":
        return {"error": f"Could not scrape JD: {jd['error']}"}

    questions = generate_jd_questions(resume_data, jd["text"])

    all_questions = []
    for category in ["technical", "project", "hr", "scenario"]:
        for q in questions.get(category, []):
            all_questions.append({
                "category": category,
                "question": q["question"],
                "difficulty": q["difficulty"]
            })

    session["resume_data"] = resume_data
    session["questions"] = all_questions
    session["answers"] = []

    return {
        "status": "success",
        "candidate": resume_data["name"],
        "role": resume_data["role"],
        "job_title": questions.get("job_title", ""),
        "company": questions.get("company", ""),
        "match_score": questions.get("match_score", 0),
        "skill_gaps": questions.get("skill_gaps", []),
        "total_questions": len(all_questions),
        "questions": all_questions
    }


@app.get("/get-report")
async def get_report():
    return session.get("result", {})

@app.get("/download-report")
async def download_report():
    path = "reports/interview_report.pdf"
    if not os.path.exists(path):
        return {"error": "Report not found. Please complete an interview first."}
    return FileResponse(
        path,
        media_type="application/pdf",
        filename="interview_report.pdf"
    )