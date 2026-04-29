import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from datetime import datetime

def generate_report(resume_data: dict, interview_result: dict, output_path: str = "reports/interview_report.pdf"):
    """Generate a professional PDF interview report."""
    
    os.makedirs("reports", exist_ok=True)
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                           rightMargin=40, leftMargin=40,
                           topMargin=40, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    elements = []
    
    # Title style
    title_style = ParagraphStyle('Title', parent=styles['Title'],
                                  fontSize=22, textColor=colors.HexColor('#1a1a2e'),
                                  spaceAfter=6)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'],
                                    fontSize=13, textColor=colors.HexColor('#16213e'),
                                    spaceBefore=12, spaceAfter=6)
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'],
                                   fontSize=10, leading=14)
    
    # Header
    elements.append(Paragraph("Interview Performance Report", title_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y %I:%M %p')}", normal_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a1a2e')))
    elements.append(Spacer(1, 12))
    
    # Candidate Info
    elements.append(Paragraph("Candidate Information", heading_style))
    candidate_data = [
        ["Name", resume_data.get("name", "N/A")],
        ["Email", resume_data.get("email", "N/A")],
        ["Phone", resume_data.get("phone", "N/A")],
        ["Role Applied", interview_result.get("role", "N/A")],
        ["Experience", f"{resume_data.get('experience_years', 'N/A')} years"],
        ["Education", resume_data.get("education", "N/A")],
    ]
    
    candidate_table = Table(candidate_data, colWidths=[2*inch, 4*inch])
    candidate_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#e8f4f8')),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(candidate_table)
    elements.append(Spacer(1, 12))
    
    # Overall Score
    elements.append(Paragraph("Overall Performance", heading_style))
    score = interview_result.get("average_score", 0)
    verdict = interview_result.get("verdict", "N/A")
    
    score_color = colors.HexColor('#27ae60') if score >= 7 else \
                  colors.HexColor('#f39c12') if score >= 5 else \
                  colors.HexColor('#e74c3c')
    
    score_style = ParagraphStyle('Score', parent=styles['Normal'],
                                  fontSize=16, textColor=score_color,
                                  fontName='Helvetica-Bold', spaceAfter=8)
    verdict_style = ParagraphStyle('Verdict', parent=styles['Normal'],
                                  fontSize=12, textColor=score_color,
                                  fontName='Helvetica-Bold', spaceAfter=8)
    elements.append(Paragraph(f"{score}/10", score_style))
    elements.append(Paragraph(f"{verdict}", verdict_style))

    
    # Q&A Evaluations
    elements.append(Paragraph("Detailed Question-wise Evaluation", heading_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    elements.append(Spacer(1, 8))
    
    for i, item in enumerate(interview_result.get("evaluations", []), 1):
        q = item["question"]
        a = item["answer"]
        ev = item["evaluation"]
        
        elements.append(Paragraph(f"Q{i}: {q}", 
            ParagraphStyle('Q', parent=styles['Normal'], 
                          fontSize=10, fontName='Helvetica-Bold',
                          textColor=colors.HexColor('#2c3e50'))))
        elements.append(Paragraph(f"Answer: {a}", normal_style))
        elements.append(Paragraph(f"Score: {ev['score']}/10  |  Technical: {ev['technical_accuracy']}/10  |  Communication: {ev['communication']}/10", 
            ParagraphStyle('Scores', parent=styles['Normal'],
                          fontSize=9, textColor=colors.HexColor('#7f8c8d'))))
        elements.append(Paragraph(f"Feedback: {ev['feedback']}", 
            ParagraphStyle('Feedback', parent=styles['Normal'],
                          fontSize=9, textColor=colors.HexColor('#27ae60'),
                          leftIndent=10)))
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#ecf0f1')))
        elements.append(Spacer(1, 6))
    
    # Skills
    elements.append(Paragraph("Skills Identified", heading_style))
    skills_text = " • ".join(resume_data.get("skills", []))
    elements.append(Paragraph(skills_text, normal_style))
    
    doc.build(elements)
    print(f"✅ Report saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    # Test with dummy data
    test_resume = {
        "name": "Boini Pavan Kumar",
        "email": "impavan2526@gmail.com",
        "phone": "6303141341",
        "role": "Data Analyst",
        "skills": ["Python", "SQL", "Power BI", "Excel"],
        "experience_years": 3,
        "education": "MBA - Human Resource Management"
    }
    test_result = {
        "role": "Data Analyst",
        "average_score": 7.5,
        "verdict": "Good - Recommended for next round",
        "evaluations": [
            {
                "question": "What is LEFT JOIN vs INNER JOIN?",
                "answer": "LEFT JOIN returns all rows from left table...",
                "evaluation": {
                    "score": 8,
                    "technical_accuracy": 9,
                    "communication": 8,
                    "confidence": 7,
                    "feedback": "Good answer with clear explanation.",
                    "ideal_answer_hint": "Add examples for better clarity."
                }
            }
        ]
    }
    generate_report(test_resume, test_result)