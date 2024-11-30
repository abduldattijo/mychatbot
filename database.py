from supabase import create_client
from datetime import datetime

url = "https://hjzgryhmegxdfdzsvzhb.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhqemdyeWhtZWd4ZGZkenN2emhiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzI5MDk2MDAsImV4cCI6MjA0ODQ4NTYwMH0.QtBhZLiO1ZXwIgNHyT7-dL_erjp3nnGl9wA-RgYmuCg"
supabase = create_client(url, key)

def init_db():
    # Create chat_sessions table
    supabase.table('chat_sessions').select("*").execute()
    # Create messages table with session_id
    supabase.table('messages').select("*").execute()

def create_new_chat():
    response = supabase.table('chat_sessions').insert({
        "created_at": datetime.now().isoformat(),
        "title": "New Chat"
    }).execute()
    return response.data[0]['id']

def get_all_chats():
    response = supabase.table('chat_sessions') \
        .select("*") \
        .order('created_at', desc=True) \
        .execute()
    return response.data

def save_message(session_id, user_message, bot_response):
    supabase.table('messages').insert({
        "session_id": session_id,
        "user_message": user_message,
        "bot_response": bot_response,
        "timestamp": datetime.now().isoformat()
    }).execute()

def get_chat_history(session_id):
    response = supabase.table('messages') \
        .select("user_message,bot_response") \
        .eq('session_id', session_id) \
        .order('timestamp') \
        .execute()
    return [(msg['user_message'], msg['bot_response']) for msg in response.data]

def update_chat_title(session_id, title):
    supabase.table('chat_sessions') \
        .update({"title": title}) \
        .eq('id', session_id) \
        .execute()
        
        
def delete_chat(session_id):
    # Delete messages first due to foreign key constraint
    supabase.table('messages').delete().eq('session_id', session_id).execute()
    # Then delete the chat session
    supabase.table('chat_sessions').delete().eq('id', session_id).execute()        