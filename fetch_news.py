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
                # 1. Construct the PDF URL
                # NSE stores files at this specific base URL
                pdf_link = None
                if item.get('attchmntFile'):
                    pdf_link = f"https://nsearchives.nseindia.com/corporate/{item.get('attchmntFile')}"

                news_data = {
                    "symbol": item.get('symbol'),
                    "desc": item.get('desc'),
                    "an_dt": item.get('an_dt'),
                    "attachment_text": item.get('attchmntText'),
                    "pdf_url": pdf_link  # <--- Saving the link
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