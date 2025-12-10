import os
import asyncio
import uuid
import time
import logging
import traceback
import json
import tempfile
from flask import Flask, render_template, request, jsonify, session, make_response, g, has_request_context
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
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
import google.cloud.logging
from agent.agent import root_agent

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


# --- Structured Logging Setup ---
class ProjectPrefixFilter(logging.Filter):
    def filter(self, record):
        try:
            prefix = "[thay-tu-online]"
            # Ensure msg is a string before checking/modifying to avoid errors with non-string objs
            if hasattr(record, 'msg') and prefix not in str(record.msg):
                record.msg = f"{prefix} {record.msg}"
            return True
        except Exception:
            # If filtering fails, allow the log through untouched rather than crashing
            return True

# Use JSON logging if in Cloud, otherwise standard text
class StructuredLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.executor = ThreadPoolExecutor(max_workers=1) # Fire-and-forget worker
        
        # Check credentials
        self.cloud_logging = False
        try:
            # HF Deployment: Load JSON from env var
            google_creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
            if google_creds_json:
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_cred_file:
                    temp_cred_file.write(google_creds_json)
                    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_cred_file.name
            
            # Local Fallback
            key_file = "nconghau-demo-devfest-c99ef2b83344.json"
            if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") and os.path.exists(key_file):
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_file

            # Initialize Cloud Logging
            log_client = google.cloud.logging.Client()
            log_client.setup_logging() # This attaches a handler to the root logger
            self.cloud_logging = True
            self.logger.info("✅ Google Cloud Logging connected.")
        except Exception as e:
            self.logger.warning(f"⚠️ Cloud Logging not available: {e}")

        # Attach Prefix Filter to Root Logger Handlers (to catch libraries too)
        for handler in logging.getLogger().handlers:
            handler.addFilter(ProjectPrefixFilter())

    def _log_worker(self, level, payload_json, message_text):
        """Background worker to perform the actual blocking I/O log call."""
        try:
            if self.cloud_logging:
                getattr(self.logger, level)(payload_json)
            else:
                # Local dev: pretty print (errors/warnings visible)
                 print(f"[{level.upper()}] [thay-tu-online] {message_text}")
        except Exception as e:
            print(f"[LOG_FAIL] {e}")

    def log(self, level, message, **kwargs):
        """
        Logs a structured event safely and asynchronously (Fire-and-Forget).
        """
        try:
            # 1. Capture Context (Must be done in Main Thread)
            payload = {"project": "thay-tu-online"}
            
            if has_request_context():
                if hasattr(g, 'trace_id'): payload['trace_id'] = g.trace_id
                if hasattr(g, 'user_id'): payload['user_id'] = g.user_id
            
            payload.update(kwargs)
            
            # 2. Serialize Payload (Fast, in Main Thread to catch serialization errors early if needed, but safe to offload too)
            # We do it here to pass string to worker
            log_entry_json = json.dumps(payload, ensure_ascii=False)
            
            # 3. Offload to Background Thread
            self.executor.submit(self._log_worker, level, log_entry_json, message)
                
        except Exception as e:
            print(f"[LOGGING_ERROR] Failed to submit log: {message}. Error: {e}")

logger = StructuredLogger("thay_tu_app")

# --- Middleware ---
@app.before_request
def before_request():
    g.start_time = time.time()
    g.trace_id = request.headers.get('X-Trace-Id', str(uuid.uuid4()))
    g.user_id = session.get('user_id', 'anonymous')
    
    # Log Start (Skip static)
    if not request.path.startswith('/static'):
        # Try to capture body for /ask
        body = None
        if request.path == '/ask' and request.is_json:
            try:
                body = request.get_json()
            except: 
                pass
                
        logger.log('info', f"▶️ Incoming {request.method} {request.path}", 
                   path=request.path, 
                   method=request.method,
                   request_body=body)

@app.after_request
def after_request(response):
    if request.path.startswith('/static'): return response
        
    duration = round(time.time() - g.start_time, 4)
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    log_data = {
        "path": request.path,
        "method": request.method,
        "status": response.status_code,
        "duration": duration,
        "ip": ip,
        "user_agent": request.headers.get('User-Agent')
    }
    
    level = 'info'
    if response.status_code >= 500: level = 'error'
    elif response.status_code >= 400: level = 'warning'
    
    logger.log(level, f"⏹️ Completed {request.method} {request.path} [{response.status_code}]", **log_data)
    return response


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
    stop=stop_after_attempt(5), # Increased to 5 to handle frequent overloads
    wait=wait_exponential(multiplier=2, min=2, max=30), # Slower backoff (2s, 4s, 8s...)
    reraise=True
)
async def run_agent_async(user_message: str, user_id: str):
    # Initialize components inside the request loop to avoid Event Loop closed errors
    api_key = os.environ.get("GOOGLE_API_KEY")
    llm_client = Gemini(model="gemini-2.5-flash", api_key=api_key)
    
    # Performance Optimization: Re-enabled with safe interval
    summarizer = LlmEventSummarizer(llm=llm_client)
    
    compaction_config = EventsCompactionConfig(
        summarizer=summarizer,
        compaction_interval=50, # High interval to reduce load
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
        # Log significant agent events
        # Note: This might be noisy, can refine later
        # logger.log('info', f"Agent Event", event_type=str(type(event))) 
        
        if hasattr(event, 'content') and event.content:
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    response_text += part.text
    
    logger.log('info', "🤖 Agent completed response", 
               response_length=len(response_text),
               full_response=response_text[:2000] + "..." if len(response_text) > 2000 else response_text) # Log full response (truncated safety)
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
        logger.log('error', f"❌ Exception in /ask: {e}", error=str(e), traceback=traceback.format_exc())
        
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
