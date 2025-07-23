import React, { useEffect, useState } from 'react';
import { askQuestion, runCode, RunResult } from './api';
import { Box, Button, TextField, Typography } from '@mui/material';

interface Item {
  question: string;
  timestamp: number;
}

interface Props {
  datasetId: string;
}

const HISTORY_KEY = 'promptHistory';

export default function HistoryPanel({ datasetId }: Props) {
  const [question, setQuestion] = useState('');
  const [history, setHistory] = useState<Item[]>(
    JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]')
  );
  const [output, setOutput] = useState<RunResult | null>(null);

  useEffect(() => {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
  }, [history]);

  const runPrompt = async () => {
    if (!question.trim()) return;
    const { code } = await askQuestion(datasetId, question);
    const result = await runCode(datasetId, code);
    setOutput(result);
    setHistory([{ question, timestamp: Date.now() }, ...history]);
    setQuestion('');
  };

  return (
    <Box sx={{ my: 2 }}>
      <Typography variant="h6">Prompt Runner</Typography>
      <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
        <TextField
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question"
          size="small"
          fullWidth
        />
        <Button onClick={runPrompt} variant="contained" size="small">
          Run
        </Button>
      </Box>
      {output && (
        <Box sx={{ mt: 1 }}>
          <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
            {output.stdout}
          </Typography>
          {output.images.map((img, idx) => (
            <img
              key={idx}
              src={`data:image/png;base64,${img}`}
              alt="img"
              style={{ maxWidth: '100%', marginTop: 4 }}
            />
          ))}
        </Box>
      )}
      <Box sx={{ mt: 2 }}>
        <Typography variant="subtitle1">History</Typography>
        {history.map((h) => (
          <Typography key={h.timestamp} variant="body2">
            {new Date(h.timestamp).toLocaleString()}: {h.question}
          </Typography>
        ))}
      </Box>
    </Box>
  );
}
