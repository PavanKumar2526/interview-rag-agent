import os
import json
from groq import Groq
from dotenv import load_dotenv
from tools.jd_scraper import scrape_job_description

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_jd_questions(resume_data: dict, jd_text: str) -> dict:
    """Generate questions based on BOTH resume + job description."""
    
    prompt = f"""You are an expert interviewer. A candidate is applying for a job.
    
Candidate Profile:
- Name: {resume_data['name']}
- Role: {resume_data['role']}
- Skills: {', '.join(resume_data['skills'])}
- Experience: {resume_data['experience_years']} years
- Projects: {', '.join(resume_data['projects'])}

Job Description:
{jd_text[:2000]}

Generate 10 interview questions that are SPECIFIC to both this candidate's background 
AND this job description. Focus on skill gaps and job requirements.

Return ONLY a JSON object:
{{
    "job_title": "extracted job title from JD",
    "company": "extracted company name from JD",
    "match_score": <0-100 how well candidate matches this job>,
    "skill_gaps": ["skill1", "skill2"],
    "technical": [
        {{"id": 1, "question": "...", "difficulty": "easy/medium/hard"}},
        {{"id": 2, "question": "...", "difficulty": "easy/medium/hard"}},
        {{"id": 3, "question": "...", "difficulty": "easy/medium/hard"}}
    ],
    "project": [
        {{"id": 4, "question": "...", "difficulty": "easy/medium/hard"}},
        {{"id": 5, "question": "...", "difficulty": "easy/medium/hard"}}
    ],
    "hr": [
        {{"id": 6, "question": "...", "difficulty": "easy/medium/hard"}},
        {{"id": 7, "question": "...", "difficulty": "easy/medium/hard"}}
    ],
    "scenario": [
        {{"id": 8, "question": "...", "difficulty": "easy/medium/hard"}},
        {{"id": 9, "question": "...", "difficulty": "easy/medium/hard"}},
        {{"id": 10, "question": "...", "difficulty": "easy/medium/hard"}}
    ]
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    raw_response = response.choices[0].message.content.strip()
    
    if "```json" in raw_response:
        raw_response = raw_response.split("```json")[1].split("```")[0].strip()
    elif "```" in raw_response:
        raw_response = raw_response.split("```")[1].split("```")[0].strip()
    
    return json.loads(raw_response)

if __name__ == "__main__":
    from tools.resume_parser import parse_resume
    from agents.resume_analyzer import analyze_resume

    print("📄 Parsing resume...")
    parsed = parse_resume("data/resume.pdf")
    resume_data = analyze_resume(parsed["raw_text"])

    url = input("🔗 Paste Job URL: ")
    print("🌐 Scraping job description...")
    jd = scrape_job_description(url)

    if jd["status"] == "success":
        print("🤖 Generating JD-matched questions...\n")
        result = generate_jd_questions(resume_data, jd["text"])
        print("✅ Done!")
        print(f"🏢 Job: {result['job_title']} at {result['company']}")
        print(f"📊 Match Score: {result['match_score']}%")
        print(f"⚠️  Skill Gaps: {', '.join(result['skill_gaps'])}")
        print(f"\n📝 Sample Question: {result['technical'][0]['question']}")
    else:
        print(f"❌ {jd['error']}")