"""
StatBot Pro - Autonomous CSV Data Analyst Agent
Main FastAPI application with comprehensive error handling and production features.

This module provides:
- RESTful API endpoints for CSV upload and natural language queries
- Web interface for user interaction
- Secure file handling with validation
- Comprehensive logging and monitoring
- Production-ready configuration
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Request, status
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, Field, validator
import pandas as pd
import os
import uuid
import asyncio
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging
import sys
import traceback
import json
from contextlib import asynccontextmanager

from config import get_config
from monitoring import metrics_collector, system_monitor, health_checker, metrics_exporter

from agent import StatBotAgent, AgentError, SecurityError, ExecutionError
from config import get_config
from monitoring import metrics_collector, system_monitor, health_checker, metrics_exporter

# Load configuration
config = get_config()

# Configure comprehensive logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOGS_DIR / 'statbot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration constants from config
MAX_FILE_SIZE = config.MAX_FILE_SIZE
ALLOWED_FILE_EXTENSIONS = set(config.ALLOWED_EXTENSIONS)
MAX_ROWS = config.MAX_ROWS
MAX_COLUMNS = config.MAX_COLUMNS
REQUEST_TIMEOUT = config.EXECUTION_TIMEOUT * 10  # Allow more time for complex analysis
RATE_LIMIT_REQUESTS = config.RATE_LIMIT_REQUESTS
CLEANUP_INTERVAL = config.CLEANUP_INTERVAL

# Application lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown"""
    # Startup
    logger.info("Starting StatBot Pro application")
    config.setup_directories()
    start_cleanup_task()
    
    # Start monitoring
    system_monitor.start_monitoring(interval=60)
    metrics_collector.increment_counter('app_starts')
    
    yield
    
    # Shutdown
    logger.info("Shutting down StatBot Pro application")
    system_monitor.stop_monitoring()
    cleanup_resources()
    metrics_collector.increment_counter('app_stops')

app = FastAPI(
    title="StatBot Pro",
    description="Production-ready Autonomous CSV Data Analyst Agent",
    version="1.0.0",
    lifespan=lifespan
)

# Request monitoring middleware
@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    """Monitor all HTTP requests"""
    start_time = time.time()
    client_ip = get_client_ip(request)
    
    # Record request start
    metrics_collector.increment_counter('http_requests_total', labels={'method': request.method, 'path': request.url.path})
    
    try:
        response = await call_next(request)
        
        # Record successful request
        duration = time.time() - start_time
        metrics_collector.record_request(duration, success=True)
        metrics_collector.record_timer('request_duration', duration, labels={'method': request.method, 'status': str(response.status_code)})
        
        # Add monitoring headers
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        response.headers["X-Request-ID"] = str(uuid.uuid4())
        
        return response
        
    except Exception as e:
        # Record failed request
        duration = time.time() - start_time
        metrics_collector.record_request(duration, success=False)
        metrics_collector.increment_counter('http_requests_errors', labels={'error_type': type(e).__name__})
        
        logger.error(f"Request failed - IP: {client_ip}, Path: {request.url.path}, Error: {str(e)}")
        raise

# Security middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=config.ALLOWED_HOSTS
)

# Directory setup
WORKSPACE_DIR = config.WORKSPACE_DIR
STATIC_DIR = config.STATIC_DIR
TEMPLATES_DIR = config.TEMPLATES_DIR
LOGS_DIR = config.LOGS_DIR

def setup_directories():
    """Create necessary directories with proper permissions"""
    config.setup_directories()
    logger.info("All directories ensured")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Global state management
