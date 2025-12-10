import os
import asyncio
import uuid
import time
import logging
import traceback
import json
import tempfile
from flask import Flask, render_template, request, jsonify, session, make_response, g
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
        prefix = "[thay-tu-online]"
        if prefix not in str(record.msg):
            record.msg = f"{prefix} {record.msg}"
        # Also ensure JSON payload includes project if structured logging is active
        # (This bit is tricky to enforce on third-party logs generically without a custom Formatter,
        # but modifying msg is the most visible fix for console/text logs)
        return True

# Use JSON logging if in Cloud, otherwise standard text
class StructuredLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
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

    def log(self, level, message, **kwargs):
        """
        Logs a structured event.
        - level: 'info', 'warning', 'error'
        - message: Human readable message
        - kwargs: Extra data fields (e.g., duration, ip, query)
        """
        # Prefix is handled by Filter now, but we add project field for JSON query
        # full_message = f"[thay-tu-online] {message}" # Filter does this
        
        # Inject trace_id/user_id from Flask context if available
        payload = {"project": "thay-tu-online"}
        if g:
            if hasattr(g, 'trace_id'): payload['trace_id'] = g.trace_id
            if hasattr(g, 'user_id'): payload['user_id'] = g.user_id
        
        payload.update(kwargs)
        
        # If using Cloud Logging, it handles JSON serialization automatically via payload
        # But standard logger needs a message string.
        # We'll rely on the Cloud Logging handler to pick up 'extra' or just log a JSON dump string.
        
        if self.cloud_logging:
            # Cloud Logging library supports structured log via `json_fields` if using logger.log_struct
            # But since we hooked into standard python logging, we pass extra dict.
            # However, simpler for this demo: Log a JSON string so it parses nicely in Explorer
            log_entry = json.dumps(payload, ensure_ascii=False)
            getattr(self.logger, level)(log_entry)
        else:
            # Local dev: pretty print
            # Msg is filtered, but here we print manually for StructuredLogger if needed?
            # actually getattr(self.logger) goes to root handler -> filter applies.
            # But wait, json.dumps(payload) is the MSG. Filter will prepend prefix to JSON string?
            # That might break JSON parsing.
            # Refinement: Only filter if msg is NOT json? Or keep prefix outside JSON?
            
            # Better approach: 
            # We want the TEXT log to have [prefix].
            # For JSON logs, we want jsonPayload.project = '...'
            
            # Since we dump JSON as the message content for Cloud Logging, pre-pending text breaks it being pure JSON.
            # However, Cloud Logging treats string payloads as text unless structured.
            # The previous approach (json.dumps) sends a TEXT payload that looks like JSON.
            # If we want pure JSON struct in Explorer, we need `logger.log_struct` from the client, not standard logging.
            # But `google.cloud.logging` handler intercepts standard logging.
            
            # Simple Fix for User's Request:
            # They verified seeing JSON-like strings. They want prefix on ALL lines.
            # If I prepend to JSON string, it's `[prefix] {"foo": "bar"}`. This is fine for text searching.
            print(f"[{level.upper()}] [thay-tu-online] {message} | {kwargs}")

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
