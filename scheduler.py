import time
import schedule  # We need to install this library
from datetime import datetime

# Import functions from your existing scripts
# (Make sure these files are in the same folder)
from fetch_news import get_latest_news
from ai_agent import summarize_news
from notifier import send_pending_alerts

def run_pipeline():
    print(f"\n--- 🔄 Pipeline Started at {datetime.now().strftime('%H:%M:%S')} ---")
    
    # Step 1: Get Data
    try:
        get_latest_news()
    except Exception as e:
        print(f"❌ Error in Fetch Step: {e}")

    # Step 2: Analyze Data
    try:
        summarize_news()
    except Exception as e:
        print(f"❌ Error in AI Step: {e}")

    # Step 3: Notify User
    try:
        send_pending_alerts()
    except Exception as e:
        print(f"❌ Error in Notify Step: {e}")
        
    print("--- ✅ Pipeline Finished. Waiting for next cycle... ---")

# Schedule the job every 10 minutes
# (You can change this to 1 minute for testing)
schedule.every(10).minutes.do(run_pipeline)

if __name__ == "__main__":
    print("🚀 Equisense Bot Launched! Press Ctrl+C to stop.")
    
    # Run once immediately when starting
    run_pipeline()
    
    # Keep running forever
    while True:
        schedule.run_pending()
        time.sleep(1)