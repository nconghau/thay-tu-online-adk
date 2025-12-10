import os
import asyncio
import uuid
from flask import Flask, render_template, request, jsonify, session, make_response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from google.adk.memory import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.apps import App
from google.adk.apps.app import EventsCompactionConfig
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
from google.adk.models import Gemini
from google.genai import types
from google.genai.errors import ServerError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'dev-secret-key')

# Security: Rate Limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per day", "30 per hour"],
    storage_uri="memory://"
)

from agent.agent import root_agent

# Configure Session/Memory Services (Keep these global as they are storage)
session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()

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

@retry(
    retry=retry_if_exception_type(ServerError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
async def run_agent_async(user_message: str, user_id: str):
    # Initialize components inside the request loop to avoid Event Loop closed errors
    api_key = os.environ.get("GOOGLE_API_KEY")
    llm_client = Gemini(model="gemini-2.5-flash", api_key=api_key)
    
    summarizer = LlmEventSummarizer(llm=llm_client)
    
    compaction_config = EventsCompactionConfig(
        summarizer=summarizer,
        compaction_interval=20, # Increased from 5 to reduce server load
        overlap_size=2
    )

    adk_app = App(
        name="thay_tu_app",
        root_agent=root_agent,
        events_compaction_config=compaction_config
    )

    runner = Runner(
        app=adk_app,
        session_service=session_service,
        memory_service=memory_service
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



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
@limiter.limit("20 per minute") # Anti-spam: 20 msg/min per IP
async def ask():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Vui lòng nhập câu hỏi'}), 400
        
        # Security: Input Validation
        if len(user_message) > 500:
            return jsonify({'error': 'Câu hỏi dài quá, thầy đọc hông kịp. Con tóm tắt lại dưới 500 chữ nghen!'}), 400
        
        # Security: Basic XSS/Injection sanitize (Mock)
        user_message = user_message.strip()
        
        user_id = session.get('user_id')
        if not user_id:
            user_id = str(uuid.uuid4())
            session['user_id'] = user_id
        
        response = await run_agent_async(user_message, user_id)
        
        if not response:
            response = "Xin lỗi, thầy chưa thể trả lời lúc này. Bạn thử hỏi lại nhé!"
        
        resp = make_response(jsonify({'response': response}))
        # Security Headers
        resp.headers['X-Content-Type-Options'] = 'nosniff'
        resp.headers['X-Frame-Options'] = 'SAMEORIGIN'
        return resp
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        # Return a friendly "Thầy Tư" style error message instead of the raw error
        friendly_error = "Chà, thiên cơ lúc mờ lúc tỏ, hoặc là mạng mẽo nó cà chớn rồi. Con thông cảm hỏi lại dìa cái khác dùm Thầy nghen!"
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
