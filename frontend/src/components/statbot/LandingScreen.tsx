import React from 'react';
import { BarChart3, Sparkles, Shield, Zap } from 'lucide-react';
import { UploadZone } from './UploadZone';
import { ExampleQuestions } from './ExampleQuestions';
import type { DatasetInfo } from '@/types/statbot';

interface LandingScreenProps {
  onUploadComplete: (dataset: DatasetInfo) => void;
}

const features = [
  {
    icon: Sparkles,
    title: 'Natural Language',
    description: 'Ask questions in plain English',
  },
  {
    icon: Zap,
    title: 'Instant Analysis',
    description: 'Get insights in seconds',
  },
  {
    icon: Shield,
    title: 'Enterprise Ready',
    description: 'Secure & transparent',
  },
];

export const LandingScreen: React.FC<LandingScreenProps> = ({ onUploadComplete }) => {
  return (
    <div className="min-h-screen flex flex-col relative overflow-hidden">
      {/* Background glow */}
      <div 
        className="absolute inset-0 pointer-events-none"
        style={{ background: 'var(--gradient-glow)' }}
      />

      {/* Header */}
      <header className="relative z-10 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-xl bg-primary flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="font-semibold text-lg">StatBot Pro</span>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="relative z-10 flex-1 flex flex-col items-center justify-center px-6 py-12">
        <div className="w-full max-w-2xl space-y-10">
          {/* Hero */}
          <div className="text-center space-y-4">
            <h1 className="text-4xl sm:text-5xl font-bold tracking-tight">
              Ask questions to your{' '}
              <span className="gradient-text">CSV data</span>
            </h1>
            <p className="text-lg text-muted-foreground max-w-lg mx-auto">
              Upload your data and get instant insights with AI-powered analysis. 
              No code required.
            </p>
          </div>

          {/* Upload Zone */}
          <UploadZone onUploadComplete={onUploadComplete} />

          {/* Example Questions */}
          <ExampleQuestions />

          {/* Features */}
          <div className="grid grid-cols-3 gap-4 pt-8 border-t border-border">
            {features.map((feature) => (
              <div key={feature.title} className="text-center">
                <div className="w-10 h-10 rounded-xl bg-secondary flex items-center justify-center mx-auto mb-3">
                  <feature.icon className="w-5 h-5 text-primary" />
                </div>
                <h3 className="font-medium text-sm mb-1">{feature.title}</h3>
                <p className="text-xs text-muted-foreground">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 px-6 py-4 border-t border-border">
        <div className="max-w-6xl mx-auto flex items-center justify-center text-xs text-muted-foreground">
          <span>Your data is processed locally and never stored</span>
        </div>
      </footer>
    </div>
  );
};
