import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './App.css';

const App = () => {
  const [video, setVideo] = useState('');
  const [video1, setVideo1] = useState('');
  const [capturedImagesCam1, setCapturedImagesCam1] = useState([]);
  const [capturedImagesCam2, setCapturedImagesCam2] = useState([]);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:5000/video_feed');

    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setVideo(data.image_1);
      setVideo1(data.image_2);
    };

    ws.onclose = () => {
      console.log('WebSocket closed');
    };
    

    return () => {
      ws.close();
    };
  }, []);

  const handleCapture = () => {
    axios.post('http://localhost:5000/capture_frame')
      .then(response => {
        console.log(response.data['cam1'])
      
        setCapturedImagesCam1(response.data['cam1'])
        setCapturedImagesCam2(response.data['cam2'])
      })
      .catch(error => console.error('Error capturing frame:', error));
  };

  return (
    <div className="dashboard">
      <button onClick={handleCapture} className='btn'>Capture</button>
      <div className="video-stream">
        <h1>Video Stream</h1>
        <div className="video-container">
          {video && <img className="video1" src={`data:image/jpeg;base64,${video}`} alt="video stream" />}
          {video1 && <img className="video2" src={`data:image/jpeg;base64,${video1}`} alt="video stream 1" />}
        </div>
      </div>
      <div className='parent'>
      <div className="captured-images">
        <h1>Camera 1</h1>
        <div className="captured-images-grid">
          {capturedImagesCam1.map((image, index) => (
            <div key={index} className="captured-image">
           
              <img src={`data:image/jpeg;base64,${image}`} alt={`captured image ${index + 1}`} />
            </div>
          ))}
        </div>
      </div>
      <div className="captured-images1">
        <h1>Camera 2</h1>
        <div className="captured-images-grid">
          {capturedImagesCam2.map((image, index) => (
            <div key={index} className="captured-image">
             
              <img src={`data:image/jpeg;base64,${image}`} alt={`captured image ${index + 1}`} />
            </div>
          ))}
        </div>
      </div>
        
      </div>
     
    </div>
  );
};


export default App;