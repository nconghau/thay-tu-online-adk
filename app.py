import os
import asyncio
import uuid
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'dev-secret-key')

from agent.agent import root_agent

session_service = InMemorySessionService()

async def get_or_create_session_async(user_id: str):
    try:
        existing = await session_service.get_session(
            app_name="thay_tu_app",
            user_id=user_id,
            session_id=user_id
        )
        if existing:
            return existing
    except Exception:
        pass
    
    return await session_service.create_session(
        app_name="thay_tu_app",
        user_id=user_id,
        session_id=user_id
    )

async def run_agent_async(user_message: str, user_id: str):
    runner = Runner(
        agent=root_agent,
        app_name="thay_tu_app",
        session_service=session_service
    )
    
    adk_session = await get_or_create_session_async(user_id)
    
    content = types.Content(
        role="user",
        parts=[types.Part(text=user_message)]
    )
    
    response_text = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=adk_session.id,
        new_message=content
    ):
        if hasattr(event, 'content') and event.content:
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    response_text += part.text
    
    return response_text

def run_agent(user_message: str, user_id: str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(run_agent_async(user_message, user_id))
    finally:
        loop.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Vui lòng nhập câu hỏi'}), 400
        
        user_id = session.get('user_id')
        if not user_id:
            user_id = str(uuid.uuid4())
            session['user_id'] = user_id
        
        response = run_agent(user_message, user_id)
        
        if not response:
            response = "Xin lỗi, thầy chưa thể trả lời lúc này. Bạn thử hỏi lại nhé!"
        
        return jsonify({'response': response})
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        # Return a friendly "Thầy Tư" style error message instead of the raw error
        friendly_error = "Chà, thiên cơ lúc mờ lúc tỏ, hoặc là mạng mẽo nó cà chớn rồi. Bậu thông cảm hỏi lại dìa cái khác dùm Thầy nghen!"
        return jsonify({'error': friendly_error}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'agent': 'Thầy Tư'})

@app.route('/reset', methods=['POST'])
def reset_session():
    if 'user_id' in session:
        del session['user_id']
    return jsonify({'status': 'reset', 'message': 'Phiên đã được làm mới'})

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    print("🚀 App đang chạy tại: http://localhost:7860")
    app.run(host='0.0.0.0', port=7860, debug=debug_mode)
