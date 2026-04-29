import streamlit as st
import requests
import json
import subprocess
import sys

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Interview Coach", page_icon="🎯", layout="wide")

st.markdown("""
<style>
    .main-title { font-size: 2.5rem; font-weight: 800; color: #1a1a2e; text-align: center; }
    .subtitle { font-size: 1.1rem; color: #666; text-align: center; margin-bottom: 2rem; }
    .score-card { background: #f0f9ff; border-radius: 12px; padding: 20px; text-align: center; }
    .question-box { background: #f8f9fa; border-left: 4px solid #4CAF50; padding: 15px; border-radius: 8px; margin: 10px 0; }
    .stButton>button { width: 100%; background-color: #1a1a2e; color: white; border-radius: 8px; padding: 10px; font-size: 1rem; }
</style>
""", unsafe_allow_html=True)

# Session state init
if "stage" not in st.session_state:
    st.session_state.stage = "upload"
if "questions" not in st.session_state:
    st.session_state.questions = []
if "answers" not in st.session_state:
    st.session_state.answers = []
if "candidate" not in st.session_state:
    st.session_state.candidate = ""
if "result" not in st.session_state:
    st.session_state.result = {}
if "match_score" not in st.session_state:
    st.session_state.match_score = 0
if "skill_gaps" not in st.session_state:
    st.session_state.skill_gaps = []
if "job_title" not in st.session_state:
    st.session_state.job_title = ""

# ── STAGE 1: Upload Resume ──
if st.session_state.stage == "upload":
    st.markdown('<div class="main-title">🎯 AI Interview Coach</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Upload your resume and get a personalized mock interview powered by AI</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        mode = st.radio("🎯 Interview Mode", ["General Interview", "Job-Specific Interview", "🎤 Voice Interview"], horizontal=True)
        uploaded_file = st.file_uploader("📄 Upload Your Resume (PDF)", type=["pdf"])

        jd_url = ""
        if mode == "Job-Specific Interview":
            jd_url = st.text_input("🔗 Paste Job URL (Naukri/LinkedIn)", placeholder="https://www.naukri.com/...")

        if uploaded_file:
            if st.button("🚀 Start My Interview"):
                if mode == "Job-Specific Interview" and not jd_url:
                    st.warning("⚠️ Please paste a job URL!")
                elif mode == "🎤 Voice Interview":
                    # Save uploaded resume to data folder
                    with open("data/resume.pdf", "wb") as f:
                        f.write(uploaded_file.getvalue())
                    st.success("✅ Resume uploaded! Starting voice interview in terminal...")
                    st.info("🎤 Check your terminal — the voice interview is running there! Come back here when done.")
                    
                    if "voice_started" not in st.session_state:
                        st.session_state.voice_started = True
                        subprocess.Popen([sys.executable, "-m", "agents.voice_interviewer"])

                    
                else:
                    with st.spinner("Analyzing your resume and generating questions..."):
                        if mode == "General Interview":
                            response = requests.post(
                                f"{API_URL}/upload-resume",
                                files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                            )
                        else:
                            response = requests.post(
                                f"{API_URL}/upload-resume-jd",
                                files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")},
                                params={"jd_url": jd_url}
                            )
                        data = response.json()
                        if "error" not in data:
                            st.session_state.questions = data["questions"]
                            st.session_state.candidate = data["candidate"]
                            if data.get("match_score"):
                                st.session_state.match_score = data["match_score"]
                                st.session_state.skill_gaps = data["skill_gaps"]
                                st.session_state.job_title = data.get("job_title", "")
                            st.session_state.stage = "interview"
                            st.rerun()
                        else:
                            st.error(f"Error: {data['error']}")

# ── STAGE 2: Interview ──
elif st.session_state.stage == "interview":
    st.markdown(f'<div class="main-title">👋 Hello, {st.session_state.candidate}!</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Answer all questions below, then submit for AI evaluation</div>', unsafe_allow_html=True)

    # Show JD match info if job-specific mode
    if st.session_state.match_score:
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"🏢 Job: {st.session_state.job_title}")
        with col2:
            st.info(f"📊 Your Match Score: {st.session_state.match_score}% | ⚠️ Skill Gaps: {', '.join(st.session_state.skill_gaps)}")

    answers = []
    with st.form("interview_form"):
        for i, q in enumerate(st.session_state.questions):
            badge = {"technical": "🔧", "project": "📊", "hr": "👥", "scenario": "💡"}.get(q["category"], "❓")
            st.write(f"{badge} **Q{i+1} [{q['difficulty'].upper()}]:** {q['question']}")
            answer = st.text_area(f"Answer {i+1}", key=f"ans_{i}", height=100, placeholder="Type your answer here...")
            answers.append(answer)
            st.markdown("---")

        submitted = st.form_submit_button("✅ Submit All Answers & Get Evaluated")

    if submitted:
        if any(a.strip() == "" for a in answers):
            st.warning("⚠️ Please answer all questions before submitting!")
        else:
            with st.spinner("AI is evaluating your answers... This may take a minute."):
                response = requests.post(
                    f"{API_URL}/submit-answers",
                    json={"answers": answers}
                )
                data = response.json()
                st.session_state.result = data
                st.session_state.stage = "result"
                st.rerun()

# ── STAGE 3: Results ──
elif st.session_state.stage == "result":
    result = st.session_state.result
    score = result.get("average_score", 0)
    verdict = result.get("verdict", "")

    st.markdown('<div class="main-title">📊 Your Interview Results</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🎯 Overall Score", f"{score}/10")
    with col2:
        color = "🟢" if score >= 7 else "🟡" if score >= 5 else "🔴"
        st.metric("📝 Verdict", f"{color} {verdict.split('-')[0].strip()}")
    with col3:
        st.metric("📄 Report", "Generated ✅")

    st.success(f"🏆 {verdict}")

    # Show skill gaps if job-specific
    if st.session_state.skill_gaps:
        st.warning(f"📚 Areas to Improve: {', '.join(st.session_state.skill_gaps)}")

    st.markdown("### 📥 Download Your Report")
    with open("reports/interview_report.pdf", "rb") as f:
        st.download_button("⬇️ Download PDF Report", f, file_name="interview_report.pdf", mime="application/pdf")

    if st.button("🔄 Start New Interview"):
        for key in ["stage", "questions", "answers", "candidate", "result", "match_score", "skill_gaps", "job_title"]:
            del st.session_state[key]
        st.rerun()