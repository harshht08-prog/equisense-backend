import threading
import time
import schedule
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from models import Announcement, engine, create_db_and_tables
# Add this to your imports at the top
from analyst import analyze_pdfs
# Import your actual task functions
from fetch_news import get_latest_news
from ai_agent import summarize_news
from notifier import send_pending_alerts

# --- BACKGROUND SCHEDULER ---
def run_scheduler():
    print("⏳ Scheduler Thread Started")
    
    # Define the job
def job():
    print("⏰ Running Scheduled Tasks...")
    try:
        # 1. Get News
        get_latest_news()

        # 2. Basic Summaries (Fast)
        summarize_news()

        # 3. Deep Analysis (The New Phase 3 Step)
        analyze_pdfs()  # <--- ADD THIS LINE

        # 4. Send Alerts
        send_pending_alerts()

        print("✅ Tasks Complete")
    except Exception as e:
        print(f"❌ Scheduler Error: {e}")

    # Schedule it every 10 minutes
    schedule.every(10).minutes.do(job)
    
    # Run loop
    while True:
        schedule.run_pending()
        time.sleep(1)

# --- LIFESPAN (Startup Event) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🛠️ Creating Database Tables...")
    create_db_and_tables()
    
    print("🚀 Starting Background Scheduler...")
    # Start the scheduler in a separate thread so it doesn't block the API
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    yield
    print("🛑 Shutting down...")

# --- APP DEFINITION ---
app = FastAPI(lifespan=lifespan)

# ... (Rest of your API code stays the same) ...
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/news")
def get_news():
    with Session(engine) as session:
        statement = select(Announcement).where(Announcement.ai_summary != None).order_by(Announcement.id.desc()).limit(20)
        results = session.exec(statement).all()
        return results

@app.get("/")
def read_root():
    return {"status": "Equisense Backend & Worker Running!"}