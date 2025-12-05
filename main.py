from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from models import Announcement, engine, create_db_and_tables # <--- Import create_db_and_tables

# --- NEW: Lifespan Manager ---
# This runs BEFORE the app starts up
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🛠️ Creating Database Tables...")
    create_db_and_tables()
    yield
    print("✅ Tables Checked/Created.")

# --- Update App Definition ---
app = FastAPI(lifespan=lifespan)

# 1. Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. The Endpoint
@app.get("/news")
def get_news():
    with Session(engine) as session:
        # Get latest 20 announcements
        statement = select(Announcement).where(Announcement.ai_summary != None).order_by(Announcement.id.desc()).limit(20)
        results = session.exec(statement).all()
        return results

# 3. Health Check
@app.get("/")
def read_root():
    return {"status": "Equisense Backend is Running!"}