from nsepython import nsefetch
import pandas as pd
from models import create_db_and_tables, save_announcement

def get_latest_news():
    # 1. Ensure DB exists
    create_db_and_tables()
    
    print("Fetching latest corporate announcements from NSE...")
    
    try:
        url = "https://www.nseindia.com/api/corporate-announcements?index=equities"
        response = nsefetch(url)
        
        if response:
            # Loop through every item in the response
            new_count = 0
            for item in response:
                # Prepare data for our DB
                # We map NSE keys to our Database keys
                news_data = {
                    "symbol": item.get('symbol'),
                    "desc": item.get('desc'),
                    "an_dt": item.get('an_dt'),
                    "attachment_text": item.get('attchmntText')
                }
                
                # Save to DB
                was_saved = save_announcement(news_data)
                if was_saved:
                    new_count += 1
            
            print(f"\n--- Process Complete ---")
            print(f"New announcements saved: {new_count}")
            
        else:
            print("Response was empty.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_latest_news()