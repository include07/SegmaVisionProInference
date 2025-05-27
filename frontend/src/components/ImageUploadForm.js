// src/components/ImageUploadForm.js
import React, { useState, useEffect } from 'react'; // <-- Add useEffect here
import authService from '../services/authService'; // Assuming uploadImage is here
import { uploadImage } from '../services/authService'; // <-- Import specific function

// Helper function to construct full result URL (pointing to backend)
const getResultImageUrl = (relativePath) => {
    if (!relativePath) return null;
    const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000/api/';
    const backendBaseUrl = apiUrl.endsWith('/api/') ? apiUrl.slice(0, -5) : apiUrl.replace('/api', '');
    const cleanRelativePath = relativePath.startsWith('/') ? relativePath.substring(1) : relativePath;
    // Use URL constructor for safer joining, handling potential double slashes etc.
    try {
      // Ensure backendBaseUrl doesn't end with / if results endpoint doesn't start with /
       const baseUrl = backendBaseUrl.endsWith('/') ? backendBaseUrl : backendBaseUrl + '/';
       return new URL(`api/results/${cleanRelativePath}`, baseUrl).href;
    } catch (e) {
        console.error("Error creating result URL:", e);
        return null; // Handle invalid URL construction
    }
};


function ImageUploadForm() {
  const [file, setFile] = useState(null);
  const [keywords, setKeywords] = useState('');
  const [colorMap, setColorMap] = useState('{}');
  const [message, setMessage] = useState('');
  const [isError, setIsError] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [resultImageUrl, setResultImageUrl] = useState(null); // Will hold Object URL

  // --- Add useEffect for Object URL cleanup ---
  useEffect(() => {
      // This function runs when the component unmounts or before the effect runs again
      return () => {
          if (resultImageUrl && resultImageUrl.startsWith('blob:')) {
              URL.revokeObjectURL(resultImageUrl);
              console.log('Revoked Object URL:', resultImageUrl);
          }
      };
  }, [resultImageUrl]); // Dependency array: run cleanup when resultImageUrl changes

  const handleFileChange = (event) => {
      // ... (keep existing file change logic, including clearing previous result) ...
       if (event.target.files && event.target.files[0]) {
          setFile(event.target.files[0]);
          // Revoke previous Object URL if one exists before setting new file
          if (resultImageUrl && resultImageUrl.startsWith('blob:')) {
              URL.revokeObjectURL(resultImageUrl);
          }
          setResultImageUrl(null);
          setMessage('');
          setIsError(false);
      } else {
          setFile(null);
      }
  };

  const handleKeywordsChange = (event) => { setKeywords(event.target.value); };
  const handleColorMapChange = (event) => { setColorMap(event.target.value); };

  const handleSubmit = async (event) => {
      event.preventDefault();
      setMessage(''); setIsError(false);
      // Revoke previous Object URL before new attempt
      if (resultImageUrl && resultImageUrl.startsWith('blob:')) {
          URL.revokeObjectURL(resultImageUrl);
      }
      setResultImageUrl(null);

      // --- Input Validation ---
      // (Keep validation logic for file, keywords, colorMap as before)
      if (!file) { setMessage('Please select an image file.'); setIsError(true); return; }
      if (!keywords.trim()) { setMessage('Please enter keywords/captions.'); setIsError(true); return; }
      try {
          const parsed = JSON.parse(colorMap);
          if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) { throw new Error("Input must be a JSON object."); }
      } catch (e) { setMessage(`Invalid Color Map JSON: ${e.message}.`); setIsError(true); return; }
      // --- End Validation ---

      setIsLoading(true);
      setMessage('Uploading and processing...');

      try {
          // Call the upload service function - it now returns a Blob on success
          const responseBlob = await authService.uploadImage(file, keywords, colorMap); // Call as a method

          // --- Handle Blob Response ---
          if (responseBlob instanceof Blob && responseBlob.size > 0) {
              // Create a temporary URL for the blob
              const objectUrl = URL.createObjectURL(responseBlob);
              setResultImageUrl(objectUrl); // Set state for the <img> tag
              setMessage('Processing successful! Result displayed below.');
              setIsError(false);
              console.log("Created Object URL:", objectUrl);
          } else {
               // This case might occur if backend sent 200 OK but empty/invalid blob
               console.error("Received unexpected response type or empty blob:", responseBlob);
               setMessage('Processing finished, but received invalid result data.');
               setIsError(true);
          }
          // Optionally clear form fields
          // event.target.reset();
          // setFile(null);
          // --- End Blob Handling ---

      } catch (err) {
          // Handle errors (e.g., 4xx, 5xx responses)
          let errorMsg = 'An error occurred during upload/processing.';
          // Attempt to parse error response if it's JSON (common for backend errors)
          if (err.response && err.response.data instanceof Blob && err.response.headers['content-type']?.includes('application/json')) {
              try {
                  // Need to read the blob as text, then parse as JSON
                  const errorJson = JSON.parse(await err.response.data.text());
                  errorMsg = errorJson.message || errorMsg;
              } catch (parseError) {
                  console.error("Could not parse error response blob:", parseError);
              }
          } else if (err.response && err.response.data) { // If error data is already JSON object
               errorMsg = err.response.data.message || errorMsg;
          } else if (err.message) {
              errorMsg = err.message;
          }
          setMessage(`Error: ${errorMsg}`);
          setIsError(true);
          setResultImageUrl(null); // Clear image on error
      } finally {
          setIsLoading(false);
      }
  };

  return (
      <div className="form-container" style={{ maxWidth: '600px', margin: 'auto' }}>
          <h2>Upload Image & Process</h2>
          <form onSubmit={handleSubmit}>
              {/* File Input */}
              <div className="form-group">
                  <label htmlFor="image-upload">Select Image:</label>
                  <input type="file" id="image-upload" accept="image/png, image/jpeg, image/gif" onChange={handleFileChange} disabled={isLoading} />
              </div>
              {/* Keywords Input */}
              <div className="form-group">
                  <label htmlFor="keywords-input">Keywords/Captions:</label>
                  <input type="text" id="keywords-input" value={keywords} onChange={handleKeywordsChange} placeholder="e.g., ball, player, table" required disabled={isLoading} />
              </div>
              {/* Color Map Input */}
              <div className="form-group">
                  <label htmlFor="color-map-input">Color Map (JSON string):</label>
                  <textarea id="color-map-input" value={colorMap} onChange={handleColorMapChange} placeholder='e.g., {"player": "green", "ball": "red"}' required disabled={isLoading} rows={4} style={{ fontFamily: 'monospace', fontSize: '0.9em' }} />
                  <small style={{ color: '#666', display: 'block', marginTop: '5px' }}>Enter as a valid JSON object.</small>
              </div>
              {/* Submit Button */}
              <button type="submit" disabled={isLoading || !file}>
                  {isLoading ? 'Processing...' : 'Upload and Process'}
              </button>
          </form>

          {/* Display Status Message */}
          {message && (<p className={`message ${isError ? 'error' : 'success'}`}>{message}</p>)}

          {/* Display Result Image using Object URL */}
          {isLoading && <p style={{ textAlign: 'center', marginTop: '15px' }}>Processing, please wait...</p>}
          {resultImageUrl && !isError && (
              <div className="result-container">
                  <h3>Processed Image Result:</h3>
                  {/* src is now the temporary Object URL */}
                  <img src={resultImageUrl} alt="Processed inference result" style={{maxWidth: '100%', height: 'auto', border: '1px solid #ccc', display: 'block', margin: 'auto'}}/>
                  {/* Link to Object URL isn't very useful */}
                  {/* <p><a href={resultImageUrl} target="_blank" rel="noopener noreferrer">View Full Size</a></p> */}
              </div>
          )}
      </div>
  );
}

export default ImageUploadForm;