# StatBot Pro

An autonomous CSV data analyst agent with a modern React frontend that generates Python code to answer natural language questions about your data.

## 🚀 Features

- **Modern Web Interface**: Beautiful React frontend with real-time chat interface
- **Autonomous Analysis**: Upload CSV files and ask questions in natural language
- **Self-Correcting Agent**: Automatically retries and fixes code execution errors
- **Secure Sandboxing**: Restricted execution environment with no filesystem access
- **Chart Generation**: Automatic matplotlib visualizations saved as PNG files
- **Real-time Processing**: Stream analysis steps for transparency
- **REST API**: Full API access for programmatic usage
- **Session Management**: Maintain context across multiple questions

## 🏗️ Architecture

- **Frontend**: React + TypeScript + Vite + shadcn/ui
- **Backend**: FastAPI (Python)
- **Agent Framework**: Custom implementation with LangChain concepts
- **Data Processing**: Pandas DataFrame operations
- **Visualization**: Matplotlib with automatic chart generation
- **Security**: Sandboxed code execution with restricted imports
- **Storage**: Local filesystem with public URLs for charts

## ✅ System Status

**Frontend-Backend Integration**: ✅ **FULLY INTEGRATED & CLEAN**
- Modern React frontend with real-time chat interface
- Complete API integration with backend
- Session management working correctly
- File upload and question processing functional
- Chart visualization support
- Error handling and user feedback
- All third-party references removed

**Current Features**:
- ✅ CSV file upload with drag-and-drop interface
- ✅ Real-time data analysis with AI agent
- ✅ Interactive chat interface for questions
- ✅ Automatic chart generation and display
- ✅ Session-based data management
- ✅ Comprehensive error handling
- ✅ Production-ready backend with monitoring
- ✅ Modern UI with shadcn/ui components
- ✅ Clean codebase with no external dependencies

## 🚀 Quick Start

### Option 1: Development Mode (Recommended)

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Install Node.js dependencies:**
```bash
cd frontend
npm install
cd ..
```

3. **Start both servers:**
```bash
# Windows
start-dev.bat

# Linux/Mac
python start-dev.py
```

4. **Access the application:**
- Frontend UI: http://localhost:8080
- Backend API: http://localhost:8001

### Option 2: Manual Setup

1. **Start the backend:**
```bash
python main.py
```

2. **Start the frontend (in another terminal):**
```bash
cd frontend
npm run dev
```

### Option 3: Docker Setup (Production)

1. **Build and run with Docker Compose:**
```bash
docker-compose up --build
```

2. **Access the application:**
```
http://localhost:8000
```

## 📊 Usage Examples

### Modern Web Interface
1. Open http://localhost:8080 in your browser
2. Upload a CSV file using the drag-and-drop interface
3. Ask questions in the chat interface like:
   - "What is the correlation between sales and marketing spend?"
   - "Show me the sales trend by region"
   - "Create a scatter plot of price vs quantity"
   - "Which product category has the highest average revenue?"

### Legacy Web Interface
1. Open http://localhost:8001 in your browser
2. Upload a CSV file using the file picker
3. Ask questions like:
   - "What is the correlation between sales and marketing spend?"
   - "Show me the sales trend by region"
   - "Create a scatter plot of price vs quantity"
   - "Which product category has the highest average revenue?"

### API Usage

**Upload CSV:**
```bash
curl -X POST -F "file=@data.csv" http://localhost:8001/upload_csv
```

**Ask Question:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"question": "What is the correlation between sales and marketing spend?"}' \
  http://localhost:8001/ask_question
