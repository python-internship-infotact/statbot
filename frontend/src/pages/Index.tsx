import React, { useState } from 'react';
import { LandingScreen } from '@/components/statbot/LandingScreen';
import { AnalysisWorkspace } from '@/components/statbot/AnalysisWorkspace';
import type { DatasetInfo } from '@/types/statbot';

const Index = () => {
  const [dataset, setDataset] = useState<DatasetInfo | null>(null);

  const handleReset = () => {
    setDataset(null);
  };

  if (dataset) {
    return <AnalysisWorkspace dataset={dataset} onReset={handleReset} />;
  }

  return <LandingScreen onUploadComplete={setDataset} />;
};

export default Index;