class ApplicationState:
    """Thread-safe application state management"""
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.request_counts: Dict[str, List[datetime]] = {}
        self.agent = StatBotAgent(max_retries=config.MAX_RETRIES, timeout=config.EXECUTION_TIMEOUT)
        self._lock = asyncio.Lock()
    
    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get or create a session"""
        async with self._lock:
            if session_id not in self.sessions:
                self.sessions[session_id] = {
                    'dataframe': None,
                    'filename': None,
                    'upload_time': None,
                    'question_count': 0,
                    'last_activity': datetime.now()
                }
            return self.sessions[session_id]
    
    async def update_session(self, session_id: str, updates: Dict[str, Any]):
        """Update session data"""
        async with self._lock:
            session = await self.get_session(session_id)
            session.update(updates)
            session['last_activity'] = datetime.now()
    
    async def cleanup_old_sessions(self):
        """Remove old inactive sessions"""
        async with self._lock:
            cutoff_time = datetime.now() - timedelta(hours=24)
            expired_sessions = [
                sid for sid, session in self.sessions.items()
                if session['last_activity'] < cutoff_time
            ]
            for sid in expired_sessions:
                del self.sessions[sid]
                logger.info(f"Cleaned up expired session: {sid}")
    
    async def check_rate_limit(self, client_ip: str) -> bool:
        """Check if client has exceeded rate limit"""
        async with self._lock:
            now = datetime.now()
            hour_ago = now - timedelta(hours=1)
            
            if client_ip not in self.request_counts:
                self.request_counts[client_ip] = []
            
            # Remove old requests
            self.request_counts[client_ip] = [
                req_time for req_time in self.request_counts[client_ip]
                if req_time > hour_ago
            ]
            
            # Check limit
            if len(self.request_counts[client_ip]) >= RATE_LIMIT_REQUESTS:
                return False
            
            # Add current request
            self.request_counts[client_ip].append(now)
            return True

app_state = ApplicationState()

# Cleanup task
cleanup_task = None

def start_cleanup_task():
    """Start background cleanup task"""
    global cleanup_task
    cleanup_task = asyncio.create_task(periodic_cleanup())

async def periodic_cleanup():
    """Periodic cleanup of old files and sessions"""
    while True:
        try:
            await asyncio.sleep(CLEANUP_INTERVAL)
            await app_state.cleanup_old_sessions()
            cleanup_old_files()
            logger.info("Periodic cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup task error: {e}")

def cleanup_old_files():
    """Remove old uploaded files and generated charts"""
    try:
        cutoff_time = time.time() - (24 * 3600)  # 24 hours ago
        
        # Clean workspace files
        for file_path in WORKSPACE_DIR.glob("*"):
            if file_path.stat().st_mtime < cutoff_time:
                file_path.unlink()
                logger.info(f"Removed old workspace file: {file_path}")
        
        # Clean static files (keep recent charts)
        for file_path in STATIC_DIR.glob("chart_*.png"):
            if file_path.stat().st_mtime < cutoff_time:
                file_path.unlink()
                logger.info(f"Removed old chart: {file_path}")
                
    except Exception as e:
        logger.error(f"File cleanup error: {e}")

def cleanup_resources():
    """Cleanup resources on shutdown"""
    global cleanup_task
    if cleanup_task:
        cleanup_task.cancel()
    logger.info("Resources cleaned up")

# Pydantic models with comprehensive validation
class QuestionRequest(BaseModel):
    """Request model for asking questions about data"""
    question: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Natural language question about the data"
    )
    session_id: Optional[str] = Field(
        None,
        description="Optional session ID for maintaining context"
    )
    
    @validator('question')
    def validate_question(cls, v):
        """Validate question content"""
        if not v.strip():
            raise ValueError("Question cannot be empty")
        
        # Check for potentially malicious content
        dangerous_patterns = [
            'import os', 'import sys', 'subprocess', '__import__',
            'exec(', 'eval(', 'open(', 'file(', 'input(',
            'rm -rf', 'del ', 'delete', 'drop table'
        ]
        
        question_lower = v.lower()
        for pattern in dangerous_patterns:
            if pattern in question_lower:
                raise ValueError(f"Question contains potentially unsafe content: {pattern}")
        
        return v.strip()

class UploadResponse(BaseModel):
    """Response model for CSV upload"""
    message: str
    filename: str
    session_id: str
    shape: List[int]
    columns: List[str]
    sample: List[Dict[str, Any]]
    data_types: Dict[str, str]
    memory_usage: str
    null_counts: Dict[str, int]

class QuestionResponse(BaseModel):
    """Response model for question answering"""
    answer: str
    chart_url: Optional[str] = None
    code_used: Optional[str] = None
    analysis_type: str
    execution_time: float
    dataframe_info: Optional[Dict[str, Any]] = None
    session_id: str

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    error_type: str
    timestamp: str
    request_id: str

# Utility functions
def get_client_ip(request: Request) -> str:
    """Extract client IP address"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host

