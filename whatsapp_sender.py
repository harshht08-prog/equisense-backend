import os
from twilio.rest import Client
from dotenv import load_dotenv

# Load credentials
load_dotenv()

# Get these from your Twilio Dashboard
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)

# The sandbox number (from Twilio)
from_whatsapp_number = 'whatsapp:+14155238886' 

# YOUR personal number (must verify in sandbox first)
to_whatsapp_number = 'whatsapp:+917570081624'  # <--- REPLACE THIS

def send_alert(stock_symbol, summary):
    try:
        message_body = f"📢 *New Update: {stock_symbol}*\n\n{summary}\n\n_Check Dashboard for more._"
        
        message = client.messages.create(
            from_=from_whatsapp_number,
            body=message_body,
            to=to_whatsapp_number
        )
        print(f"✅ Message sent! ID: {message.sid}")
    except Exception as e:
        print(f"❌ Failed to send WhatsApp: {e}")

if __name__ == "__main__":
    # Test it
    send_alert("TEST-STOCK", "This is a test message from your Python code!")