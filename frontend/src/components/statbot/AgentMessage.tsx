import React, { useState } from 'react';
import { Bot, User, CheckCircle2, Loader2, Code2, AlertTriangle, ChevronDown, ChevronRight, Copy, Check } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { ChatMessage, AgentStep, AgentStepType } from '@/types/statbot';
import { Button } from '@/components/ui/button';

interface AgentMessageProps {
  message: ChatMessage;
  showReasoning: boolean;
}

const stepIcons: Record<AgentStepType, React.ElementType> = {
  loading: Loader2,
  analyzing: Loader2,
  coding: Code2,
  executing: Loader2,
  plotting: Loader2,
  complete: CheckCircle2,
  error: AlertTriangle,
};

const stepColors: Record<AgentStepType, string> = {
  loading: 'text-muted-foreground',
  analyzing: 'text-accent',
  coding: 'text-agent-code',
  executing: 'text-accent',
  plotting: 'text-primary',
  complete: 'text-success',
  error: 'text-destructive',
};

export const AgentMessage: React.FC<AgentMessageProps> = ({ message, showReasoning }) => {
  const [codeExpanded, setCodeExpanded] = useState(false);
  const [copied, setCopied] = useState(false);
  
  const isUser = message.role === 'user';
  const hasSteps = message.steps && message.steps.length > 0;
  const codeStep = message.steps?.find(s => s.type === 'coding');

  const handleCopy = async () => {
    if (message.content) {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className={cn('flex gap-3 animate-fade-in-up', isUser ? 'flex-row-reverse' : '')}>
      {/* Avatar */}
      <div className={cn(
        'w-8 h-8 rounded-lg flex items-center justify-center shrink-0',
        isUser ? 'bg-primary' : 'bg-secondary'
      )}>
        {isUser ? (
          <User className="w-4 h-4 text-primary-foreground" />
        ) : (
          <Bot className="w-4 h-4 text-foreground" />
        )}
      </div>

      {/* Content */}
      <div className={cn('flex-1 max-w-[85%] space-y-2', isUser ? 'items-end' : '')}>
        {/* Main message bubble */}
        <div className={cn(
          'rounded-2xl px-4 py-3',
          isUser ? 'bg-primary text-primary-foreground rounded-tr-md' : 'bg-secondary rounded-tl-md'
        )}>
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        </div>

        {/* Agent reasoning steps */}
        {!isUser && showReasoning && hasSteps && (
          <div className="space-y-1.5 pl-2 border-l-2 border-border ml-2">
            {message.steps!.map((step) => {
              const Icon = stepIcons[step.type];
              return (
                <div key={step.id} className="flex items-center gap-2 text-xs">
                  <Icon className={cn(
                    'w-3.5 h-3.5',
                    stepColors[step.type],
                    (step.type === 'loading' || step.type === 'analyzing' || step.type === 'executing' || step.type === 'plotting') && message.isStreaming && 'animate-spin'
                  )} />
                  <span className="text-muted-foreground">{step.message}</span>
                </div>
              );
            })}
          </div>
        )}

        {/* Streaming indicator */}
        {!isUser && message.isStreaming && (
          <div className="thinking-indicator ml-2">
            <span></span>
            <span></span>
            <span></span>
          </div>
        )}

        {/* Code block (collapsed by default) */}
        {!isUser && codeStep && (
          <div className="mt-2">
            <button
              onClick={() => setCodeExpanded(!codeExpanded)}
              className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
            >
              {codeExpanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
              <Code2 className="w-3 h-3" />
              <span>View generated code</span>
            </button>
            {codeExpanded && (
              <div className="mt-2 p-3 rounded-lg bg-background border border-border font-mono text-xs overflow-x-auto">
                <pre className="text-muted-foreground">
                  {codeStep.code || `# Generated analysis code
# Code will be displayed here when available`}
                </pre>
              </div>
            )}
          </div>
        )}

        {/* Result display */}
        {!isUser && message.result && (
          <div className="mt-3">
            {message.result.type === 'chart' && message.result.chartUrl && (
              <div className="rounded-lg overflow-hidden border border-border bg-background p-2">
                <img 
                  src={message.result.chartUrl} 
                  alt="Analysis chart"
                  className="w-full h-auto rounded"
                />
              </div>
            )}
            
            {message.result.type === 'table' && message.result.tableData && (
              <div className="rounded-lg border border-border overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead className="bg-secondary">
                      <tr>
                        {Object.keys(message.result.tableData[0] || {}).map((key) => (
                          <th key={key} className="text-left py-2 px-3 font-medium">{key}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {message.result.tableData.map((row, idx) => (
                        <tr key={idx} className="border-t border-border">
                          {Object.values(row).map((val, vIdx) => (
                            <td key={vIdx} className="py-2 px-3 font-mono text-muted-foreground">
                              {String(val)}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {message.result.type === 'error' && (
              <div className="flex items-start gap-2 p-3 rounded-lg bg-destructive/10 border border-destructive/20">
                <AlertTriangle className="w-4 h-4 text-destructive shrink-0 mt-0.5" />
                <p className="text-sm text-destructive">{message.result.content}</p>
              </div>
            )}
          </div>
        )}

        {/* Actions */}
        {!isUser && !message.isStreaming && (
          <div className="flex items-center gap-2 mt-2">
            <Button
              variant="ghost"
              size="sm"
              className="h-7 text-xs text-muted-foreground hover:text-foreground"
              onClick={handleCopy}
            >
              {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
              <span className="ml-1">{copied ? 'Copied' : 'Copy'}</span>
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};