def generate_session_id() -> str:
    """Generate unique session ID"""
    return str(uuid.uuid4())

def validate_csv_file(file: UploadFile) -> None:
    """Comprehensive CSV file validation"""
    # Check file extension
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )
    
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_FILE_EXTENSIONS)}"
        )
    
    # Check file size (this is approximate, actual size checked during read)
    if hasattr(file, 'size') and file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )

def validate_dataframe(df: pd.DataFrame) -> None:
    """Validate dataframe constraints"""
    if df.shape[0] > MAX_ROWS:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Too many rows. Maximum: {MAX_ROWS}"
        )
    
    if df.shape[1] > MAX_COLUMNS:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Too many columns. Maximum: {MAX_COLUMNS}"
        )
    
    if df.empty:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file is empty"
        )

async def rate_limit_check(request: Request):
    """Check rate limiting"""
    client_ip = get_client_ip(request)
    if not await app_state.check_rate_limit(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with detailed logging"""
    request_id = str(uuid.uuid4())
    client_ip = get_client_ip(request)
    
    logger.warning(
        f"HTTP Exception - Request ID: {request_id}, "
        f"IP: {client_ip}, Status: {exc.status_code}, "
        f"Detail: {exc.detail}, Path: {request.url.path}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            error_type="HTTPException",
            timestamp=datetime.now().isoformat(),
            request_id=request_id
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    request_id = str(uuid.uuid4())
    client_ip = get_client_ip(request)
    
    logger.error(
        f"Unexpected Exception - Request ID: {request_id}, "
        f"IP: {client_ip}, Error: {str(exc)}, "
        f"Path: {request.url.path}, Traceback: {traceback.format_exc()}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal server error occurred",
            error_type="InternalError",
            timestamp=datetime.now().isoformat(),
            request_id=request_id
        ).dict()
    )

@app.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...)):
    """Upload a CSV file for analysis"""
    global current_dataframe, current_filename
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        # Save uploaded file
        file_id = str(uuid.uuid4())
        filename = f"{file_id}_{file.filename}"
        filepath = WORKSPACE_DIR / filename
        
        content = await file.read()
        with open(filepath, "wb") as f:
            f.write(content)
        
        # Load dataframe
        current_dataframe = pd.read_csv(filepath)
        current_filename = filename
        
        logger.info(f"Loaded CSV: {filename}, Shape: {current_dataframe.shape}")
        
        return {
            "message": "CSV uploaded successfully",
            "filename": filename,
            "shape": current_dataframe.shape,
            "columns": list(current_dataframe.columns),
            "sample": current_dataframe.head(3).to_dict('records')
        }
        
    except Exception as e:
        logger.error(f"Error uploading CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")

@app.post("/ask_question")
async def ask_question(request: QuestionRequest):
    """Ask a natural language question about the uploaded CSV"""
    global current_dataframe
    
    if current_dataframe is None:
        raise HTTPException(status_code=400, detail="No CSV file uploaded")
    
    try:
        logger.info(f"Processing question: {request.question}")
        
        # Use the agent to process the question
        result = await agent.process_question(current_dataframe, request.question)
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

# API Endpoints
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the web interface"""
    try:
        with open("templates/index.html", "r", encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        logger.error("Web interface template not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Web interface not available"
        )
    except Exception as e:
        logger.error(f"Error serving web interface: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error loading web interface"
        )

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint with monitoring integration"""
    try:
        # Get comprehensive health status
        health_status = health_checker.check_health()
        
        # Add application-specific information
        health_status["application"] = {
            "active_sessions": len(app_state.sessions),
            "agent_ready": app_state.agent is not None,
            "version": "1.0.0"
        }
        
        # Determine HTTP status code based on health
        status_code = status.HTTP_200_OK
        if health_status["status"] == "critical":
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        elif health_status["status"] == "warning":
            status_code = status.HTTP_200_OK  # Still operational
        
        return JSONResponse(content=health_status, status_code=status_code)
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@app.get("/metrics")
async def get_metrics():
    """Get application metrics"""
    try:
        metrics_summary = metrics_collector.get_metrics_summary()
        return metrics_summary
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving metrics"
        )

@app.get("/metrics/prometheus")
async def get_prometheus_metrics():
    """Get metrics in Prometheus format"""
    try:
        prometheus_metrics = metrics_exporter.export_prometheus()
        return Response(content=prometheus_metrics, media_type="text/plain")
    except Exception as e:
        logger.error(f"Error exporting Prometheus metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error exporting metrics"
        )

@app.post("/upload_csv", response_model=UploadResponse)
async def upload_csv(request: Request, file: UploadFile = File(...)):
    """
    Upload and validate CSV file with comprehensive error handling
    
    Args:
        request: FastAPI request object
        file: Uploaded CSV file
        
    Returns:
        UploadResponse with file information and session ID
        
    Raises:
        HTTPException: For various validation and processing errors
    """
    start_time = time.time()
    client_ip = get_client_ip(request)
    
    # Rate limiting
    await rate_limit_check(request)
    
    # Generate session ID
    session_id = generate_session_id()
    
    logger.info(f"CSV upload started - Session: {session_id}, IP: {client_ip}, File: {file.filename}")
    
    try:
        # Validate file
        validate_csv_file(file)
        
        # Read file content with size check
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        safe_filename = f"{file_id}_{file.filename}"
        filepath = WORKSPACE_DIR / safe_filename
        
        # Save file
        with open(filepath, "wb") as f:
            f.write(content)
        
        # Load and validate dataframe
        try:
            df = pd.read_csv(filepath, encoding='utf-8')
        except UnicodeDecodeError:
            # Try different encodings
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    df = pd.read_csv(filepath, encoding=encoding)
                    logger.info(f"Successfully loaded CSV with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unable to decode CSV file. Please check file encoding."
                )
        except pd.errors.EmptyDataError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CSV file is empty or contains no data"
            )
        except pd.errors.ParserError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"CSV parsing error: {str(e)}"
            )
        
        # Validate dataframe
        validate_dataframe(df)
        
        # Calculate memory usage
        memory_usage = df.memory_usage(deep=True).sum()
        memory_usage_str = f"{memory_usage / (1024*1024):.2f} MB"
        
        # Get data types and null counts
        data_types = {col: str(dtype) for col, dtype in df.dtypes.items()}
        null_counts = {col: int(count) for col, count in df.isnull().sum().items()}
        
        # Store in session
        await app_state.update_session(session_id, {
            'dataframe': df,
            'filename': safe_filename,
            'upload_time': datetime.now(),
            'original_filename': file.filename
        })
        
        # Prepare response
        sample_data = df.head(3).fillna("").to_dict('records')  # Fill NaN for JSON serialization
        
        processing_time = time.time() - start_time
        logger.info(
            f"CSV upload completed - Session: {session_id}, "
            f"Shape: {df.shape}, Processing time: {processing_time:.2f}s"
        )
        
        return UploadResponse(
            message="CSV uploaded successfully",
            filename=safe_filename,
            session_id=session_id,
            shape=list(df.shape),
            columns=list(df.columns),
            sample=sample_data,
            data_types=data_types,
            memory_usage=memory_usage_str,
            null_counts=null_counts
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"CSV upload error - Session: {session_id}, Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing CSV file: {str(e)}"
        )
    finally:
        # Cleanup temporary file if error occurred
        if 'filepath' in locals() and filepath.exists() and session_id not in app_state.sessions:
            try:
                filepath.unlink()
            except Exception as cleanup_error:
                logger.error(f"Error cleaning up file {filepath}: {cleanup_error}")

@app.post("/ask_question", response_model=QuestionResponse)
async def ask_question(request: Request, question_request: QuestionRequest):
    """
    Process natural language questions about uploaded data
    
    Args:
        request: FastAPI request object
        question_request: Question request with session info
        
    Returns:
        QuestionResponse with analysis results
        
    Raises:
        HTTPException: For various processing errors
    """
    start_time = time.time()
    client_ip = get_client_ip(request)
    
    # Rate limiting
    await rate_limit_check(request)
    
    # Extract session ID
    session_id = question_request.session_id
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session ID required. Please upload a CSV file first."
        )
    
    logger.info(
        f"Question processing started - Session: {session_id}, "
        f"IP: {client_ip}, Question: {question_request.question[:100]}..."
    )
    
    try:
        # Get session data
        session = await app_state.get_session(session_id)
        df = session.get('dataframe')
        
        if df is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No CSV data found. Please upload a CSV file first."
            )
        
        # Update session activity
        await app_state.update_session(session_id, {
            'question_count': session.get('question_count', 0) + 1
        })
        
        # Process question with timeout
        try:
            result = await asyncio.wait_for(
                app_state.agent.process_question(df, question_request.question),
                timeout=REQUEST_TIMEOUT
            )
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail=f"Question processing timed out after {REQUEST_TIMEOUT} seconds"
            )
        except SecurityError as e:
            logger.warning(f"Security violation - Session: {session_id}, Error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Security violation: {str(e)}"
            )
        except ExecutionError as e:
            logger.error(f"Execution error - Session: {session_id}, Error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Analysis execution failed: {str(e)}"
            )
        except AgentError as e:
            logger.error(f"Agent error - Session: {session_id}, Error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Agent processing error: {str(e)}"
            )
        
        processing_time = time.time() - start_time
        
        logger.info(
            f"Question processing completed - Session: {session_id}, "
            f"Type: {result.get('analysis_type', 'unknown')}, "
            f"Processing time: {processing_time:.2f}s"
        )
        
        return QuestionResponse(
            answer=result.get('answer', 'No answer generated'),
            chart_url=result.get('chart_url'),
            code_used=result.get('code_used'),
            analysis_type=result.get('analysis_type', 'unknown'),
            execution_time=processing_time,
            dataframe_info=result.get('dataframe_info'),
            session_id=session_id
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Question processing error - Session: {session_id}, Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing question: {str(e)}"
        )

@app.get("/sessions/{session_id}")
async def get_session_info(session_id: str):
    """Get information about a specific session"""
    try:
        session = await app_state.get_session(session_id)
        
        # Remove dataframe from response (too large)
        session_info = {k: v for k, v in session.items() if k != 'dataframe'}
        
        # Add dataframe summary if exists
        if session.get('dataframe') is not None:
            df = session['dataframe']
            session_info['dataframe_summary'] = {
                'shape': df.shape,
                'columns': list(df.columns),
                'memory_usage': f"{df.memory_usage(deep=True).sum() / (1024*1024):.2f} MB"
            }
        
        return session_info
        
    except Exception as e:
        logger.error(f"Error getting session info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving session information"
        )

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and cleanup associated files"""
    try:
        session = await app_state.get_session(session_id)
        
        # Cleanup associated files
        if session.get('filename'):
            filepath = WORKSPACE_DIR / session['filename']
            if filepath.exists():
                filepath.unlink()
                logger.info(f"Deleted file: {filepath}")
        
        # Remove from sessions
        if session_id in app_state.sessions:
            del app_state.sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
        
        return {"message": "Session deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting session"
        )

# Production server configuration
if __name__ == "__main__":
    import uvicorn
    
    # Get production configuration
    uvicorn_config = config.get_uvicorn_config()
    
    logger.info(f"Starting StatBot Pro server with config: {uvicorn_config}")
    logger.info(f"Environment: {config.ENVIRONMENT}")
    logger.info(f"Max file size: {config.MAX_FILE_SIZE // (1024*1024)}MB")
    logger.info(f"Rate limit: {config.RATE_LIMIT_REQUESTS} requests/hour")
    
    # Start server
    uvicorn.run("main:app", **uvicorn_config)