```

**Access Generated Charts:**
```bash
# Charts are available at /static/{chart_name}.png
curl http://localhost:8001/static/chart_abc123.png
```

## 🔒 Security Features

- **Sandboxed Execution**: Code runs in restricted environment
- **Limited Imports**: Only pandas, numpy, matplotlib, math allowed
- **No File System Access**: Cannot read/write files outside workspace
- **No Shell Commands**: subprocess, os.system blocked
- **Execution Timeout**: Prevents infinite loops
- **Input Validation**: All inputs sanitized and validated

## 🤖 Agent Capabilities

### Autonomous Behavior
- Inspects dataframe schema before analysis
- Generates appropriate Python code based on question intent
- Self-corrects on execution errors (up to 3 retries)
- Automatically determines if visualization is needed
- Provides transparent step-by-step progress

### Supported Analysis Types
- **Statistical Analysis**: Mean, median, correlation, distribution
- **Data Exploration**: Shape, columns, data types, missing values
- **Visualizations**: Histograms, scatter plots, line charts, heatmaps
- **Comparative Analysis**: Group by operations, regional comparisons
- **Trend Analysis**: Time series patterns, rolling averages

### Example Questions
- "What are the summary statistics for all numeric columns?"
- "Show me a correlation matrix heatmap"
- "Plot sales over time with a 3-month rolling average"
- "Which region has the most consistent performance?"
- "Create a box plot showing price distribution by category"
- "Find outliers in the revenue data"

## 📁 Project Structure

```
statbot-pro/
├── main.py                 # FastAPI server
├── agent.py               # Autonomous agent implementation
├── config.py              # Configuration management
├── monitoring.py          # System monitoring
├── requirements.txt       # Python dependencies
├── start-dev.py           # Development startup script
├── start-dev.bat          # Windows development startup
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose setup
├── frontend/             # React frontend application
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── lib/          # Utilities and API client
│   │   └── types/        # TypeScript type definitions
│   ├── package.json      # Node.js dependencies
│   └── vite.config.ts    # Vite configuration
├── templates/
│   └── index.html        # Legacy web interface
├── workspace/            # CSV upload directory
├── static/              # Generated charts
├── example_data.csv     # Sample dataset
├── test_examples.py     # Basic API tests
├── advanced_test.py     # Advanced functionality tests
└── README.md           # This file
```

## 🧪 Testing

### Basic Functionality Test
```bash
python test_examples.py
```

### Advanced Features Test
```bash
python advanced_test.py
```

### Manual Testing
1. Start the server: `python main.py`
2. Open http://localhost:8001
3. Upload `example_data.csv`
4. Try the example questions provided in the interface

## 🔧 Configuration

### Environment Variables
- `PORT`: Server port (default: 8001)
- `HOST`: Server host (default: 0.0.0.0)
- `WORKSPACE_DIR`: CSV upload directory (default: ./workspace)
- `STATIC_DIR`: Chart output directory (default: ./static)

### Security Settings
The agent's security settings are configured in `agent.py`:
- `ALLOWED_MODULES`: Permitted Python modules
- `BLOCKED_BUILTINS`: Restricted built-in functions
- `timeout`: Code execution timeout (default: 30 seconds)

## 🚀 Production Deployment

### Docker Deployment (Recommended)
```bash
# Build the image
docker build -t statbot-pro .

# Run with custom port
docker run -p 8080:8000 -v $(pwd)/data:/app/workspace statbot-pro
```

### Security Considerations
- Run behind a reverse proxy (nginx/Apache)
- Enable HTTPS with SSL certificates
- Implement rate limiting
- Add authentication if needed
- Monitor resource usage
- Regular security updates

## 🤝 API Reference

### Endpoints

#### `POST /upload_csv`
Upload a CSV file for analysis.

**Request:**
- Content-Type: multipart/form-data
- Body: CSV file

**Response:**
```json
{
  "message": "CSV uploaded successfully",
  "filename": "unique_filename.csv",
  "shape": [rows, columns],
  "columns": ["col1", "col2", ...],
  "sample": [{"col1": "val1", ...}, ...]
}
```

#### `POST /ask_question`
Ask a natural language question about the uploaded data.

**Request:**
```json
{
  "question": "What is the correlation between sales and marketing spend?"
}
```

**Response:**
```json
{
  "answer": "Analysis results...",
  "chart_url": "/static/chart_abc123.png",
  "code_used": "Generated Python code",
  "analysis_type": "visualization|computation",
  "dataframe_info": {...}
}
```

#### `GET /static/{image_name}`
Access generated chart images.

#### `GET /health`
Health check endpoint.

## 🐛 Troubleshooting

### Common Issues

**Port Already in Use:**
```bash
# Change port in main.py or use environment variable
PORT=8002 python main.py
```

**Dependencies Issues:**
```bash
# Clean install
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

**Chart Generation Fails:**
- Ensure matplotlib backend is set correctly
- Check static directory permissions
- Verify sufficient disk space

**Memory Issues with Large CSV:**
- Implement chunking for large files
- Add memory monitoring
- Consider using Dask for big data

## 📈 Performance Tips

- Use smaller CSV files for faster processing
- Cache frequently used datasets
- Implement connection pooling for high traffic
- Monitor memory usage with large datasets
- Use async processing for multiple requests

## 🔮 Future Enhancements

- Support for multiple file formats (Excel, JSON, Parquet)
- Advanced ML capabilities (clustering, classification)
- Real-time data streaming support
- Multi-user session management
- Advanced visualization libraries (Plotly, Seaborn)
- Natural language to SQL conversion
- Integration with cloud storage (S3, GCS)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the API documentation