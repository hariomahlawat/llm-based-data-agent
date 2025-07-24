import React, { useEffect, useState } from 'react';
import { fetchInsights, Insights } from './api';
import { Box, Typography, Card, CardContent } from '@mui/material';

interface Props {
  datasetId: string;
}

export default function InsightCards({ datasetId }: Props) {
  const [insights, setInsights] = useState<Insights | null>(null);

  useEffect(() => {
    fetchInsights(datasetId)
      .then(setInsights)
      .catch(() => setInsights(null));
  }, [datasetId]);

  if (!insights) return null;

  return (
    <Box sx={{ my: 2, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
      {Object.entries(insights.missing_pct).map(([col, pct]) => (
        <Card key={col} sx={{ minWidth: 200 }}>
          <CardContent>
            <Typography variant="subtitle2">Missing % for {col}</Typography>
            <Typography variant="body2">{pct}%</Typography>
          </CardContent>
        </Card>
      ))}
      {Object.entries(insights.outlier_counts).map(([col, cnt]) => (
        <Card key={col + 'out'} sx={{ minWidth: 200 }}>
          <CardContent>
            <Typography variant="subtitle2">Outliers in {col}</Typography>
            <Typography variant="body2">{cnt}</Typography>
          </CardContent>
        </Card>
      ))}
    </Box>
  );
}
