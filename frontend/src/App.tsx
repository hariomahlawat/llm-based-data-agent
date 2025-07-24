import React, { useMemo, useState } from 'react';
import {
  Container,
  Typography,
  Box,
  CssBaseline,
  createTheme,
  ThemeProvider,
  IconButton,
} from '@mui/material';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import FileUpload from './FileUpload';
import DatasetSummary from './DatasetSummary';
import InsightCards from './InsightCards';
import ChartBuilder from './ChartBuilder';
import HistoryPanel from './HistoryPanel';

export default function App() {
  const [datasetId, setDatasetId] = useState<string | null>(null);
  const [columns, setColumns] = useState<string[]>([]);
  const [chartUrl, setChartUrl] = useState<string | null>(null);
  const [mode, setMode] = useState<'light' | 'dark'>(() =>
    (localStorage.getItem('theme') as 'light' | 'dark') || 'light'
  );

  const theme = useMemo(
    () =>
      createTheme({
        palette: { mode },
      }),
    [mode]
  );

  const toggleTheme = () => {
    const next = mode === 'light' ? 'dark' : 'light';
    setMode(next);
    localStorage.setItem('theme', next);
  };

  const handleUploaded = async (id: string) => {
    setDatasetId(id);
    setChartUrl(null);
  };

  React.useEffect(() => {
    if (!datasetId) return;
    import('./api').then(({ fetchSummary }) =>
      fetchSummary(datasetId)
        .then((s) => setColumns(s.columns))
        .catch(() => setColumns([]))
    );
  }, [datasetId]);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container sx={{ marginTop: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Typography variant="h4" sx={{ flexGrow: 1 }} gutterBottom>
            Data Agent React UI
          </Typography>
          <IconButton onClick={toggleTheme} color="inherit">
            {mode === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
          </IconButton>
        </Box>
        <Box sx={{ mb: 2 }}>
          <FileUpload onUploaded={handleUploaded} />
        </Box>
        {datasetId && (
          <>
            <DatasetSummary datasetId={datasetId} />
            <InsightCards datasetId={datasetId} />
            <ChartBuilder
              datasetId={datasetId}
              columns={columns}
              onChart={(url) => setChartUrl(url)}
            />
            {chartUrl && (
              <img src={chartUrl} alt="chart" style={{ maxWidth: '100%' }} />
            )}
            <HistoryPanel datasetId={datasetId} />
          </>
        )}
      </Container>
    </ThemeProvider>
  );
}
