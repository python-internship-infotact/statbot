# StatBot Pro - Comprehensive Project Documentation

## Project Overview

**StatBot Pro** is an autonomous data analysis agent with a modern web interface that allows users to upload CSV files and ask natural language questions to get intelligent data insights, visualizations, and analysis.

### Key Features
- **Natural Language Processing**: Ask questions in plain English about your data
- **Intelligent Code Generation**: Automatically generates and executes Python analysis code
- **Secure Execution Environment**: Sandboxed code execution with comprehensive security measures
- **Interactive Visualizations**: Automatic chart generation with matplotlib
- **Real-time Analysis**: Streaming responses with step-by-step reasoning
- **Production Ready**: Full monitoring, logging, and deployment capabilities
- **Modern UI**: React-based frontend with TypeScript and Tailwind CSS

### Technology Stack

#### Backend
- **Python 3.11+** - Core runtime
- **FastAPI** - Modern web framework for APIs
- **Pandas** - Data manipulation and analysis
- **Matplotlib** - Data visualization
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **AsyncIO** - Asynchronous programming

#### Frontend
- **React 18** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Icon library
- **Radix UI** - Headless UI components

#### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Reverse proxy (production)
- **GitHub Actions** - CI/CD pipeline

## Architecture Overview

### System Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Analysis      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   Engine        │
│                 │    │                 │    │   (Python)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Static Files  │    │   Session       │    │   Secure        │
│   (Charts/Data) │    │   Management    │    │   Executor      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Core Components

#### 1. StatBot Agent (`agent.py`)
- **Purpose**: Core AI agent for data analysis
- **Key Features**:
  - Natural language question processing
  - Intelligent code generation with pattern recognition
  - Self-correcting behavior with retry logic
  - Secure code execution with sandboxing
  - Support for specific queries (filtering, aggregation)
  - Comprehensive error handling

#### 2. FastAPI Backend (`main.py`)
- **Purpose**: REST API server
- **Endpoints**:
  - `POST /upload_csv` - File upload and processing
  - `POST /ask_question` - Natural language query processing
  - `GET /health` - Health check
  - `GET /static/{path}` - Static file serving
- **Features**:
  - Session management
  - Rate limiting
  - CORS handling
  - Comprehensive error handling
  - Request/response logging

#### 3. React Frontend
- **Purpose**: User interface
- **Key Components**:
  - `AnalysisWorkspace` - Main analysis interface
  - `ChatPanel` - Question/answer interface
  - `DatasetInspector` - Data overview
  - `ResultsPanel` - Analysis results display
  - `UploadZone` - File upload interface

#### 4. Security System (`SecureExecutor`)
- **Purpose**: Safe code execution
- **Features**:
  - AST-based code validation
  - Restricted module imports
  - Blocked dangerous functions
  - Resource limits (memory, CPU)
  - Execution timeout
  - Comprehensive logging

## File Structure

```
statbot-pro/
├── backend/
│   ├── agent.py              # Core AI agent
│   ├── main.py               # FastAPI server
│   ├── config.py             # Configuration
│   ├── monitoring.py         # System monitoring
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── statbot/      # StatBot-specific components
│   │   │   └── ui/           # Reusable UI components
│   │   ├── lib/              # Utilities and API client
│   │   ├── types/            # TypeScript type definitions
│   │   └── pages/            # Page components
│   ├── package.json          # Node.js dependencies
│   └── vite.config.ts        # Vite configuration
├── docker/
│   ├── Dockerfile            # Container definition
│   └── docker-compose.yml    # Multi-container setup
├── tests/
│   ├── test_examples.py      # Example tests
│   ├── test_integration.py   # Integration tests
│   └── advanced_test.py      # Advanced testing
├── static/                   # Generated charts and files
├── workspace/                # User data storage
├── logs/                     # Application logs
└── docs/
    ├── README.md             # Project overview
    ├── PRODUCTION_GUIDE.md   # Deployment guide
    └── API_DOCUMENTATION.md  # API reference
```

## Key Features Deep Dive

### 1. Natural Language Processing
- **Question Analysis**: Parses user questions to determine intent
- **Pattern Recognition**: Identifies specific query types (filtering, aggregation, visualization)
- **Context Understanding**: Maintains conversation context across questions

### 2. Intelligent Code Generation
- **Template System**: Pre-built code templates for common analysis patterns
- **Dynamic Generation**: Creates custom code based on question analysis
- **Specific Query Handling**: Special logic for filtering and aggregation queries
- **Error Recovery**: Self-correcting code generation with retry logic

