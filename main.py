from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from models import Announcement, engine

app = FastAPI()

# 1. Enable CORS
# This allows your React app (running on localhost:3000) to talk to this Python app (localhost:8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, change this to your specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. The Endpoint
# When someone goes to http://localhost:8000/news, run this function
@app.get("/news")
def get_news():
    with Session(engine) as session:
        # Get latest 5 announcements with summaries, ordered by newest first
        statement = select(Announcement).where(Announcement.ai_summary != None).order_by(Announcement.id.desc()).limit(5)
        results = session.exec(statement).all()
        return results

# 3. Health Check
@app.get("/")
def read_root():
    return {"status": "Equisense Backend is Running!"}