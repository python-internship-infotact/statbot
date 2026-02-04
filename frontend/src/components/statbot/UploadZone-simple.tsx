import React, { useState } from 'react';
import { apiClient } from '@/lib/api';
import type { DatasetInfo, ColumnInfo } from '@/types/statbot';

interface UploadZoneProps {
  onUploadComplete: (dataset: DatasetInfo) => void;
}

export const UploadZone: React.FC<UploadZoneProps> = ({ onUploadComplete }) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFile = async (file: File) => {
    if (!file.name.endsWith('.csv')) {
      setError('Please upload a CSV file');
      return;
    }

    setIsProcessing(true);
    setError(null);

    try {
      const response = await apiClient.uploadCSV(file);

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
  };

  return (
    <div className="relative rounded-2xl border-2 border-dashed border-border p-12 text-center hover:border-muted-foreground/50 transition-all duration-300">
      <input
        type="file"
        accept=".csv"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleFile(file);
        }}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        disabled={isProcessing}
      />

      <div className="flex flex-col items-center gap-4">
        {isProcessing ? (
          <>
            <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
              <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
            </div>
            <div>
              <p className="text-lg font-medium">Processing your data...</p>
              <p className="text-sm text-muted-foreground mt-1">Detecting columns and types</p>
            </div>
          </>
        ) : error ? (
          <>
            <div className="w-16 h-16 rounded-full bg-destructive/10 flex items-center justify-center">
              <span className="text-2xl">⚠️</span>
            </div>
            <div>
              <p className="text-lg font-medium text-destructive">{error}</p>
              <p className="text-sm text-muted-foreground mt-1">Please try again with a valid CSV file</p>
            </div>
          </>
        ) : (
          <>
            <div className="w-16 h-16 rounded-full bg-secondary flex items-center justify-center">
              <span className="text-2xl">📁</span>
            </div>
            <div>
              <p className="text-lg font-medium">Drop your CSV here</p>
              <p className="text-sm text-muted-foreground mt-1">or click to browse</p>
            </div>
            <div className="flex items-center gap-4 text-xs text-muted-foreground mt-2">
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 bg-success rounded-full"></span>
                Max 50MB
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 bg-success rounded-full"></span>
                Auto-detect columns
              </span>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