### 3. Security Features
- **Sandboxed Execution**: Isolated Python environment
- **Code Validation**: AST-based security checks
- **Resource Limits**: Memory and CPU constraints
- **Blocked Operations**: Prevents dangerous system calls
- **Audit Logging**: Comprehensive security event logging

### 4. Data Visualization
- **Automatic Chart Generation**: Creates visualizations based on analysis type
- **Multiple Chart Types**: Histograms, scatter plots, correlation heatmaps, bar charts
- **Interactive Results**: Clickable and explorable visualizations
- **Export Capabilities**: Save charts as PNG files

### 5. Session Management
- **Persistent Sessions**: Maintains data across multiple questions
- **UUID-based Identification**: Secure session tracking
- **Data Isolation**: Each session has isolated data storage
- **Cleanup Mechanisms**: Automatic session cleanup

## API Documentation

### Upload CSV Endpoint
```http
POST /upload_csv
Content-Type: multipart/form-data

Parameters:
- file: CSV file (required)

Response:
{
  "message": "File uploaded successfully",
  "filename": "data.csv",
  "session_id": "uuid-string",
  "shape": [rows, columns],
  "columns": ["col1", "col2", ...],
  "sample": [{"col1": "val1", ...}, ...],
  "data_types": {"col1": "object", ...},
  "memory_usage": "1.2 MB",
  "null_counts": {"col1": 0, ...}
}
```

### Ask Question Endpoint
```http
POST /ask_question
Content-Type: application/json

Body:
{
  "question": "What is the correlation between sales and marketing spend?",
  "session_id": "uuid-string"
}

Response:
{
  "answer": "Analysis results...",
  "chart_url": "/static/chart_uuid.png",
  "code_used": "# Generated Python code...",
  "analysis_type": "visualization",
  "execution_time": 0.45,
  "session_id": "uuid-string"
}
```

## Frontend Components

### Core Components

#### 1. AnalysisWorkspace
- **Purpose**: Main application interface
- **Features**:
  - Three-panel layout (dataset, chat, results)
  - Real-time analysis streaming
  - Session management
  - Error handling

#### 2. ChatPanel
- **Purpose**: Question/answer interface
- **Features**:
  - Message history
  - Streaming responses
  - Code display toggle
  - Copy functionality

#### 3. DatasetInspector
- **Purpose**: Data overview and exploration
- **Features**:
  - Dataset statistics
  - Column information
  - Sample data display
  - Data type indicators

#### 4. ResultsPanel
- **Purpose**: Analysis results display
- **Features**:
  - Chart visualization
  - Table data display
  - Export capabilities
  - Result history

### UI Components (Shadcn/ui)
- **Button, Card, Dialog, Input, Table** - Basic UI elements
- **Accordion, Tabs, Tooltip** - Interactive components
- **Alert, Badge, Progress** - Status indicators
- **Form, Select, Textarea** - Form elements

## Development Workflow

### Local Development Setup
1. **Backend Setup**:
   ```bash
   pip install -r requirements.txt
   python main.py
   ```

2. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Docker Development**:
   ```bash
   docker-compose up --build
   ```

### Testing Strategy
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Security Tests**: Validation of security measures
- **Performance Tests**: Load and stress testing

### Code Quality
- **Type Safety**: TypeScript for frontend, Pydantic for backend
- **Linting**: ESLint for frontend, Black/Flake8 for backend
- **Code Formatting**: Prettier for frontend, Black for backend
- **Documentation**: Comprehensive docstrings and comments

## Deployment

### Production Architecture
```
Internet → Load Balancer → Nginx → FastAPI → StatBot Agent
                                 ↓
                               Static Files
                                 ↓
                               React App
```

### Deployment Options

#### 1. Docker Deployment
```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8001:8001"
    environment:
      - ENVIRONMENT=production
    volumes:
      - ./static:/app/static
      - ./workspace:/app/workspace
      - ./logs:/app/logs

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

#### 2. Cloud Deployment
- **AWS**: ECS, Lambda, S3
- **Google Cloud**: Cloud Run, Cloud Storage
- **Azure**: Container Instances, Blob Storage
- **Heroku**: Web dynos, add-ons

### Environment Configuration
```python
# config.py
class Settings:
    environment: str = "development"
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    rate_limit: int = 100  # requests per hour
    session_timeout: int = 3600  # 1 hour
    log_level: str = "INFO"
    cors_origins: List[str] = ["http://localhost:3000"]
