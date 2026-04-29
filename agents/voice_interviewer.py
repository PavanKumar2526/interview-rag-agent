import os
import json
from dotenv import load_dotenv
from tools.voice_handler import listen_and_transcribe
from tools.tts_handler import speak, configure_voice
from tools.resume_parser import parse_resume
from agents.resume_analyzer import analyze_resume
from agents.question_generator import generate_questions
from agents.evaluator import evaluate_full_interview
from tools.report_generator import generate_report

load_dotenv()

def run_voice_interview():
    """Run a complete voice-based interview session."""
    
    configure_voice(rate=160)
    
    # Welcome
    speak("Welcome to AI Interview Coach. Let's begin your mock interview.")
    speak("I will ask you 10 questions. Please answer clearly after each question.")
    
    # Load resume
    print("\n📄 Loading your resume...")
    parsed = parse_resume("data/resume.pdf")
    if parsed["status"] != "success":
        speak("Sorry, I could not load your resume. Please check the file.")
        return
    
    # Analyze resume
    print("🔍 Analyzing resume...")
    speak("Analyzing your resume. Please wait a moment.")
    resume_data = analyze_resume(parsed["raw_text"])
    
    speak(f"Hello {resume_data['name']}! I can see you are a {resume_data['role']}.")
    speak("Let's start your interview now.")
    
    # Generate questions
    print("❓ Generating questions...")
    questions_data = generate_questions(resume_data)
    
    # Flatten questions
    all_questions = []
    for category in ["technical", "project", "hr", "scenario"]:
        for q in questions_data.get(category, []):
            all_questions.append({
                "category": category,
                "question": q["question"],
                "difficulty": q["difficulty"]
            })
    
    answers = []
    
    # Interview loop
    for i, q in enumerate(all_questions):
        print(f"\n--- Question {i+1}/{len(all_questions)} ---")
        
        # Speak question
        speak(f"Question {i+1}.")
        speak(q["question"])
        speak("You have 30 seconds to answer. Speak now.")
        
        # Listen to answer
        print("🎤 Listening...")
        answer = listen_and_transcribe(duration=30)
        
        if answer:
            print(f"📝 Answer captured: {answer[:100]}...")
            speak("Got it. Moving to the next question.")
        else:
            answer = "No answer provided"
            speak("I did not catch your answer. Moving to next question.")
        
        answers.append(answer)
    
    # Evaluation
    speak("Interview complete! Evaluating your performance. Please wait.")
    print("\n📊 Evaluating all answers...")
    
    question_texts = [q["question"] for q in all_questions]
    result = evaluate_full_interview(question_texts, answers, resume_data["role"])
    
    # Generate report
    report_path = generate_report(resume_data, result)
    
    # Final verdict
    score = result["average_score"]
    verdict = result["verdict"]
    
    speak(f"Evaluation complete!")
    speak(f"Your overall score is {score} out of 10.")
    speak(verdict)
    speak("Your detailed PDF report has been saved. Thank you for using AI Interview Coach!")
    
    print(f"\n✅ Interview Complete!")
    print(f"📊 Score: {score}/10")
    print(f"📝 Verdict: {verdict}")
    print(f"📄 Report: {report_path}")

if __name__ == "__main__":
    run_voice_interview()