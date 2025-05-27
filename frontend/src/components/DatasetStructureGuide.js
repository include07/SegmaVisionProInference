import React from 'react';

const DatasetStructureGuide = () => {
  return (
    <div className="dataset-guide">
      <h2>Dataset Structure Requirements</h2>
      <p>Your dataset ZIP file must follow the COCO format structure as shown below:</p>
      
      <div className="folder-structure">
        <pre>
{`dataset_folder/
├── annotations/
│   ├── train.json
│   └── val.json
├── train/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
└── val/
    ├── image1.jpg
    ├── image2.jpg
    └── ...`}
        </pre>
      </div>

      <div className="annotation-format">
        <h3>Annotation Format (train.json/val.json)</h3>
        <p>The JSON files must follow the COCO format:</p>
        <pre>
{`{
  "images": [
    {
      "id": 1,
      "file_name": "image1.jpg",
      "height": 480,
      "width": 640
    }
  ],
  "annotations": [
    {
      "id": 1,
      "image_id": 1,
      "category_id": 1,
      "bbox": [x, y, width, height],
      "area": float,
      "iscrowd": 0
    }
  ],
  "categories": [
    {
      "id": 1,
      "name": "class_name"
    }
  ]
}`}
        </pre>
      </div>

      <div className="requirements-list">
        <h3>Important Requirements:</h3>
        <ul>
          <li>Images must be in JPG/JPEG format</li>
          <li>Bounding box coordinates must be in [x, y, width, height] format</li>
          <li>The x,y coordinates represent the top-left corner of the bounding box</li>
          <li>All IDs must be integers and unique within their category</li>
          <li>Image filenames in JSON must exactly match the actual image files</li>
        </ul>
      </div>
    </div>
  );
};

export default DatasetStructureGuide;
