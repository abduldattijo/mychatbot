from flask import Flask, request, jsonify, render_template, send_file
from dotenv import load_dotenv
import os
import openai
from database import init_db, save_message, get_chat_history
import speech_recognition as sr
import pyttsx3
import tempfile
from datetime import datetime

load_dotenv()
app = Flask(__name__, static_url_path='/static', static_folder='static')
openai.api_key = os.getenv('OPENAI_API_KEY')

init_db()

def text_to_speech(text):
    engine = pyttsx3.init()
    temp_file = os.path.join(tempfile.gettempdir(), f'response_{datetime.now().timestamp()}.mp3')
    engine.save_to_file(text, temp_file)
    engine.runAndWait()
    return temp_file

@app.route('/')
def home():
    history = get_chat_history()
    return render_template('index.html', history=history)

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    chat_history = get_chat_history()
    
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
        save_message(user_message, bot_response)
        
    except Exception as e:
        bot_response = f"Error: {str(e)}"
    
    return jsonify({'response': bot_response})

@app.route('/speech-to-text', methods=['POST'])
def speech_to_text():
    audio_file = request.files.get('audio')
    if not audio_file:
        return jsonify({'error': 'No audio file received'})
    
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
            return jsonify({'text': text})
        except:
            return jsonify({'error': 'Could not recognize speech'})

@app.route('/text-to-speech', methods=['POST'])
def get_speech():
    text = request.json.get('text', '')
    try:
        speech_file = text_to_speech(text)
        return send_file(speech_file, mimetype='audio/mp3')
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')      