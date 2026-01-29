import React, { useCallback, useState } from 'react';
import { Upload, FileSpreadsheet, CheckCircle2, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/lib/api';
import type { DatasetInfo, ColumnInfo } from '@/types/statbot';

interface UploadZoneProps {
  onUploadComplete: (dataset: DatasetInfo) => void;
}

export const UploadZone: React.FC<UploadZoneProps> = ({ onUploadComplete }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFile = useCallback(async (file: File) => {
    if (!file.name.endsWith('.csv')) {
      setError('Please upload a CSV file');
      return;
    }

    if (file.size > 50 * 1024 * 1024) {
      setError('File size must be under 50MB');
      return;
    }

    setIsProcessing(true);
    setError(null);

    try {
      const response = await apiClient.uploadCSV(file);

      // Convert API response to DatasetInfo format
      const columns: ColumnInfo[] = response.columns.map(name => ({
        name,
        type: response.data_types[name] === 'object' ? 'string' : 
              response.data_types[name].includes('int') || response.data_types[name].includes('float') ? 'number' :
              response.data_types[name].includes('datetime') ? 'date' : 'string',
        sampleValues: response.sample.slice(0, 5).map(row => String(row[name] || '')),
      }));

      const dataset: DatasetInfo = {
        id: response.session_id,
        fileName: file.name,
        rowCount: response.shape[0],
        columns,
        sampleData: response.sample.slice(0, 10),
        uploadedAt: new Date(),
      };

      onUploadComplete(dataset);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload CSV');
    } finally {
      setIsProcessing(false);
    }
  }, [onUploadComplete]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }, [handleFile]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  }, [handleFile]);

  return (
    <div
      className={cn(
        'relative rounded-2xl border-2 border-dashed transition-all duration-300',
        'p-12 text-center',
        isDragging ? 'border-primary bg-primary/5 scale-[1.02]' : 'border-border hover:border-muted-foreground/50',
        isProcessing && 'pointer-events-none opacity-70'
      )}
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
    >
      <input
        type="file"
        accept=".csv"
        onChange={handleFileInput}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        disabled={isProcessing}
      />

      <div className="flex flex-col items-center gap-4">
        {isProcessing ? (
          <>
            <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
              <FileSpreadsheet className="w-8 h-8 text-primary animate-pulse" />
            </div>
            <div>
              <p className="text-lg font-medium">Processing your data...</p>
              <p className="text-sm text-muted-foreground mt-1">Detecting columns and types</p>
            </div>
          </>
        ) : error ? (
          <>
            <div className="w-16 h-16 rounded-full bg-destructive/10 flex items-center justify-center">
              <AlertCircle className="w-8 h-8 text-destructive" />
            </div>
            <div>
              <p className="text-lg font-medium text-destructive">{error}</p>
              <p className="text-sm text-muted-foreground mt-1">Please try again with a valid CSV file</p>
            </div>
          </>
        ) : (
          <>
            <div className={cn(
              'w-16 h-16 rounded-full flex items-center justify-center transition-colors',
              isDragging ? 'bg-primary/20' : 'bg-secondary'
            )}>
              <Upload className={cn('w-8 h-8 transition-colors', isDragging ? 'text-primary' : 'text-muted-foreground')} />
            </div>
            <div>
              <p className="text-lg font-medium">Drop your CSV here</p>
              <p className="text-sm text-muted-foreground mt-1">or click to browse</p>
            </div>
            <div className="flex items-center gap-4 text-xs text-muted-foreground mt-2">
              <span className="flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3 text-success" />
                Max 50MB
              </span>
              <span className="flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3 text-success" />
                Auto-detect columns
              </span>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
