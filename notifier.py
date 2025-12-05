import os
import time
from twilio.rest import Client
from dotenv import load_dotenv
from sqlmodel import Session, select
from models import Announcement, engine

# Load keys
load_dotenv()
client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

# Configuration
FROM_NUMBER = 'whatsapp:+14155238886' 
TO_NUMBER = 'whatsapp:+917570081624' # <--- PUT YOUR NUMBER HERE

def send_pending_alerts():
    print("🚀 Notifier checking for new alerts...")
    
    with Session(engine) as session:
        # 1. Find news that has a Summary BUT hasn't been sent yet
        statement = select(Announcement).where(
            Announcement.ai_summary != None,
            Announcement.whatsapp_sent == False
        )
        results = session.exec(statement).all()
        
        print(f"Found {len(results)} pending alerts.")
        
        for news in results:
            try:
                # 2. Format the message nicely
                # Using emojis and bolding (*) for WhatsApp formatting
                msg_body = (
                    f"📢 *{news.symbol} Update*\n"
                    f"🗓 {news.an_dt}\n\n"
                    f"{news.ai_summary}\n\n"
                    f"🔗 _Check Dashboard for details_"
                )
                
                # 3. Send via Twilio
                print(f"Sending alert for {news.symbol}...", end=" ")
                client.messages.create(
                    from_=FROM_NUMBER,
                    body=msg_body,
                    to=TO_NUMBER
                )
                
                # 4. Mark as Sent in DB so we don't send it again
                news.whatsapp_sent = True
                session.add(news)
                session.commit()
                print("✅ Sent.")
                
                # Sleep to be nice to the API
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error sending {news.symbol}: {e}")

if __name__ == "__main__":
    send_pending_alerts()