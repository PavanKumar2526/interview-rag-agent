import requests
from bs4 import BeautifulSoup

def scrape_job_description(url: str) -> dict:
    """Scrape job description from a given URL."""
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove scripts and styles
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        
        text = soup.get_text(separator="\n")
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        clean_text = "\n".join(lines[:200])  # First 200 lines is enough
        
        return {"status": "success", "text": clean_text, "url": url}
    
    except Exception as e:
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    url = input("Paste a job URL: ")
    result = scrape_job_description(url)
    if result["status"] == "success":
        print("✅ JD Scraped!")
        print(result["text"][:500])
    else:
        print(f"❌ {result['error']}")