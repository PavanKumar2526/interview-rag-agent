from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import shutil, os, json
from groq import Groq
from dotenv import load_dotenv

from tools.resume_parser import parse_resume
from agents.resume_analyzer import analyze_resume
from agents.question_generator import generate_questions
from agents.evaluator import evaluate_full_interview
from tools.report_generator import generate_report

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI(title="AI Interview Coach")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

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
    return {
        "status": "success",
        "candidate": resume_data["name"],
        "role": resume_data["role"],
        "total_questions": len(all_questions),
        "questions": all_questions
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
    return {
        "status": "success",
        "candidate": resume_data["name"],
        "role": resume_data["role"],
        "job_title": questions.get("job_title", ""),
        "match_score": questions.get("match_score", 0),
        "skill_gaps": questions.get("skill_gaps", []),
        "total_questions": len(all_questions),
        "questions": all_questions
    }

@app.post("/submit-answers")
async def submit_answers(payload: dict):
    answers = payload.get("answers", [])
    resume_data = payload.get("resume_data") or session.get("resume_data", {})
    questions_data = payload.get("questions") or session.get("questions", [])
    question_texts = [q["question"] if isinstance(q, dict) else q for q in questions_data]
    role = resume_data.get("role", "General") if resume_data else "General"
    result = evaluate_full_interview(question_texts, answers, role)
    generate_report(resume_data or {}, result)
    session["result"] = result
    return {
        "status": "success",
        "average_score": result["average_score"],
        "verdict": result["verdict"],
        "total_questions": result["total_questions"],
        "role": result["role"],
        "evaluations": result["evaluations"]
    }

@app.get("/get-report")
async def get_report():
    return session.get("result", {})

@app.get("/download-report")
async def download_report():
    path = "reports/interview_report.pdf"
    if not os.path.exists(path):
        return {"error": "Report not found. Please complete an interview first."}
    return FileResponse(path, media_type="application/pdf", filename="interview_report.pdf")

@app.post("/check-relevance")
async def check_relevance(payload: dict):
    """
    Check if candidate's partial answer is relevant to the question.
    Called after 8-10 seconds of candidate speaking.
    Returns: { relevant: bool, confidence: str, message: str }
    """
    question = payload.get("question", "")
    answer_chunk = payload.get("answer_chunk", "")
    
    if not answer_chunk.strip() or len(answer_chunk.strip()) < 5:
        return {"relevant": False, "confidence": "high", "message": "No meaningful answer detected"}

    prompt = f"""You are evaluating if a candidate's answer is relevant to an interview question.

Interview Question: {question}

Candidate's answer so far (first 8-10 seconds): "{answer_chunk}"

Determine if the candidate is attempting to answer the question OR giving completely irrelevant/nonsense content.

Rules:
- If the answer is even slightly related to the topic → relevant = true
- If the answer is random words, jokes, gibberish, completely off-topic → relevant = false
- Be generous — partial or hesitant answers count as relevant
- Only mark false if clearly unrelated to the question topic

Return ONLY this JSON, nothing else:
{{
    "relevant": true or false,
    "confidence": "high" or "medium",
    "reason": "one sentence explanation"
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=100
    )
    
    raw = response.choices[0].message.content.strip()
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()
    
    result = json.loads(raw)
    return result