export const API_BASE = '/api';

export async function uploadFile(file: File): Promise<{ dataset_id: string; rows: number }> {
  const body = new FormData();
  body.append('file', file);
  const res = await fetch(`${API_BASE}/upload`, { method: 'POST', body });
  if (!res.ok) throw new Error('Upload failed');
  return res.json();
}

export async function fetchChart(dsId: string, spec: any): Promise<string> {
  const res = await fetch(`${API_BASE}/chart/${dsId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(spec),
  });
  if (!res.ok) throw new Error('Chart failed');
  const blob = await res.blob();
  return URL.createObjectURL(blob);
}

export interface Summary {
  rows: number;
  columns: string[];
  dtypes: Record<string, string>;
  null_counts: Record<string, number>;
}

export async function fetchSummary(dsId: string): Promise<Summary> {
  const res = await fetch(`${API_BASE}/summary/${dsId}`);
  if (!res.ok) throw new Error('Summary failed');
  return res.json();
}

export async function askQuestion(
  dsId: string,
  question: string
): Promise<{ intent: string; code: string }> {
  const res = await fetch(`${API_BASE}/nl2code/${dsId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error('LLM failed');
  return res.json();
}

export interface RunResult {
  stdout: string;
  tables: string[];
  images: string[];
  texts: string[];
}

export interface Insights {
  missing_pct: Record<string, number>;
  outlier_counts: Record<string, number>;
}

export async function runCode(
  dsId: string,
  code: string
): Promise<RunResult> {
  const res = await fetch(`${API_BASE}/run_code/${dsId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code }),
  });
  if (!res.ok) throw new Error('Run failed');
  return res.json();
}

export async function fetchInsights(dsId: string): Promise<Insights> {
  const res = await fetch(`${API_BASE}/insights/${dsId}`);
  if (!res.ok) throw new Error('Insights failed');
  return res.json();
}

export async function explainChart(dsId: string, spec: any): Promise<string> {
  const res = await fetch(`${API_BASE}/explain_chart/${dsId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ spec }),
  });
  if (!res.ok) throw new Error('Explain failed');
  const data = await res.json();
  return data.summary;
}
