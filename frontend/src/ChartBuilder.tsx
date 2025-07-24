import React, { useState } from 'react';
import {
  Box,
  Button,
  MenuItem,
  Select,
  TextField,
  Typography,
} from '@mui/material';
import { fetchChart, explainChart } from './api';

const CHART_TYPES = [
  'line',
  'bar',
  'hist',
  'box',
  'scatter',
  'facet_line',
  'facet_bar',
  'facet_hist',
];

export interface ChartPreset {
  name: string;
  spec: any;
}

interface Props {
  datasetId: string;
  columns: string[];
  onChart: (url: string) => void;
}

const PRESET_KEY = 'chartPresets';

export default function ChartBuilder({ datasetId, columns, onChart }: Props) {
  const [chartType, setChartType] = useState('bar');
  const [xField, setXField] = useState('');
  const [yField, setYField] = useState('');
  const [facetField, setFacetField] = useState('');
  const [presetName, setPresetName] = useState('');
  const [presets, setPresets] = useState<ChartPreset[]>(
    JSON.parse(localStorage.getItem(PRESET_KEY) || '[]')
  );
  const [explanation, setExplanation] = useState('');

  const buildSpec = () => {
    const params: any = {};
    if (xField) params.x = xField;
    if (yField) params.y = yField;
    if (chartType.startsWith('facet_') && facetField) params.facet = facetField;
    return { type: chartType, params };
  };

  const handleBuild = async () => {
    const spec = buildSpec();
    const url = await fetchChart(datasetId, spec);
    onChart(url);
    try {
      const text = await explainChart(datasetId, spec);
      setExplanation(text);
    } catch {
      setExplanation('');
    }
  };

  const handleSave = () => {
    const spec = buildSpec();
    const next = [...presets, { name: presetName || `Preset ${presets.length + 1}`, spec }];
    setPresets(next);
    localStorage.setItem(PRESET_KEY, JSON.stringify(next));
    setPresetName('');
  };

  const handlePresetSelect = (e: any) => {
    const p = presets.find((pr) => pr.name === e.target.value);
    if (p) {
      setChartType(p.spec.type);
      setXField(p.spec.params?.x || '');
      setYField(p.spec.params?.y || '');
      setFacetField(p.spec.params?.facet || '');
    }
  };

  return (
    <Box sx={{ my: 2 }}>
      <Typography variant="h6">Chart Builder</Typography>
      <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mt: 1 }}>
        <Select value={chartType} onChange={(e) => setChartType(e.target.value)} size="small">
          {CHART_TYPES.map((t) => (
            <MenuItem key={t} value={t}>
              {t}
            </MenuItem>
          ))}
        </Select>
        <Select
          value={xField}
          onChange={(e) => setXField(e.target.value)}
          displayEmpty
          size="small"
        >
          <MenuItem value="">
            <em>X</em>
          </MenuItem>
          {columns.map((c) => (
            <MenuItem key={c} value={c}>
              {c}
            </MenuItem>
          ))}
        </Select>
        <Select
          value={yField}
          onChange={(e) => setYField(e.target.value)}
          displayEmpty
          size="small"
        >
          <MenuItem value="">
            <em>Y</em>
          </MenuItem>
          {columns.map((c) => (
            <MenuItem key={c} value={c}>
              {c}
            </MenuItem>
          ))}
        </Select>
        {chartType.startsWith('facet_') && (
          <Select
            value={facetField}
            onChange={(e) => setFacetField(e.target.value)}
            displayEmpty
            size="small"
          >
            <MenuItem value="">
              <em>Facet</em>
            </MenuItem>
            {columns.map((c) => (
              <MenuItem key={c} value={c}>
                {c}
              </MenuItem>
            ))}
          </Select>
        )}
        <Button variant="contained" onClick={handleBuild} size="small">
          Build
        </Button>
      </Box>
      <Box sx={{ mt: 2, display: 'flex', gap: 1, alignItems: 'center' }}>
        <Select
          value=""
          onChange={handlePresetSelect}
          displayEmpty
          size="small"
          sx={{ minWidth: 120 }}
        >
          <MenuItem value="">
            <em>Load preset</em>
          </MenuItem>
          {presets.map((p) => (
            <MenuItem key={p.name} value={p.name}>
              {p.name}
            </MenuItem>
          ))}
        </Select>
        <TextField
          value={presetName}
          onChange={(e) => setPresetName(e.target.value)}
          placeholder="Preset name"
          size="small"
        />
        <Button onClick={handleSave} variant="outlined" size="small">
          Save Preset
        </Button>
      </Box>
      {explanation && (
        <Typography variant="body2" sx={{ mt: 1 }}>
          {explanation}
        </Typography>
      )}
    </Box>
  );
}
