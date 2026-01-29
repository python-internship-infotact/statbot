import React, { useState } from 'react';

// Simple types without external imports
interface DatasetInfo {
  id: string;
  fileName: string;
  rowCount: number;
  columns: Array<{
    name: string;
    type: 'string' | 'number' | 'date' | 'boolean';
    sampleValues: string[];
  }>;
  sampleData: Record<string, unknown>[];
  uploadedAt: Date;
}

// Simple Landing Component
const SimpleLanding: React.FC<{ onUploadComplete: (dataset: DatasetInfo) => void }> = ({ onUploadComplete }) => {
  const [isUploading, setIsUploading] = useState(false);

  const handleFileUpload = async (file: File) => {
    setIsUploading(true);
    
    try {
      // Create FormData and upload to backend
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/upload_csv', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        
        // Convert backend response to DatasetInfo
        const dataset: DatasetInfo = {
          id: data.session_id,
          fileName: file.name,
          rowCount: data.shape[0],
          columns: data.columns.map((name: string) => ({
            name,
            type: data.data_types[name] === 'object' ? 'string' as const : 
                  data.data_types[name].includes('int') || data.data_types[name].includes('float') ? 'number' as const :
                  data.data_types[name].includes('datetime') ? 'date' as const : 'string' as const,
            sampleValues: data.sample.slice(0, 3).map((row: any) => String(row[name] || '')),
          })),
          sampleData: data.sample.slice(0, 10),
          uploadedAt: new Date(),
        };

        onUploadComplete(dataset);
      } else {
        alert('Upload failed. Please try again.');
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Upload failed. Please check your connection.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-4xl mx-auto text-center">
        <h1 className="text-5xl font-bold mb-4">StatBot Pro</h1>
        <p className="text-xl text-gray-300 mb-12">
          AI-powered CSV data analysis tool
        </p>
        
        <div className="bg-gray-800 border-2 border-dashed border-gray-600 rounded-xl p-12 mb-8">
          <div className="text-6xl mb-4">📊</div>
          <h2 className="text-2xl font-semibold mb-4">Upload your CSV file</h2>
          <p className="text-gray-400 mb-6">
            Drag and drop your CSV file here or click to browse
          </p>
          
          <input
            type="file"
            accept=".csv"
            disabled={isUploading}
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleFileUpload(file);
            }}
            className="block w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700 file:cursor-pointer cursor-pointer"
          />
          
          {isUploading && (
            <div className="mt-4 text-blue-400">
              Uploading and processing your file...
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="text-3xl mb-3">✨</div>
            <h3 className="text-lg font-semibold mb-2">Natural Language</h3>
            <p className="text-gray-400">Ask questions in plain English</p>
          </div>
          <div className="text-center">
            <div className="text-3xl mb-3">⚡</div>
            <h3 className="text-lg font-semibold mb-2">Instant Analysis</h3>
            <p className="text-gray-400">Get insights in seconds</p>
          </div>
          <div className="text-center">
            <div className="text-3xl mb-3">🛡️</div>
            <h3 className="text-lg font-semibold mb-2">Secure</h3>
            <p className="text-gray-400">Your data stays private</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Simple Chat Component
const SimpleChat: React.FC<{ dataset: DatasetInfo; onReset: () => void }> = ({ dataset, onReset }) => {
  const [messages, setMessages] = useState<Array<{
    id: string;
    role: 'user' | 'agent';
    content: string;
    timestamp: Date;
    chartUrl?: string;
  }>>([]);
  const [input, setInput] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleSendMessage = async (question: string) => {
    if (!question.trim() || isAnalyzing) return;

    const userMessage = {
      id: Date.now().toString(),
      role: 'user' as const,
      content: question,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsAnalyzing(true);

    try {
      const response = await fetch('/api/ask_question', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question,
          session_id: dataset.id,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const agentMessage = {
          id: (Date.now() + 1).toString(),
          role: 'agent' as const,
          content: data.answer,
          timestamp: new Date(),
          chartUrl: data.chart_url,
        };
        setMessages(prev => [...prev, agentMessage]);
      } else {
        const errorMessage = {
          id: (Date.now() + 1).toString(),
          role: 'agent' as const,
          content: 'Sorry, I encountered an error processing your question.',
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Question error:', error);
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        role: 'agent' as const,
        content: 'Sorry, I encountered a connection error.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col">
      {/* Header */}
      <div className="bg-gray-800 p-4 border-b border-gray-700">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold">StatBot Pro</h1>
            <p className="text-sm text-gray-400">
              Analyzing: {dataset.fileName} ({dataset.rowCount} rows)
            </p>
          </div>
          <button
            onClick={onReset}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm"
          >
            Upload New File
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-4xl mb-4">💬</div>
              <h2 className="text-xl font-semibold mb-2">Ask me anything about your data</h2>
              <p className="text-gray-400">
                I can analyze trends, create visualizations, and answer questions about your CSV data.
              </p>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-2xl p-4 rounded-lg ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-800 text-gray-100'
                  }`}
                >
                  <div className="whitespace-pre-wrap">{message.content}</div>
                  {message.chartUrl && (
                    <div className="mt-3">
                      <img
                        src={message.chartUrl}
                        alt="Generated chart"
                        className="max-w-full h-auto rounded border"
                      />
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          {isAnalyzing && (
            <div className="flex justify-start">
              <div className="bg-gray-800 p-4 rounded-lg">
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-400"></div>
                  <span className="text-gray-400">Analyzing your question...</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Input */}
      <div className="bg-gray-800 p-4 border-t border-gray-700">
        <div className="max-w-4xl mx-auto">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage(input);
            }}
            className="flex space-x-4"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about your data..."
              disabled={isAnalyzing}
              className="flex-1 px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
            />
            <button
              type="submit"
              disabled={!input.trim() || isAnalyzing}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-medium"
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

// Main App Component
const App = () => {
  const [dataset, setDataset] = useState<DatasetInfo | null>(null);

  const handleReset = () => {
    setDataset(null);
  };

  if (dataset) {
    return <SimpleChat dataset={dataset} onReset={handleReset} />;
  }

  return <SimpleLanding onUploadComplete={setDataset} />;
};

export default App;