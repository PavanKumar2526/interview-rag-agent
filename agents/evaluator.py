import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def evaluate_answer(question: str, answer: str, role: str) -> dict:
    """Evaluate a single answer and return score + feedback."""
    
    prompt = f"""You are an expert interviewer evaluating a candidate for a {role} position.

Question: {question}
Candidate's Answer: {answer}

Evaluate the answer and return ONLY a JSON object with no extra text:
{{
    "score": <number from 0 to 10>,
    "technical_accuracy": <number from 0 to 10>,
    "communication": <number from 0 to 10>,
    "confidence": <number from 0 to 10>,
    "feedback": "specific feedback on the answer",
    "ideal_answer_hint": "brief hint about what a perfect answer would include"
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    
    raw_response = response.choices[0].message.content.strip()
    
    if "```json" in raw_response:
        raw_response = raw_response.split("```json")[1].split("```")[0].strip()
    elif "```" in raw_response:
        raw_response = raw_response.split("```")[1].split("```")[0].strip()
    
    return json.loads(raw_response)

def evaluate_full_interview(questions: list, answers: list, role: str) -> dict:
    """Evaluate all answers and generate final report data."""
    
    evaluations = []
    total_score = 0
    
    for i, (question, answer) in enumerate(zip(questions, answers)):
        print(f"  Evaluating answer {i+1}/{len(questions)}...")
        evaluation = evaluate_answer(question, answer, role)
        evaluations.append({
            "question": question,
            "answer": answer,
            "evaluation": evaluation
        })
        total_score += evaluation["score"]
    
    avg_score = round(total_score / len(evaluations), 1)
    
    # Overall verdict
    if avg_score >= 8:
        verdict = "Excellent - Strong candidate"
    elif avg_score >= 6:
        verdict = "Good - Recommended for next round"
    elif avg_score >= 4:
        verdict = "Average - Needs improvement"
    else:
        verdict = "Below average - Not recommended"
    
    return {
        "role": role,
        "total_questions": len(questions),
        "average_score": avg_score,
        "verdict": verdict,
        "evaluations": evaluations
    }

if __name__ == "__main__":
    # Quick test with sample data
    test_question = "What is the difference between a LEFT JOIN and an INNER JOIN in SQL?"
    test_answer = "LEFT JOIN returns all rows from the left table even if there's no match in the right table, while INNER JOIN only returns rows where there's a match in both tables."
    
    print("🧪 Testing evaluator with sample Q&A...\n")
    result = evaluate_answer(test_question, test_answer, "Data Analyst")
    print("✅ Evaluation Result:")
    print(json.dumps(result, indent=2))