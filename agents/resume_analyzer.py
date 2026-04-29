import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_resume(raw_text: str) -> dict:
    """Extract skills, role, experience from resume text using Groq."""
    
    prompt = f"""You are a resume analyzer. Extract information from this resume and return ONLY a JSON object with no extra text.

Resume:
{raw_text}

Return exactly this JSON structure:
{{
    "name": "candidate full name",
    "email": "email address",
    "phone": "phone number",
    "role": "detected job role (e.g. Data Analyst, Software Engineer)",
    "skills": ["skill1", "skill2", "skill3"],
    "experience_years": "total years of experience as a number",
    "education": "highest education qualification",
    "projects": ["project1", "project2"],
    "certifications": ["cert1", "cert2"],
    "summary": "2 line professional summary"
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    
    raw_response = response.choices[0].message.content.strip()
    
    # Clean response if it has markdown code blocks
    if "```json" in raw_response:
        raw_response = raw_response.split("```json")[1].split("```")[0].strip()
    elif "```" in raw_response:
        raw_response = raw_response.split("```")[1].split("```")[0].strip()
    
    result = json.loads(raw_response)
    return result

if __name__ == "__main__":
    from tools.resume_parser import parse_resume
    
    result = parse_resume("data/resume.pdf")
    if result["status"] == "success":
        print("🔍 Analyzing resume with AI...\n")
        analysis = analyze_resume(result["raw_text"])
        print("✅ Resume Analysis Complete!")
        print(json.dumps(analysis, indent=2))
    else:
        print(f"❌ {result['error']}")