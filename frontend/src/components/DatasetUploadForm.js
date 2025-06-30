import React, { useState, useEffect } from 'react';
import api from '../services/api';

const DatasetUploadForm = () => {
  const [dataset, setDataset] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [finetuneStatus, setFinetuneStatus] = useState(null); // 'processing', 'completed', 'failed'
  const [datasetId, setDatasetId] = useState(null);
  const [progress, setProgress] = useState(0);
  const [availableModel, setAvailableModel] = useState(null);

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
      const response = await api.post('/finetune', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      setMessage('Dataset uploaded successfully! Finetuning process started.');
      setDatasetId(response.data.dataset_id);
      setFinetuneStatus('processing');
      setProgress(0);
      
      // Start polling for status updates
      startStatusPolling(response.data.dataset_id);
      
    } catch (error) {
      setMessage('Error uploading dataset: ' + (error.response?.data?.error || error.message));
      setFinetuneStatus('failed');
    } finally {
      setIsLoading(false);
    }
  };

  // Function to poll fine-tuning status
  const startStatusPolling = (datasetId) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await api.get(`/finetune/status/${datasetId}`);
        const { status, progress, message: statusMessage } = response.data;
        
        setProgress(progress);
        setMessage(statusMessage || 'Processing...');
        
        if (status === 'completed') {
          setFinetuneStatus('completed');
          setAvailableModel(response.data.model_path || 'model_epoch_000.pth');
          setMessage('Fine-tuning completed successfully! You can now download the model or use it for inference.');
          clearInterval(pollInterval);
        } else if (status === 'failed') {
          setFinetuneStatus('failed');
          setMessage('Fine-tuning failed. Please check the logs and try again.');
          clearInterval(pollInterval);
        }
      } catch (error) {
        console.error('Error polling status:', error);
        // Continue polling on error, don't stop
      }
    }, 5000); // Poll every 5 seconds

    // Store interval ID to clear it if component unmounts
    return pollInterval;
  };

  // Function to download the trained model
  const handleDownloadModel = async () => {
    try {
      const response = await api.get(`/finetune/download/${datasetId}`, {
        responseType: 'blob', // Important for file downloads
      });
      
      // Create blob URL and trigger download
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = availableModel || 'trained_model.pth';
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      setMessage('Model download started!');
    } catch (error) {
      setMessage('Error downloading model: ' + (error.response?.data?.error || error.message));
    }
  };

  // Function to use the model for inference
  const handleUseForInference = () => {
    // Store the trained model info in localStorage for use in inference
    localStorage.setItem('trainedModel', JSON.stringify({
      datasetId: datasetId,
      modelPath: availableModel,
      isCustomModel: true
    }));
    
    setMessage('Model selected for inference! You can now go to the Dashboard to use it.');
    
    // Optionally redirect to dashboard/inference page
    // window.location.href = '/dashboard';
  };

  // Cleanup effect
  useEffect(() => {
    return () => {
      // Clear any polling intervals when component unmounts
      // This would require storing the interval ID in state if needed
    };
  }, []);

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
            disabled={finetuneStatus === 'processing'}
          />
        </div>
        
        {message && (
          <div className={message.includes('Error') || message.includes('failed') ? 'error-message' : 'success-message'}>
            {message}
          </div>
        )}
        
        {/* Progress indicator for fine-tuning */}
        {finetuneStatus === 'processing' && (
          <div className="progress-container">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <div className="progress-text">{progress}% Complete</div>
          </div>
        )}
        
        {/* Upload/Start button */}
        <button 
          type="submit" 
          className="submit-button"
          disabled={isLoading || !dataset || finetuneStatus === 'processing'}
        >
          {isLoading ? 'Processing...' : 
           finetuneStatus === 'processing' ? 'Training in Progress...' : 
           'Start Finetuning'}
        </button>
      </form>
      
      {/* Action buttons after fine-tuning completion */}
      {finetuneStatus === 'completed' && (
        <div className="post-training-actions">
          <h3>Fine-tuning Complete!</h3>
          <p>Your model has been successfully trained. Choose an action:</p>
          
          <div className="action-buttons">
            <button 
              className="download-button"
              onClick={handleDownloadModel}
            >
              📥 Download Model
            </button>
            
            <button 
              className="inference-button"
              onClick={handleUseForInference}
            >
              🚀 Use for Inference
            </button>
          </div>
          
          {availableModel && (
            <div className="model-info">
              <small>Model: {availableModel}</small>
            </div>
          )}
        </div>
      )}
      
      {/* Reset button for failed training */}
      {finetuneStatus === 'failed' && (
        <div className="failed-actions">
          <button 
            className="reset-button"
            onClick={() => {
              setFinetuneStatus(null);
              setDatasetId(null);
              setProgress(0);
              setMessage('');
              setDataset(null);
            }}
          >
            Try Again
          </button>
        </div>
      )}
    </div>
  );
};

export default DatasetUploadForm;
