import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_questions(resume_data: dict) -> dict:
    """Generate interview questions based on resume analysis."""
    
    prompt = f"""You are an expert interviewer. Based on this candidate profile, generate interview questions.

Candidate Profile:
- Name: {resume_data['name']}
- Role: {resume_data['role']}
- Skills: {', '.join(resume_data['skills'])}
- Experience: {resume_data['experience_years']} years
- Projects: {', '.join(resume_data['projects'])}
- Certifications: {', '.join(resume_data.get('certifications', []))}

Generate exactly 10 questions total. Return ONLY a JSON object with no extra text:
{{
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
    
    questions = json.loads(raw_response)
    return questions

if __name__ == "__main__":
    from tools.resume_parser import parse_resume
    from agents.resume_analyzer import analyze_resume
    
    print("📄 Parsing resume...")
    parsed = parse_resume("data/resume.pdf")
    
    print("🔍 Analyzing resume...")
    resume_data = analyze_resume(parsed["raw_text"])
    
    print("❓ Generating questions...\n")
    questions = generate_questions(resume_data)
    
    print("✅ Questions Generated!")
    print(json.dumps(questions, indent=2))