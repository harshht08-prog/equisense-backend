import os
import time
import requests
import google.generativeai as genai
from dotenv import load_dotenv
from sqlmodel import Session, select
from models import Announcement, engine

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use Gemini 2.5 Flash
model = genai.GenerativeModel('models/gemini-2.5-flash')

def smart_download(pdf_url, filename):
    """
    Tries to download the PDF from multiple NSE servers if the first one fails.
    """
    
    # 1. Extract the filename from the URL (e.g., "5382_RELIANCE.pdf")
    clean_filename = pdf_url.split("/")[-1]
    
    # 2. List of possible server locations for the file
    candidate_urls = [
        pdf_url,                                                  # The one we saved (nsearchives)
        f"https://archives.nseindia.com/corporate/{clean_filename}", # Old archive server
        f"https://www.nseindia.com/content/corporate/{clean_filename}" # Main server backup
    ]

    # 3. Headers that mimic a real Chrome browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://www.nseindia.com/companies-listing/corporate-filings-announcements",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    }

    # 4. Try each URL until one works
    for target_url in candidate_urls:
        try:
            # print(f"   Trying: {target_url} ...")
            response = requests.get(target_url, headers=headers, timeout=20)
            
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                return True # Success!
            elif response.status_code == 404:
                continue # Try next URL
            else:
                print(f"   ⚠️ Blocked/Error ({response.status_code}) on {target_url}")
                
        except Exception as e:
            print(f"   ⚠️ Connection Error: {str(e)[:50]}")
            
    return False # Failed all attempts

def analyze_pdfs():
    print("🕵️ Forensic Analyst starting...")
    
    if not os.path.exists("temp_pdfs"):
        os.makedirs("temp_pdfs")

    # 1. Get List of IDs
    with Session(engine) as session:
        statement = select(Announcement.id).where(
            Announcement.pdf_url != None,
            Announcement.forensic_analysis == None
        )
        pending_ids = session.exec(statement).all()

    print(f"Found {len(pending_ids)} PDFs to analyze.")
    
    # 2. Process
    for ann_id in pending_ids:
        with Session(engine) as session:
            news = session.get(Announcement, ann_id)
            if not news: continue

            print(f"📄 Analyzing {news.symbol}...", end=" ", flush=True)
            local_filename = f"temp_pdfs/{news.symbol}_{news.id}.pdf"
            
            # --- USE SMART DOWNLOAD ---
            if smart_download(news.pdf_url, local_filename):
                try:
                    # Upload
                    sample_file = genai.upload_file(path=local_filename, display_name=news.symbol)
                    
                    # Prompt
                    prompt = """
                    You are a Forensic Accountant. Analyze this document rigorously.
                    
                    1. SENTIMENT: (Positive / Negative / Neutral)
                    2. RED FLAGS: List any strict warnings (Resignations, Defaults, Litigation, Tax Raids, Delays). If none, write "None".
                    3. KEY METRICS: Extract Revenue, PAT, and Margins if this is a financial result.
                    
                    Output Format:
                    Sentiment: [Value]
                    Red Flags: [Value]
                    Summary: [One sentence takeaway]
                    """
                    
                    response = model.generate_content([sample_file, prompt])
                    news.forensic_analysis = response.text
                    
                    # Flag logic
                    if "Resignation" in response.text or "Default" in response.text:
                        news.is_red_flag = True
                        
                    session.add(news)
                    session.commit()
                    print("✅ Analyzed.")
                    
                    # Cleanup
                    try: os.remove(local_filename)
                    except: pass
                    
                except Exception as e:
                    print(f"❌ AI Error: {e}")
            else:
                print("Skipped (File Not Found on NSE servers).")
            
            time.sleep(3) # Be nice to the server

if __name__ == "__main__":
    analyze_pdfs()