import React, { useEffect, useState } from 'react';
import { fetchSummary, Summary } from './api';
import {
  Box,
  Typography,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
} from '@mui/material';

interface Props {
  datasetId: string;
}

export default function DatasetSummary({ datasetId }: Props) {
  const [summary, setSummary] = useState<Summary | null>(null);

  useEffect(() => {
    fetchSummary(datasetId)
      .then(setSummary)
      .catch(() => setSummary(null));
  }, [datasetId]);

  if (!summary) return null;

  return (
    <Box sx={{ my: 2 }}>
      <Typography variant="h6">Dataset Summary</Typography>
      <Typography variant="body2">Rows: {summary.rows}</Typography>
      <Table size="small" sx={{ mt: 1 }}>
        <TableHead>
          <TableRow>
            <TableCell>Column</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>Nulls</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {summary.columns.map((col) => (
            <TableRow key={col}>
              <TableCell>{col}</TableCell>
              <TableCell>{summary.dtypes[col]}</TableCell>
              <TableCell>{summary.null_counts[col]}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Box>
  );
}
