import streamlit as st

# Set page configuration - THIS MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="SSS/DSS AI Assistant",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

from datetime import datetime
import openai
from supabase import create_client
import os
from dotenv import load_dotenv
import base64
from pathlib import Path

# Load environment variables
load_dotenv()

# Initialize OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize Supabase
url = "https://hjzgryhmegxdfdzsvzhb.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhqemdyeWhtZWd4ZGZkenN2emhiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzI5MDk2MDAsImV4cCI6MjA0ODQ4NTYwMH0.QtBhZLiO1ZXwIgNHyT7-dL_erjp3nnGl9wA-RgYmuCg"
supabase = create_client(url, key)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #1a1a1a;
    }
    .stTextInput > div > div > input {
        background-color: #2d3748;
        color: white;
        border: 2px solid #008000;
    }
    .stButton button {
        background-color: #008000;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
    .stButton button:hover {
        background-color: #006400;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 3px solid #008000;
    }
    .user-message {
        background-color: rgba(0, 100, 0, 0.3);
    }
    .bot-message {
        background-color: rgba(0, 70, 0, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None
if 'chats' not in st.session_state:
    st.session_state.chats = []

def init_db():
    """Initialize database tables"""
    try:
        supabase.table('chat_sessions').select("*").execute()
        supabase.table('messages').select("*").execute()
    except Exception as e:
        st.error(f"Database initialization error: {str(e)}")

def create_new_chat():
    """Create a new chat session"""
    try:
        response = supabase.table('chat_sessions').insert({
            "created_at": datetime.now().isoformat(),
            "title": "New Chat"
        }).execute()
        return response.data[0]['id']
    except Exception as e:
        st.error(f"Error creating new chat: {str(e)}")
        return None

def get_all_chats():
    """Get all chat sessions"""
    try:
        response = supabase.table('chat_sessions') \
            .select("*") \
            .order('created_at', desc=True) \
            .execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching chats: {str(e)}")
        return []

def save_message(session_id, user_message, bot_response):
    """Save a message to the database"""
    try:
        supabase.table('messages').insert({
            "session_id": session_id,
            "user_message": user_message,
            "bot_response": bot_response,
            "timestamp": datetime.now().isoformat()
        }).execute()
    except Exception as e:
        st.error(f"Error saving message: {str(e)}")

def get_chat_history(session_id):
    """Get chat history for a session"""
    try:
        response = supabase.table('messages') \
            .select("user_message,bot_response") \
            .eq('session_id', session_id) \
            .order('timestamp') \
            .execute()
        return [(msg['user_message'], msg['bot_response']) for msg in response.data]
    except Exception as e:
        st.error(f"Error fetching chat history: {str(e)}")
        return []

def update_chat_title(session_id, title):
    """Update the title of a chat session"""
    try:
        supabase.table('chat_sessions') \
            .update({"title": title}) \
            .eq('id', session_id) \
            .execute()
    except Exception as e:
        st.error(f"Error updating chat title: {str(e)}")

def delete_chat(session_id):
    """Delete a chat session and its messages"""
    try:
        # Delete messages first due to foreign key constraint
        supabase.table('messages').delete().eq('session_id', session_id).execute()
        # Then delete the chat session
        supabase.table('chat_sessions').delete().eq('id', session_id).execute()
    except Exception as e:
        st.error(f"Error deleting chat: {str(e)}")

def get_bot_response(user_message, chat_history):
    """Get response from OpenAI"""
    try:
        messages = [{"role": "system", "content": """You are the SSS/DSS AI Assistant. Your responses should:
        - Focus on Nigerian security matters and intelligence
        - Maintain confidentiality and professionalism
        - Provide security-conscious guidance
        - Avoid sharing sensitive information
        - Use official, professional language
        - Reference Nigerian law and security protocols when relevant
        When unsure, err on the side of security and confidentiality."""}]
        
        for msg in chat_history:
            messages.extend([
                {"role": "user", "content": msg[0]},
                {"role": "assistant", "content": msg[1]}
            ])
        messages.append({"role": "user", "content": user_message})
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error getting bot response: {str(e)}")
        return "I apologize, but I encountered an error processing your request. Please try again."

def load_and_display_image():
    """Load and display the SSS logo"""
    try:
        image_path = Path("static/sss_logo.png.png")
        if image_path.exists():
            with open(image_path, "rb") as img_file:
                img_data = base64.b64encode(img_file.read()).decode()
                st.markdown(
                    f'<div style="display: flex; justify-content: center; margin: 2rem 0;"><img src="data:image/png;base64,{img_data}" style="max-width: 250px;"></div>',
                    unsafe_allow_html=True
                )
    except Exception as e:
        st.warning("Logo image could not be loaded")

# Initialize database
init_db()

# Sidebar
with st.sidebar:
    st.title("SSS/DSS AI Assistant")
    st.markdown("---")
    
    if st.button("📝 New Chat", key="new_chat"):
        new_chat_id = create_new_chat()
        if new_chat_id:
            st.session_state.current_chat_id = new_chat_id
            st.session_state.chat_history = []
            st.rerun()
    
    st.markdown("---")
    st.subheader("Your Chats")
    
    # Get and display all chats
    st.session_state.chats = get_all_chats()
    for chat in st.session_state.chats:
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(
                f"💬 {chat['title'][:30] + '...' if len(chat['title']) > 30 else chat['title']}", 
                key=f"chat_{chat['id']}"
            ):
                st.session_state.current_chat_id = chat['id']
                st.session_state.chat_history = get_chat_history(chat['id'])
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"delete_{chat['id']}"):
                delete_chat(chat['id'])
                if chat['id'] == st.session_state.current_chat_id:
                    st.session_state.current_chat_id = None
                    st.session_state.chat_history = []
                st.rerun()

# Main chat interface
st.title("SSS/DSS AI Assistant")
load_and_display_image()

# Initialize current chat if needed
if st.session_state.current_chat_id is None and st.session_state.chats:
    st.session_state.current_chat_id = st.session_state.chats[0]['id']
    st.session_state.chat_history = get_chat_history(st.session_state.current_chat_id)
elif st.session_state.current_chat_id is None:
    st.session_state.current_chat_id = create_new_chat()
    st.session_state.chat_history = []

# Display chat container with custom styling
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display chat history
for user_msg, bot_msg in st.session_state.chat_history:
    with st.chat_message("user"):
        st.markdown(f'<div class="chat-message user-message">{user_msg}</div>', unsafe_allow_html=True)
    with st.chat_message("assistant"):
        st.markdown(f'<div class="chat-message bot-message">{bot_msg}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Chat input
if user_input := st.chat_input("Type your message here..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(f'<div class="chat-message user-message">{user_input}</div>', unsafe_allow_html=True)
    
    # Get and display bot response
    with st.chat_message("assistant"):
        bot_response = get_bot_response(user_input, st.session_state.chat_history)
        st.markdown(f'<div class="chat-message bot-message">{bot_response}</div>', unsafe_allow_html=True)
    
    # Save message to database and update chat history
    save_message(st.session_state.current_chat_id, user_input, bot_response)
    st.session_state.chat_history = get_chat_history(st.session_state.current_chat_id)
    
    # Update chat title if this is the first message
    if len(st.session_state.chat_history) == 1:
        title = user_input[:30] + "..." if len(user_input) > 30 else user_input
        update_chat_title(st.session_state.current_chat_id, title)
        st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        Powered by SSS/DSS AI Assistant
    </div>
    """,
    unsafe_allow_html=True)