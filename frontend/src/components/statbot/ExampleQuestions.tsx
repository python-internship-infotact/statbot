import React from 'react';
import { TrendingUp, BarChart3, PieChart, ArrowRightLeft } from 'lucide-react';

const examples = [
  {
    icon: TrendingUp,
    question: 'Show sales trend by region',
    description: 'Time-series analysis',
  },
  {
    icon: BarChart3,
    question: 'Compare revenue across categories',
    description: 'Grouped comparison',
  },
  {
    icon: ArrowRightLeft,
    question: 'Find correlation with marketing spend',
    description: 'Statistical analysis',
  },
  {
    icon: PieChart,
    question: 'Break down by customer segment',
    description: 'Distribution analysis',
  },
];

interface ExampleQuestionsProps {
  onSelectQuestion?: (question: string) => void;
}

export const ExampleQuestions: React.FC<ExampleQuestionsProps> = ({ onSelectQuestion }) => {
  return (
    <div className="space-y-3">
      <p className="text-sm text-muted-foreground font-medium">Example questions:</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {examples.map((example) => (
          <button
            key={example.question}
            onClick={() => onSelectQuestion?.(example.question)}
            className="flex items-start gap-3 p-3 rounded-lg bg-secondary/50 hover:bg-secondary transition-colors text-left group"
          >
            <div className="w-8 h-8 rounded-md bg-primary/10 flex items-center justify-center shrink-0 group-hover:bg-primary/20 transition-colors">
              <example.icon className="w-4 h-4 text-primary" />
            </div>
            <div>
              <p className="text-sm font-medium text-foreground">{example.question}</p>
              <p className="text-xs text-muted-foreground mt-0.5">{example.description}</p>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};
