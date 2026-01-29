import React from 'react';

const App = () => {
  return (
    <div style={{ 
      padding: '40px', 
      backgroundColor: '#1a1a1a', 
      color: 'white', 
      minHeight: '100vh',
      fontFamily: 'Arial, sans-serif'
    }}>
      <h1 style={{ fontSize: '48px', textAlign: 'center', marginBottom: '20px' }}>
        StatBot Pro
      </h1>
      <p style={{ fontSize: '18px', textAlign: 'center', color: '#ccc' }}>
        Frontend is working! React is rendering correctly.
      </p>
      <div style={{
        backgroundColor: '#007bff',
        color: 'white',
        padding: '20px',
        borderRadius: '8px',
        textAlign: 'center',
        marginTop: '40px',
        maxWidth: '600px',
        margin: '40px auto 0'
      }}>
        <h2>✅ Success!</h2>
        <p>If you can see this, the frontend is working properly.</p>
      </div>
    </div>
  );
};

export default App;