import React, { useEffect, useState } from 'react';
import './App.css';

function App() {
  const [message, setMessage] = useState('');
  const [health, setHealth] = useState('');

  useEffect(() => {
    // Test API calls
    fetch('/api/health')
      .then(res => res.json())
      .then(data => setHealth(data.status))
      .catch(err => console.error('Error fetching health:', err));

    fetch('/api/hello')
      .then(res => res.json())
      .then(data => setMessage(data.message))
      .catch(err => console.error('Error fetching hello:', err));
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>FastAPI + React on Azure</h1>
        <p>Health Status: {health || 'Loading...'}</p>
        <p>API Message: {message || 'Loading...'}</p>
      </header>
    </div>
  );
}

export default App;