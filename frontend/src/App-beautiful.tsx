import React, { useState } from 'react';

// Types
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

// Beautiful Landing Component
const BeautifulLanding: React.FC<{ onUploadComplete: (dataset: DatasetInfo) => void }> = ({ onUploadComplete }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  const handleFileUpload = async (file: File) => {
    setIsUploading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/upload_csv', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        
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

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const file = e.dataTransfer.files?.[0];
    if (file && file.name.endsWith('.csv')) {
      handleFileUpload(file);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white overflow-hidden relative">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse animation-delay-2000"></div>
        <div className="absolute top-40 left-1/2 w-80 h-80 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse animation-delay-4000"></div>
      </div>

      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen p-8">
        {/* Header */}
        <div className="text-center mb-16 animate-fade-in">
          <div className="flex items-center justify-center mb-6">
            <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-2xl">
              <span className="text-2xl">📊</span>
            </div>
          </div>
          <h1 className="text-6xl md:text-7xl font-bold bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 bg-clip-text text-transparent mb-6">
            StatBot Pro
          </h1>
          <p className="text-xl md:text-2xl text-gray-300 max-w-2xl mx-auto leading-relaxed">
            Transform your CSV data into insights with AI-powered analysis. 
            <span className="text-blue-400 font-semibold"> Ask questions in plain English.</span>
          </p>
        </div>

        {/* Upload Zone */}
        <div className="w-full max-w-2xl mb-16">
          <div
            className={`relative group transition-all duration-300 ${
              dragActive ? 'scale-105' : 'hover:scale-102'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <div className={`absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-600 rounded-3xl blur-lg opacity-30 group-hover:opacity-50 transition-opacity duration-300 ${
              dragActive ? 'opacity-70' : ''
            }`}></div>
            
            <div className={`relative bg-slate-800/50 backdrop-blur-xl border-2 border-dashed rounded-3xl p-12 text-center transition-all duration-300 ${
              dragActive 
                ? 'border-blue-400 bg-blue-500/10' 
                : 'border-gray-600 hover:border-gray-500'
            }`}>
              {isUploading ? (
                <div className="animate-pulse">
                  <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
                  </div>
                  <h3 className="text-2xl font-semibold mb-2 text-blue-400">Processing your data...</h3>
                  <p className="text-gray-400">Analyzing columns and detecting data types</p>
                </div>
              ) : (
                <>
                  <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-2xl group-hover:shadow-blue-500/25 transition-shadow duration-300">
                    <span className="text-3xl">⬆️</span>
                  </div>
                  <h3 className="text-2xl font-semibold mb-4">Drop your CSV here</h3>
                  <p className="text-gray-400 mb-6">or click to browse your files</p>
                  
                  <input
                    type="file"
                    accept=".csv"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) handleFileUpload(file);
                    }}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  />
                  
                  <div className="flex items-center justify-center space-x-6 text-sm text-gray-500">
                    <div className="flex items-center">
                      <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                      Max 50MB
                    </div>
                    <div className="flex items-center">
                      <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                      Auto-detect types
                    </div>
                    <div className="flex items-center">
                      <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                      Secure processing
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl w-full">
          {[
            {
              icon: "✨",
              title: "Natural Language",
              description: "Ask questions like 'What's the correlation between sales and marketing spend?'",
              color: "from-yellow-400 to-orange-500"
            },
            {
              icon: "⚡",
              title: "Instant Analysis",
              description: "Get comprehensive insights and visualizations in seconds",
              color: "from-blue-400 to-cyan-500"
            },
            {
              icon: "🛡️",
              title: "Enterprise Ready",
              description: "Secure processing with no data storage or external sharing",
              color: "from-green-400 to-emerald-500"
            }
          ].map((feature, index) => (
            <div
              key={feature.title}
              className="group relative animate-fade-in-up"
              style={{ animationDelay: `${index * 200}ms` }}
            >
              <div className="absolute inset-0 bg-gradient-to-r opacity-0 group-hover:opacity-20 rounded-2xl blur transition-opacity duration-300"
                   style={{ backgroundImage: `linear-gradient(135deg, var(--tw-gradient-stops))` }}></div>
              
              <div className="relative bg-slate-800/30 backdrop-blur-sm border border-gray-700 rounded-2xl p-8 text-center hover:border-gray-600 transition-all duration-300 group-hover:transform group-hover:scale-105">
                <div className={`w-16 h-16 mx-auto mb-4 bg-gradient-to-r ${feature.color} rounded-2xl flex items-center justify-center text-2xl shadow-lg`}>
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
                <p className="text-gray-400 leading-relaxed">{feature.description}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="mt-16 text-center text-gray-500">
          <p className="text-sm">Your data is processed locally and never stored permanently</p>
        </div>
      </div>

      <style jsx>{`
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes fade-in-up {
          from { opacity: 0; transform: translateY(30px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in {
          animation: fade-in 1s ease-out;
        }
        .animate-fade-in-up {
          animation: fade-in-up 0.8s ease-out both;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
        .hover\\:scale-102:hover {
          transform: scale(1.02);
        }
      `}</style>
    </div>
  );
};

// Beautiful Chat Component
const BeautifulChat: React.FC<{ dataset: DatasetInfo; onReset: () => void }> = ({ dataset, onReset }) => {
  const [messages, setMessages] = useState<Array<{
    id: string;
    role: 'user' | 'agent';
    content: string;
    timestamp: Date;
    chartUrl?: string;
    isStreaming?: boolean;
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

    const agentMessage = {
      id: (Date.now() + 1).toString(),
      role: 'agent' as const,
      content: '',
      timestamp: new Date(),
      isStreaming: true,
    };

    setMessages(prev => [...prev, userMessage, agentMessage]);
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
        setMessages(prev => prev.map(msg => 
          msg.id === agentMessage.id 
            ? { ...msg, content: data.answer, chartUrl: data.chart_url, isStreaming: false }
            : msg
        ));
      } else {
        setMessages(prev => prev.map(msg => 
          msg.id === agentMessage.id 
            ? { ...msg, content: 'Sorry, I encountered an error processing your question.', isStreaming: false }
            : msg
        ));
      }
    } catch (error) {
      console.error('Question error:', error);
      setMessages(prev => prev.map(msg => 
        msg.id === agentMessage.id 
          ? { ...msg, content: 'Sorry, I encountered a connection error.', isStreaming: false }
          : msg
      ));
    } finally {
      setIsAnalyzing(false);
    }
  };

  const suggestedQuestions = [
    "What are the summary statistics?",
    "Show me a correlation matrix",
    "Create a visualization",
    "Find any outliers in the data"
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white flex flex-col">
      {/* Animated background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-pulse"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-pulse animation-delay-2000"></div>
      </div>

      {/* Header */}
      <div className="relative z-10 bg-slate-800/50 backdrop-blur-xl border-b border-gray-700">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                <span className="text-lg">📊</span>
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                  StatBot Pro
                </h1>
                <p className="text-sm text-gray-400">
                  {dataset.fileName} • {dataset.rowCount.toLocaleString()} rows • {dataset.columns.length} columns
                </p>
              </div>
            </div>
            <button
              onClick={onReset}
              className="px-4 py-2 bg-gradient-to-r from-gray-700 to-gray-600 hover:from-gray-600 hover:to-gray-500 rounded-xl text-sm font-medium transition-all duration-200 hover:scale-105"
            >
              Upload New File
            </button>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="relative z-10 flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {messages.length === 0 ? (
            <div className="text-center py-16 animate-fade-in">
              <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <span className="text-3xl">💬</span>
              </div>
              <h2 className="text-2xl font-bold mb-4">Ask me anything about your data</h2>
              <p className="text-gray-400 mb-8 max-w-md mx-auto">
                I can analyze trends, create visualizations, find correlations, and answer questions about your CSV data.
              </p>
              
              <div className="grid grid-cols-2 gap-3 max-w-lg mx-auto">
                {suggestedQuestions.map((question, index) => (
                  <button
                    key={index}
                    onClick={() => handleSendMessage(question)}
                    className="p-3 bg-slate-800/50 hover:bg-slate-700/50 border border-gray-700 hover:border-gray-600 rounded-xl text-sm transition-all duration-200 hover:scale-105"
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={message.id}
                className={`flex animate-fade-in-up ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div
                  className={`max-w-3xl p-6 rounded-2xl shadow-lg ${
                    message.role === 'user'
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                      : 'bg-slate-800/70 backdrop-blur-sm border border-gray-700 text-gray-100'
                  }`}
                >
                  {message.isStreaming ? (
                    <div className="flex items-center space-x-3">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce animation-delay-200"></div>
                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce animation-delay-400"></div>
                      </div>
                      <span className="text-gray-400">Analyzing your question...</span>
                    </div>
                  ) : (
                    <>
                      <div className="whitespace-pre-wrap font-mono text-sm leading-relaxed">
                        {message.content}
                      </div>
                      {message.chartUrl && (
                        <div className="mt-4 p-4 bg-white rounded-xl">
                          <img
                            src={message.chartUrl}
                            alt="Generated chart"
                            className="max-w-full h-auto rounded-lg shadow-lg"
                          />
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Input */}
      <div className="relative z-10 bg-slate-800/50 backdrop-blur-xl border-t border-gray-700">
        <div className="max-w-4xl mx-auto p-6">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage(input);
            }}
            className="relative"
          >
            <div className="relative">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask a question about your data..."
                disabled={isAnalyzing}
                className="w-full px-6 py-4 pr-16 bg-slate-700/50 border border-gray-600 rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200"
              />
              <button
                type="submit"
                disabled={!input.trim() || isAnalyzing}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 disabled:from-gray-600 disabled:to-gray-600 disabled:cursor-not-allowed rounded-xl flex items-center justify-center transition-all duration-200 hover:scale-105"
              >
                <span className="text-xl">🚀</span>
              </button>
            </div>
          </form>
        </div>
      </div>

      <style jsx>{`
        .animation-delay-200 {
          animation-delay: 0.2s;
        }
        .animation-delay-400 {
          animation-delay: 0.4s;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
      `}</style>
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
    return <BeautifulChat dataset={dataset} onReset={handleReset} />;
  }

  return <BeautifulLanding onUploadComplete={setDataset} />;
};

export default App;