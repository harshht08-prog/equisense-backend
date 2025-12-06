import os
from sqlalchemy import text, create_engine
from dotenv import load_dotenv
from models import create_db_and_tables

# 1. Load the Cloud URL
load_dotenv()
database_url = os.getenv("DATABASE_URL")

# Fix Postgres URL if needed
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

if not database_url:
    print("❌ Error: Could not find DATABASE_URL. Make sure .env is readable.")
    exit()

print(f"🔌 Connecting to: {database_url}")
engine = create_engine(database_url)

def force_reset():
    print("🚀 Starting Force Reset...")
    
    with engine.connect() as connection:
        # 2. Force Drop the table
        print("⚠️  Dropping table 'announcement'...")
        connection.execute(text("DROP TABLE IF EXISTS announcement CASCADE;"))
        connection.commit()
        print("✅ Table dropped.")

    # 3. Recreate
    print("🛠️  Creating new table structure...")
    create_db_and_tables()
    print("✅ New table created with 'pdf_url' column!")

if __name__ == "__main__":
    force_reset()
    