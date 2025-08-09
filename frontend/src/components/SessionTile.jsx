import React from 'react';

// A simplified version for debugging
const SessionTile = ({ session }) => {
  if (!session) {
    return (
      <div style={{ padding: '20px', border: '1px solid red' }}>
        <p>Error: Session prop is missing!</p>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', border: '1px solid green' }}>
      <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{session.session_name}</h3>
      <p>Location: {session.location}</p>
      <p>If you can see this, the basic component is rendering correctly.</p>
    </div>
  );
};

export default SessionTile;