```

## Monitoring and Observability

### Logging System
- **Structured Logging**: JSON format with correlation IDs
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Rotation**: Automatic log file rotation
- **Centralized Logging**: Support for external log aggregation

### Metrics Collection
- **System Metrics**: CPU, memory, disk usage
- **Application Metrics**: Request count, response time, error rate
- **Business Metrics**: Analysis count, user sessions, data volume
- **Custom Metrics**: Agent performance, code execution time

### Health Monitoring
```python
# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "uptime": get_uptime(),
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('.').percent
        }
    }
```

## Security Considerations

### Data Security
- **Input Validation**: Comprehensive data validation
- **File Type Restrictions**: Only CSV files allowed
- **Size Limits**: Maximum file size enforcement
- **Data Isolation**: Session-based data separation
- **Temporary Storage**: Automatic cleanup of uploaded files

### Code Execution Security
- **Sandboxed Environment**: Isolated Python execution
- **Import Restrictions**: Limited module access
- **Function Blocking**: Dangerous functions disabled
- **Resource Limits**: Memory and CPU constraints
- **Timeout Protection**: Execution time limits

### Network Security
- **CORS Configuration**: Controlled cross-origin access
- **Rate Limiting**: Request throttling
- **Input Sanitization**: XSS and injection prevention
- **HTTPS Enforcement**: Secure communication
- **Authentication**: Session-based access control

## Performance Optimization

### Backend Optimization
- **Async Processing**: Non-blocking request handling
- **Connection Pooling**: Efficient database connections
- **Caching**: Result and computation caching
- **Resource Management**: Efficient memory usage
- **Code Optimization**: Optimized analysis algorithms

### Frontend Optimization
- **Code Splitting**: Lazy loading of components
- **Bundle Optimization**: Minimized JavaScript bundles
- **Image Optimization**: Compressed static assets
- **Caching Strategy**: Browser and CDN caching
- **Performance Monitoring**: Real-time performance tracking

## Troubleshooting Guide

### Common Issues

#### 1. File Upload Failures
- **Cause**: File size exceeds limit
- **Solution**: Check file size, increase limit if needed
- **Prevention**: Client-side validation

#### 2. Analysis Timeouts
- **Cause**: Complex queries or large datasets
- **Solution**: Increase timeout, optimize queries
- **Prevention**: Query complexity analysis

#### 3. Memory Issues
- **Cause**: Large datasets or memory leaks
- **Solution**: Increase memory limits, optimize processing
- **Prevention**: Memory monitoring and cleanup

#### 4. Security Violations
- **Cause**: Unsafe code generation
- **Solution**: Review and fix code templates
- **Prevention**: Enhanced security validation

### Debug Tools
- **Logging**: Comprehensive debug logging
- **Health Checks**: System status monitoring
- **Performance Metrics**: Real-time performance data
- **Error Tracking**: Detailed error reporting

## Future Enhancements

### Planned Features
1. **Multi-format Support**: Excel, JSON, Parquet files
2. **Advanced Visualizations**: Interactive charts with D3.js
3. **Machine Learning**: Automated ML model generation
4. **Collaboration**: Multi-user sessions and sharing
5. **API Integration**: External data source connections
6. **Mobile Support**: Responsive mobile interface
7. **Export Options**: PDF reports, PowerPoint presentations
8. **Scheduled Analysis**: Automated recurring analysis

### Technical Improvements
1. **Performance**: Query optimization and caching
2. **Scalability**: Horizontal scaling support
3. **Security**: Enhanced sandboxing and validation
4. **Monitoring**: Advanced observability features
5. **Testing**: Comprehensive test coverage
6. **Documentation**: Interactive API documentation

## Contributing Guidelines

### Development Process
1. **Fork Repository**: Create personal fork
2. **Feature Branch**: Create feature-specific branch
3. **Development**: Implement changes with tests
4. **Code Review**: Submit pull request for review
5. **Testing**: Ensure all tests pass
6. **Deployment**: Merge to main branch

### Code Standards
- **Python**: Follow PEP 8, use type hints
- **TypeScript**: Follow ESLint rules, use strict types
- **Documentation**: Comprehensive docstrings and comments
- **Testing**: Unit and integration test coverage
- **Security**: Security-first development approach

### Review Checklist
- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] Security considerations addressed
- [ ] Performance impact assessed
- [ ] Backward compatibility maintained

---

This documentation provides a comprehensive overview of the StatBot Pro project, covering architecture, features, deployment, and development practices. Use this information to create detailed Notion project documentation with proper organization, formatting, and cross-references.