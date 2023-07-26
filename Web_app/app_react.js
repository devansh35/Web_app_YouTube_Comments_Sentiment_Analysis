import React, { useState } from 'react';
import axios from 'axios';
import CircularProgress from '@mui/material/CircularProgress';

function YoutubeSentimentAnalysis() {
 const [videoLink, setVideoLink] = useState('');
 const [sentiment, setSentiment] = useState('');
 const [loading, setLoading] = useState(false);

 const handleSubmit = (event) => {
 event.preventDefault();
 setLoading(true);
 setSentiment(''); // Reset the sentiment state
 axios.post('http://127.0.0.1:5000/predict_sentiment', {
 video_link: videoLink,
 }, {
 headers: {
 'Content-Type': 'application/x-www-form-urlencoded'
 } 
 })
 .then(response => {
 if (response.data.error) {
 // Handle error
 console.log(response.data.error);
 } else {
 setSentiment(response.data);
 }
 setLoading(false);
 })
 .catch(error => {
 console.log(error);
 setLoading(false);
 });

 event.target.querySelector('input[type="text"]').blur();

 const inputField = event.target.querySelector('input[type="text"]');
inputField.selectionStart = 0;
inputField.selectionEnd = 0;
 }

 return (
 <div className="YoutubeSentimentAnalysis">
 <h1 className="text-color">Youtube Comment Sentiment Analysis</h1>
 <form onSubmit={handleSubmit}>
 <label className="video-link">
 <span className="text-color">Video link:</span>
 <input type="text" value={videoLink} onChange={event => setVideoLink(event.target.value)} />
</label>
 <button type="submit">Submit</button>
 </form>
 {loading && <CircularProgress className="circular-progress" />}
 {sentiment && <p>The sentiment of the video is: {sentiment}</p>}
 </div>
 );
}

export default YoutubeSentimentAnalysis;