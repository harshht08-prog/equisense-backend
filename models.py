import os
from sqlmodel import SQLModel, Field, create_engine, Session, select
from datetime import datetime

# 1. Define the Data Model
class Announcement(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    symbol: str             # Stock Ticker
    desc: str               # Raw text from NSE
    an_dt: str              # Date string
    attachment_text: str | None = None # PDF Link
    
    # AI Fields
    ai_summary: str | None = None 
    is_red_flag: bool = False
    
    # Automation Fields
    whatsapp_sent: bool = Field(default=False)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

# 2. Database Connection Logic (Updated for Cloud)
# Render provides the DB URL via 'DATABASE_URL' environment variable.
database_url = os.getenv("DATABASE_URL")

# Fix: SQLAlchemy requires 'postgresql://', but some clouds give 'postgres://'
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# Fallback: If no cloud DB found, use local file
if not database_url:
    database_url = "sqlite:///equisense.db"

# Create the engine
engine = create_engine(database_url)

# 3. Helper Functions
def create_db_and_tables():
    # This creates the tables in Postgres or SQLite
    SQLModel.metadata.create_all(engine)

def save_announcement(data_dict):
    """Saves a single announcement to the DB if it doesn't exist."""
    with Session(engine) as session:
        # Check for duplicates based on Symbol + Description
        statement = select(Announcement).where(
            Announcement.symbol == data_dict['symbol'],
            Announcement.desc == data_dict['desc']
        )
        results = session.exec(statement).first()

        if results is None:
            # Create new record
            news = Announcement(**data_dict)
            session.add(news)
            session.commit()
            session.refresh(news)
            print(f"✅ Saved: {news.symbol}")
            return True
        else:
            return False