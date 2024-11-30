from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os
import openai
from database import init_db, save_message, get_chat_history, create_new_chat, get_all_chats, update_chat_title, delete_chat

load_dotenv()
app = Flask(__name__, static_url_path='/static', static_folder='static')
openai.api_key = os.getenv('OPENAI_API_KEY')

init_db()

@app.route('/')
def home():
    chats = get_all_chats()
    if not chats:
        session_id = create_new_chat()
    else:
        session_id = chats[0]['id']
    history = get_chat_history(session_id)
    return render_template('index.html', history=history, chats=chats, current_chat=session_id)

@app.route('/new_chat', methods=['POST'])
def new_chat():
    session_id = create_new_chat()
    return jsonify({'session_id': session_id})

@app.route('/get_chat/<int:session_id>')
def get_chat(session_id):
    history = get_chat_history(session_id)
    return jsonify({'history': history})

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    session_id = request.json.get('session_id')
    chat_history = get_chat_history(session_id)
    
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
            messages=messages
        )
        bot_response = response.choices[0].message.content
        save_message(session_id, user_message, bot_response)
        
        if not chat_history:
            title = user_message[:30] + "..." if len(user_message) > 30 else user_message
            update_chat_title(session_id, title)
        
    except Exception as e:
        bot_response = f"Error: {str(e)}"
    
    return jsonify({'response': bot_response})

@app.route('/delete_chat/<int:session_id>', methods=['DELETE'])
def delete_chat_route(session_id):
    try:
        delete_chat(session_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')  