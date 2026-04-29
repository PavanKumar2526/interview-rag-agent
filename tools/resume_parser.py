import pdfplumber
import os

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract raw text from a PDF file."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text.strip()

def parse_resume(pdf_path: str) -> dict:
    """Parse resume and return structured text."""
    if not os.path.exists(pdf_path):
        return {"error": "File not found", "status": "error"}
    
    raw_text = extract_text_from_pdf(pdf_path)
    
    if not raw_text:
        return {"error": "Could not extract text from PDF", "status": "error"}
    
    return {
        "raw_text": raw_text,
        "char_count": len(raw_text),
        "status": "success"
    }

if __name__ == "__main__":
    test_path = input("Enter path to your resume PDF: ").strip().strip("'\"& ")
    print(f"\nLooking for file at: {test_path}")
    result = parse_resume(test_path)
    if result["status"] == "success":
        print(f"\n✅ Resume parsed successfully!")
        print(f"📄 Characters extracted: {result['char_count']}")
        print(f"\nFirst 500 characters:\n{result['raw_text'][:500]}")
    else:
        print(f"❌ Error: {result['error']}")