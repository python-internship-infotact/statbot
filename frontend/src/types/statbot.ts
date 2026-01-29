export interface DatasetInfo {
  id: string;
  fileName: string;
  rowCount: number;
  columns: ColumnInfo[];
  sampleData: Record<string, unknown>[];
  uploadedAt: Date;
}

export interface ColumnInfo {
  name: string;
  type: 'string' | 'number' | 'date' | 'boolean';
  sampleValues: string[];
}

export type MessageRole = 'user' | 'agent';

export type AgentStepType = 'loading' | 'analyzing' | 'coding' | 'executing' | 'plotting' | 'complete' | 'error';

export interface AgentStep {
  id: string;
  type: AgentStepType;
  message: string;
  timestamp: Date;
  code?: string;
}

export interface ResultData {
  type: 'text' | 'table' | 'chart' | 'error';
  content: string;
  tableData?: Record<string, unknown>[];
  chartUrl?: string;
}

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  steps?: AgentStep[];
  result?: ResultData;
  isStreaming?: boolean;
}

export interface AnalysisState {
  dataset: DatasetInfo | null;
  messages: ChatMessage[];
  isAnalyzing: boolean;
  showReasoning: boolean;
}
