import React, { useState } from 'react';
import { Container, Typography, Box } from '@mui/material';
import FileUpload from './FileUpload';
import { fetchChart } from './api';

export default function App() {
  const [datasetId, setDatasetId] = useState<string | null>(null);
  const [chartUrl, setChartUrl] = useState<string | null>(null);

  const handleUploaded = async (id: string) => {
    setDatasetId(id);
    try {
      const url = await fetchChart(id, { type: 'bar', params: {} });
      setChartUrl(url);
    } catch {
      setChartUrl(null);
    }
  };

  return (
    <Container sx={{ marginTop: 4 }}>
      <Typography variant="h4" gutterBottom>
        Data Agent React UI
      </Typography>
      <Box sx={{ mb: 2 }}>
        <FileUpload onUploaded={handleUploaded} />
      </Box>
      {datasetId && chartUrl && (
        <img src={chartUrl} alt="chart" style={{ maxWidth: '100%' }} />
      )}
    </Container>
  );
}
