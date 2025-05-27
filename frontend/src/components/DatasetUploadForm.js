import React, { useState } from 'react';
import api from '../services/api';

const DatasetUploadForm = () => {
  const [dataset, setDataset] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file && file.type === 'application/zip') {
      setDataset(file);
      setMessage('');
    } else {
      setMessage('Please upload a .zip file');
      setDataset(null);
    }
  };

  const handleFinetune = async (e) => {
    e.preventDefault();
    if (!dataset) {
      setMessage('Please select a dataset first');
      return;
    }

    setIsLoading(true);
    const formData = new FormData();
    formData.append('dataset', dataset);

    try {
      await api.post('/finetune', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setMessage('Dataset uploaded successfully! Finetuning process started.');
    } catch (error) {
      setMessage('Error uploading dataset: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="upload-form-container">
      <form onSubmit={handleFinetune}>
        <div className="form-group">
          <label htmlFor="dataset">Upload Dataset (.zip)</label>
          <input
            type="file"
            id="dataset"
            accept=".zip"
            onChange={handleFileChange}
            className="form-control"
          />
        </div>
        {message && <div className={message.includes('Error') ? 'error-message' : 'success-message'}>{message}</div>}
        <button 
          type="submit" 
          className="submit-button"
          disabled={isLoading || !dataset}
        >
          {isLoading ? 'Processing...' : 'Finetune'}
        </button>
      </form>
    </div>
  );
};

export default DatasetUploadForm;
