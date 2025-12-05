import os
import time  # <--- Added this
import google.generativeai as genai
from dotenv import load_dotenv
from sqlmodel import Session, select
from models import Announcement, engine

# 1. Setup
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Using 2.5 Flash as confirmed working
model = genai.GenerativeModel('models/gemini-2.5-flash')

def summarize_news():
    print("🤖 AI Agent waking up...")
    
    with Session(engine) as session:
        # Find news that needs processing
        statement = select(Announcement).where(Announcement.ai_summary == None)
        results = session.exec(statement).all()
        
        print(f"Found {len(results)} items to summarize.")
        
        for i, news in enumerate(results):
            try:
                print(f"[{i+1}/{len(results)}] Processing: {news.symbol}...", end=" ", flush=True)
                
                prompt = f"""
                You are a financial analyst. Summarize this corporate announcement for a retail investor.
                Company: {news.symbol}
                Announcement: {news.desc}
                Output requirements:
                - exactly 3 short bullet points.
                - If it mentions numbers, highlight them.
                - Keep it under 50 words total.
                """
                
                response = model.generate_content(prompt)
                
                # Check if the response was blocked
                if response.text:
                    news.ai_summary = response.text
                    session.add(news)
                    session.commit()
                    print("✅ Done.")
                else:
                    print("⚠️ No text returned.")

                # --- THE IMPORTANT FIX ---
                # Wait 5 seconds before the next one to respect the API Limit
                time.sleep(5) 
                
            except Exception as e:
                print(f"\n❌ Error on {news.symbol}: {e}")
                # If we hit a rate limit error specifically, wait longer
                if "429" in str(e) or "Quota" in str(e):
                    print("Cooling down for 30 seconds...")
                    time.sleep(30)

    print("💤 AI Agent finished work.")

if __name__ == "__main__":
    summarize_news()