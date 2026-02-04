import React from 'react';

const Test = () => {
  return (
    <div style={{ padding: '20px', backgroundColor: '#f0f0f0', minHeight: '100vh' }}>
      <h1 style={{ color: '#333', fontSize: '24px', marginBottom: '20px' }}>
        StatBot Pro - Test Page
      </h1>
      <p style={{ color: '#666', fontSize: '16px' }}>
        If you can see this, React is working correctly.
      </p>
      <div style={{ 
        backgroundColor: '#007bff', 
        color: 'white', 
        padding: '10px 20px', 
        borderRadius: '5px',
        marginTop: '20px',
        display: 'inline-block'
      }}>
        Frontend is working!
      </div>
    </div>
  );
};

export default Test;
