import React from 'react';
import { BarChart3, Table2, FileText, Download, Maximize2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import type { ChatMessage, ResultData } from '@/types/statbot';

interface ResultsPanelProps {
  messages: ChatMessage[];
}

export const ResultsPanel: React.FC<ResultsPanelProps> = ({ messages }) => {
  const resultsWithData = messages.filter(m => m.role === 'agent' && m.result);

  return (
    <div className="h-full flex flex-col bg-card border-l border-border">
      {/* Header */}
      <div className="px-4 py-3 border-b border-border">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-primary" />
          <span className="font-medium text-sm">Results</span>
        </div>
      </div>

      {/* Results list */}
      <ScrollArea className="flex-1">
        <div className="p-4 space-y-4">
          {resultsWithData.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-12 h-12 rounded-2xl bg-secondary flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="w-6 h-6 text-muted-foreground" />
              </div>
              <p className="text-sm text-muted-foreground">
                Results will appear here
              </p>
            </div>
          ) : (
            resultsWithData.map((message) => (
              <ResultCard key={message.id} result={message.result!} />
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  );
};

const ResultCard: React.FC<{ result: ResultData }> = ({ result }) => {
  const icons = {
    chart: BarChart3,
    table: Table2,
    text: FileText,
    error: FileText,
  };

  const Icon = icons[result.type];

  return (
    <div className="rounded-xl border border-border overflow-hidden bg-background animate-fade-in-up">
      {/* Card header */}
      <div className="px-3 py-2 bg-secondary/50 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Icon className="w-3.5 h-3.5 text-muted-foreground" />
          <span className="text-xs font-medium capitalize">{result.type}</span>
        </div>
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="icon" className="h-6 w-6">
            <Download className="w-3 h-3" />
          </Button>
          <Button variant="ghost" size="icon" className="h-6 w-6">
            <Maximize2 className="w-3 h-3" />
          </Button>
        </div>
      </div>

      {/* Card content */}
      <div className="p-3">
        {result.type === 'chart' && result.chartUrl && (
          <img 
            src={result.chartUrl} 
            alt="Chart result"
            className="w-full h-auto rounded-lg"
          />
        )}

        {result.type === 'table' && result.tableData && (
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-border">
                  {Object.keys(result.tableData[0] || {}).map((key) => (
                    <th key={key} className="text-left py-2 px-2 font-medium text-muted-foreground">
                      {key}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {result.tableData.slice(0, 10).map((row, idx) => (
                  <tr key={idx} className="border-b border-border/50">
                    {Object.values(row).map((val, vIdx) => (
                      <td key={vIdx} className="py-1.5 px-2 font-mono">
                        {String(val)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
            {result.tableData.length > 10 && (
              <p className="text-xs text-muted-foreground text-center py-2">
                Showing 10 of {result.tableData.length} rows
              </p>
            )}
          </div>
        )}

        {result.type === 'text' && (
          <p className="text-sm text-foreground">{result.content}</p>
        )}

        {result.type === 'error' && (
          <p className="text-sm text-destructive">{result.content}</p>
        )}
      </div>
    </div>
  );
};
