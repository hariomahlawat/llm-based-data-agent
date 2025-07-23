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
