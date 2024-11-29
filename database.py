from supabase import create_client
from datetime import datetime

url = "https://hjzgryhmegxdfdzsvzhb.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhqemdyeWhtZWd4ZGZkenN2emhiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzI5MDk2MDAsImV4cCI6MjA0ODQ4NTYwMH0.QtBhZLiO1ZXwIgNHyT7-dL_erjp3nnGl9wA-RgYmuCg"
supabase = create_client(url, key)

def init_db():
    # Create messages table if it doesn't exist
    supabase.table('messages').select("*").execute()

def save_message(user_message, bot_response):
    supabase.table('messages').insert({
        "user_message": user_message,
        "bot_response": bot_response,
        "timestamp": datetime.now().isoformat()
    }).execute()

def get_chat_history(limit=5):
    response = supabase.table('messages') \
        .select("user_message,bot_response") \
        .order('timestamp', desc=True) \
        .limit(limit) \
        .execute()
    return [(msg['user_message'], msg['bot_response']) for msg in response.data][::-1]