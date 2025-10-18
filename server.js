// file: server.js
// version: 1.0

require('dotenv').config({ path: '.env.local' });
const express = require('express');
const path = require('path');
const { Pool } = require('pg');

const app = express();
const port = process.env.PORT || 3987;


// Middleware
app.use(express.json());


// Serve static files (your HTML, CSS, images)
app.use(express.static(__dirname));

// Fallback for SPA-like behavior (optional)
app.get('*', (req, res) => {
  if (!req.path.startsWith('/api/')) {
    res.sendFile(path.join(__dirname, 'index.html'));
  } else {
    res.status(404).json({ error: 'API endpoint not found' });
  }
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});

