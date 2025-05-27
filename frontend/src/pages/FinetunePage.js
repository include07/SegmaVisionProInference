import React from 'react';
import DatasetUploadForm from '../components/DatasetUploadForm';
import DatasetStructureGuide from '../components/DatasetStructureGuide';

const FinetunePage = () => {
  return (
    <div className="finetune-page">
      <h1>Finetune Model</h1>
      <p>Upload your dataset in .zip format to finetune the model</p>
      <DatasetStructureGuide />
      <DatasetUploadForm />
    </div>
  );
};

export default FinetunePage;
