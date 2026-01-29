import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Eye, EyeOff, RotateCcw } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { AgentMessage } from './AgentMessage';
import type { ChatMessage, DatasetInfo, AgentStep } from '@/types/statbot';

interface ChatPanelProps {
  dataset: DatasetInfo;
  messages: ChatMessage[];
  onSendMessage: (message: string) => void;
  isAnalyzing: boolean;
  showReasoning: boolean;
  onToggleReasoning: () => void;
  onReset: () => void;
}

const suggestedFollowUps = [
  'Can you break this down by month?',
  'Show me the top 5 performers',
  'What patterns do you see?',
  'Compare this to the previous period',
];

export const ChatPanel: React.FC<ChatPanelProps> = ({
  dataset,
  messages,
  onSendMessage,
  isAnalyzing,
  showReasoning,
  onToggleReasoning,
  onReset,
}) => {
  const [input, setInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isAnalyzing) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="h-full flex flex-col bg-background">
      {/* Header */}
      <div className="px-4 py-3 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-primary" />
          <span className="font-medium text-sm">Analysis Chat</span>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggleReasoning}
            className="h-8 text-xs gap-1.5"
          >
            {showReasoning ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
            {showReasoning ? 'Reasoning On' : 'Reasoning Off'}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={onReset}
            className="h-8 text-xs gap-1.5"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Reset
          </Button>
        </div>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 p-4" ref={scrollRef}>
        <div className="space-y-6">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-12 h-12 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-4">
                <Sparkles className="w-6 h-6 text-primary" />
              </div>
              <h3 className="font-semibold text-lg mb-2">Ask me anything about your data</h3>
              <p className="text-sm text-muted-foreground max-w-sm mx-auto">
                I can analyze trends, find correlations, create visualizations, and help you understand your {dataset.fileName} dataset.
              </p>
            </div>
          ) : (
            messages.map((message) => (
              <AgentMessage 
                key={message.id} 
                message={message} 
                showReasoning={showReasoning}
              />
            ))
          )}
        </div>
      </ScrollArea>

      {/* Follow-up suggestions */}
      {messages.length > 0 && !isAnalyzing && (
        <div className="px-4 py-2 border-t border-border">
          <div className="flex items-center gap-2 overflow-x-auto scrollbar-thin pb-1">
            <span className="text-xs text-muted-foreground shrink-0">Follow up:</span>
            {suggestedFollowUps.slice(0, 3).map((suggestion) => (
              <button
                key={suggestion}
                onClick={() => onSendMessage(suggestion)}
                className="shrink-0 text-xs px-3 py-1.5 rounded-full bg-secondary hover:bg-secondary/80 transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-border">
        <div className="relative">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about your data..."
            disabled={isAnalyzing}
            rows={1}
            className={cn(
              'w-full resize-none rounded-xl bg-secondary border-0 px-4 py-3 pr-12',
              'text-sm placeholder:text-muted-foreground',
              'focus:outline-none focus:ring-2 focus:ring-primary/50',
              'disabled:opacity-50'
            )}
            style={{ minHeight: '48px', maxHeight: '120px' }}
          />
          <Button
            type="submit"
            size="icon"
            disabled={!input.trim() || isAnalyzing}
            className="absolute right-2 top-1/2 -translate-y-1/2 h-8 w-8 rounded-lg"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </form>
    </div>
  );
};
