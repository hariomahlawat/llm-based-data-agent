import React, { useState } from 'react';
import { Button } from '@mui/material';
import { uploadFile } from './api';

interface Props {
  onUploaded: (id: string) => void;
}

export default function FileUpload({ onUploaded }: Props) {
  const [loading, setLoading] = useState(false);

  const handleChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true);
    try {
      const result = await uploadFile(file);
      onUploaded(result.dataset_id);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button variant="contained" component="label" disabled={loading}>
      {loading ? 'Uploading...' : 'Upload CSV'}
      <input type="file" hidden onChange={handleChange} />
    </Button>
  );
}
