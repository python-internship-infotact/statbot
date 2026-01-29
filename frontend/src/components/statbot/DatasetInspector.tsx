import React from 'react';
import { FileSpreadsheet, Rows3, Columns3, Clock } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { DatasetInfo } from '@/types/statbot';
import { ScrollArea } from '@/components/ui/scroll-area';

interface DatasetInspectorProps {
  dataset: DatasetInfo;
}

const typeColors: Record<string, string> = {
  string: 'text-emerald-400 bg-emerald-400/10',
  number: 'text-blue-400 bg-blue-400/10',
  date: 'text-purple-400 bg-purple-400/10',
  boolean: 'text-amber-400 bg-amber-400/10',
};

export const DatasetInspector: React.FC<DatasetInspectorProps> = ({ dataset }) => {
  return (
    <div className="h-full flex flex-col bg-card border-r border-border">
      {/* Header */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
            <FileSpreadsheet className="w-4 h-4 text-primary" />
          </div>
          <div className="min-w-0 flex-1">
            <p className="font-medium text-sm truncate">{dataset.fileName}</p>
            <p className="text-xs text-muted-foreground">Dataset</p>
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-2">
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-secondary/50">
            <Rows3 className="w-3.5 h-3.5 text-muted-foreground" />
            <span className="text-xs">
              <span className="font-semibold text-foreground">{dataset.rowCount.toLocaleString()}</span>
              <span className="text-muted-foreground ml-1">rows</span>
            </span>
          </div>
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-secondary/50">
            <Columns3 className="w-3.5 h-3.5 text-muted-foreground" />
            <span className="text-xs">
              <span className="font-semibold text-foreground">{dataset.columns.length}</span>
              <span className="text-muted-foreground ml-1">cols</span>
            </span>
          </div>
        </div>
      </div>

      {/* Columns */}
      <div className="flex-1 overflow-hidden flex flex-col">
        <div className="px-4 py-3 border-b border-border">
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Columns</p>
        </div>
        
        <ScrollArea className="flex-1">
          <div className="p-2 space-y-1">
            {dataset.columns.map((column) => (
              <div
                key={column.name}
                className="px-3 py-2 rounded-lg hover:bg-secondary/50 transition-colors"
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="text-sm font-medium truncate">{column.name}</span>
                  <span className={cn('text-xs px-2 py-0.5 rounded-full font-mono', typeColors[column.type])}>
                    {column.type}
                  </span>
                </div>
                <p className="text-xs text-muted-foreground mt-1 truncate font-mono">
                  {column.sampleValues.slice(0, 3).join(', ')}
                </p>
              </div>
            ))}
          </div>
        </ScrollArea>
      </div>

      {/* Sample Preview */}
      <div className="border-t border-border">
        <div className="px-4 py-3 flex items-center justify-between">
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Preview</p>
          <span className="text-xs text-muted-foreground">First 10 rows</span>
        </div>
        <ScrollArea className="h-32">
          <div className="px-2 pb-2">
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-border">
                    {dataset.columns.slice(0, 4).map((col) => (
                      <th key={col.name} className="text-left py-1.5 px-2 font-medium text-muted-foreground">
                        {col.name}
                      </th>
                    ))}
                    {dataset.columns.length > 4 && (
                      <th className="text-left py-1.5 px-2 font-medium text-muted-foreground">...</th>
                    )}
                  </tr>
                </thead>
                <tbody>
                  {dataset.sampleData.slice(0, 5).map((row, idx) => (
                    <tr key={idx} className="border-b border-border/50">
                      {dataset.columns.slice(0, 4).map((col) => (
                        <td key={col.name} className="py-1.5 px-2 truncate max-w-[100px] font-mono text-muted-foreground">
                          {String(row[col.name] ?? '')}
                        </td>
                      ))}
                      {dataset.columns.length > 4 && (
                        <td className="py-1.5 px-2 text-muted-foreground">...</td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </ScrollArea>
      </div>
    </div>
  );
};
