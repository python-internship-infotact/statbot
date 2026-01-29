import React, { useState, useCallback } from 'react';
import { DatasetInspector } from './DatasetInspector';
import { ChatPanel } from './ChatPanel';
import { ResultsPanel } from './ResultsPanel';
import { apiClient } from '@/lib/api';
import type { DatasetInfo, ChatMessage, AgentStep } from '@/types/statbot';

interface AnalysisWorkspaceProps {
  dataset: DatasetInfo;
  onReset: () => void;
}

export const AnalysisWorkspace: React.FC<AnalysisWorkspaceProps> = ({ dataset, onReset }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showReasoning, setShowReasoning] = useState(true);

  const handleSendMessage = useCallback(async (content: string) => {
    // Add user message
    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      timestamp: new Date(),
    };

    // Add placeholder agent message
    const agentMessageId = crypto.randomUUID();
    const agentMessage: ChatMessage = {
      id: agentMessageId,
      role: 'agent',
      content: '',
      timestamp: new Date(),
      steps: [],
      isStreaming: true,
    };

    setMessages(prev => [...prev, userMessage, agentMessage]);
    setIsAnalyzing(true);

    try {
      // Simulate streaming steps for better UX
      const steps: Array<{ type: AgentStep['type']; message: string; delay: number }> = [
        { type: 'loading', message: 'Loading dataset into memory...', delay: 200 },
        { type: 'analyzing', message: 'Analyzing your question...', delay: 300 },
        { type: 'coding', message: 'Generating analysis code...', delay: 400 },
        { type: 'executing', message: 'Running analysis...', delay: 500 },
      ];

      // Show streaming steps
      for (const step of steps) {
        await new Promise(resolve => setTimeout(resolve, step.delay));
        const newStep: AgentStep = {
          id: crypto.randomUUID(),
          type: step.type,
          message: step.message,
          timestamp: new Date(),
        };
        
        setMessages(prev => prev.map(msg => 
          msg.id === agentMessageId 
            ? { ...msg, steps: [...(msg.steps || []), newStep] }
            : msg
        ));
      }

      // Call the actual API
      const response = await apiClient.askQuestion(content, dataset.id);

      // Add final step
      const finalStep: AgentStep = {
        id: crypto.randomUUID(),
        type: 'complete',
        message: 'Analysis complete',
        timestamp: new Date(),
      };

      // Determine result type and prepare result data
      let result: ChatMessage['result'] | undefined;
      
      if (response.chart_url) {
        result = {
          type: 'chart',
          content: response.answer,
          chartUrl: apiClient.getStaticUrl(response.chart_url),
        };
      } else {
        // Try to extract table data from the answer if it looks like tabular data
        const lines = response.answer.split('\n');
        const tableLines = lines.filter(line => line.includes('|') || line.includes('\t'));
        
        if (tableLines.length > 2) {
          result = {
            type: 'table',
            content: response.answer,
            tableData: [
              { Metric: 'Analysis Type', Value: response.analysis_type },
              { Metric: 'Execution Time', Value: `${response.execution_time.toFixed(2)}s` },
            ],
          };
        } else {
          result = {
            type: 'text',
            content: response.answer,
          };
        }
      }

      // Update the message with final result and add code to the coding step
      setMessages(prev => prev.map(msg =>
        msg.id === agentMessageId
          ? { 
              ...msg, 
              content: response.answer, 
              result, 
              isStreaming: false,
              steps: [
                ...(msg.steps || []).map(step => 
                  step.type === 'coding' 
                    ? { ...step, code: response.code_used }
                    : step
                ),
                finalStep
              ]
            }
          : msg
      ));

    } catch (error) {
      // Handle error
      const errorStep: AgentStep = {
        id: crypto.randomUUID(),
        type: 'error',
        message: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date(),
      };

      const errorResult: ChatMessage['result'] = {
        type: 'error',
        content: error instanceof Error ? error.message : 'An error occurred while processing your question.',
      };

      setMessages(prev => prev.map(msg =>
        msg.id === agentMessageId
          ? { 
              ...msg, 
              content: 'Sorry, I encountered an error while processing your question.',
              result: errorResult,
              isStreaming: false,
              steps: [...(msg.steps || []), errorStep]
            }
          : msg
      ));
    } finally {
      setIsAnalyzing(false);
    }
  }, [dataset.id]);

  const handleReset = useCallback(() => {
    setMessages([]);
    onReset();
  }, [onReset]);

  return (
    <div className="h-screen flex">
      {/* Left Panel - Dataset Inspector */}
      <div className="w-72 shrink-0">
        <DatasetInspector dataset={dataset} />
      </div>

      {/* Center Panel - Chat */}
      <div className="flex-1 min-w-0">
        <ChatPanel
          dataset={dataset}
          messages={messages}
          onSendMessage={handleSendMessage}
          isAnalyzing={isAnalyzing}
          showReasoning={showReasoning}
          onToggleReasoning={() => setShowReasoning(prev => !prev)}
          onReset={handleReset}
        />
      </div>

      {/* Right Panel - Results */}
      <div className="w-80 shrink-0">
        <ResultsPanel messages={messages} />
      </div>
    </div>
  );
};
