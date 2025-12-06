from nsepython import nsefetch
import pandas as pd
from models import create_db_and_tables, save_announcement
from dotenv import load_dotenv
import os

load_dotenv()

def get_latest_news():
    create_db_and_tables()
    print("🕵️ Fetching news + searching for PDF links...")
    
    try:
        url = "https://www.nseindia.com/api/corporate-announcements?index=equities"
        response = nsefetch(url)
        
        if response:
            new_count = 0
            for item in response:
                # --- BUG FIX START ---
                raw_file = item.get('attchmntFile')
                pdf_link = None
                
                if raw_file:
                    # Check if it already looks like a URL
                    if raw_file.startswith("http"):
                        pdf_link = raw_file
                    else:
                        # It's just a filename, so add the prefix
                        pdf_link = f"https://nsearchives.nseindia.com/corporate/{raw_file}"
                # --- BUG FIX END ---

                news_data = {
                    "symbol": item.get('symbol'),
                    "desc": item.get('desc'),
                    "an_dt": item.get('an_dt'),
                    "attachment_text": item.get('attchmntText'),
                    "pdf_url": pdf_link
                }
                
                if save_announcement(news_data):
                    new_count += 1
            
            print(f"✅ Process Complete. New items: {new_count}")
        else:
            print("Response was empty.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    get_latest_news()