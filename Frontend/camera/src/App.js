import React, { useEffect, useState } from 'react';
import './App.css';

const App = () => {
  const [video, setVideo] = useState('');
  const [capturedImages, setCapturedImages] = useState([]);
  const [showCapturedImages, setShowCapturedImages] = useState(false);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:5000/video_feed');

    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setVideo(data.image_1);
    };

    ws.onclose = () => {
      console.log('WebSocket closed');
    };

    return () => {
      ws.close();
    };
  }, []);

  const handleCapture = () => {
    setCapturedImages([...capturedImages, video]);
  };

  const toggleShowCapturedImages = () => {
    setShowCapturedImages(!showCapturedImages);
  };

  return (
    <div className="dashboard">
      <div className="video-stream">
        <h1>Video Stream</h1>
        <div className="video-container">
          {video && <img className="video" src={`data:image/jpeg;base64,${video}`} alt="video stream" />}
        </div>
      </div>
      <div className="captured-images">
        <h1>Captured Images</h1>
        <button onClick={handleCapture}>Capture</button>
        <button onClick={toggleShowCapturedImages}>
          {showCapturedImages ? 'Hide Captured Images' : 'Show Captured Images'}
        </button>
        {showCapturedImages && (
          <div className="captured-images-grid">
            {capturedImages.map((image, index) => (
              <div key={index} className="captured-image">
                <h2>Captured Image {index + 1}</h2>
                <img src={`data:image/jpeg;base64,${image}`} alt={`captured image ${index + 1}`} />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
