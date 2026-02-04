import React from 'react';
import type { DatasetInfo } from '@/types/statbot';

interface SimpleLandingProps {
  onUploadComplete: (dataset: DatasetInfo) => void;
}

export const SimpleLanding: React.FC<SimpleLandingProps> = ({ onUploadComplete }) => {
  return (
    <div style={{ padding: '40px', textAlign: 'center', minHeight: '100vh', backgroundColor: '#1a1a1a', color: 'white' }}>
      <h1 style={{ fontSize: '48px', marginBottom: '20px' }}>
        StatBot Pro
      </h1>
      <p style={{ fontSize: '18px', marginBottom: '40px', color: '#ccc' }}>
        AI-powered CSV data analysis tool
      </p>
      
      <div style={{
        border: '2px dashed #666',
        borderRadius: '12px',
        padding: '60px 40px',
        backgroundColor: '#2a2a2a',
        maxWidth: '600px',
        margin: '0 auto'
      }}>
        <div style={{ fontSize: '48px', marginBottom: '20px' }}>📊</div>
        <h2 style={{ fontSize: '24px', marginBottom: '10px' }}>Upload your CSV file</h2>
        <p style={{ color: '#ccc', marginBottom: '20px' }}>
          Drag and drop your CSV file here or click to browse
        </p>
        <input 
          type="file" 
          accept=".csv"
          style={{
            padding: '10px 20px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer'
          }}
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) {
              // Mock dataset for testing
              const mockDataset: DatasetInfo = {
                id: 'test-123',
                fileName: file.name,
                rowCount: 100,
                columns: [
                  { name: 'name', type: 'string', sampleValues: ['John', 'Jane'] },
                  { name: 'age', type: 'number', sampleValues: ['25', '30'] }
                ],
                sampleData: [
                  { name: 'John', age: 25 },
                  { name: 'Jane', age: 30 }
                ],
                uploadedAt: new Date()
              };
              onUploadComplete(mockDataset);
            }
          }}
        />
      </div>
      
      <div style={{ marginTop: '60px' }}>
        <h3 style={{ fontSize: '20px', marginBottom: '20px' }}>Features</h3>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '40px', flexWrap: 'wrap' }}>
          <div style={{ textAlign: 'center', maxWidth: '200px' }}>
            <div style={{ fontSize: '24px', marginBottom: '10px' }}>✨</div>
            <h4>Natural Language</h4>
            <p style={{ color: '#ccc', fontSize: '14px' }}>Ask questions in plain English</p>
          </div>
          <div style={{ textAlign: 'center', maxWidth: '200px' }}>
            <div style={{ fontSize: '24px', marginBottom: '10px' }}>⚡</div>
            <h4>Instant Analysis</h4>
            <p style={{ color: '#ccc', fontSize: '14px' }}>Get insights in seconds</p>
          </div>
          <div style={{ textAlign: 'center', maxWidth: '200px' }}>
            <div style={{ fontSize: '24px', marginBottom: '10px' }}>🛡️</div>
            <h4>Secure</h4>
            <p style={{ color: '#ccc', fontSize: '14px' }}>Your data stays private</p>
          </div>
        </div>
      </div>
    </div>
  );
};
