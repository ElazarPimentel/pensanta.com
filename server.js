require('dotenv').config();
const express = require('express');
const path = require('path');
const { Pool } = require('pg');

const app = express();
const port = process.env.PORT || 3000;

// PostgreSQL connection
const pool = process.env.DATABASE_URL
  ? new Pool({
      connectionString: process.env.DATABASE_URL,
      ssl: { rejectUnauthorized: false }
    })
  : new Pool({
      host: process.env.DB_HOST,
      port: process.env.DB_PORT,
      database: process.env.DB_NAME,
      user: process.env.DB_USER,
      password: process.env.DB_PASSWORD,
      ssl: process.env.DB_SSL === 'true' ? { rejectUnauthorized: false } : false
    });

// Middleware
app.use(express.json());

// API routes
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Example API endpoint - modify as needed
app.get('/api/data', async (req, res) => {
  try {
    const result = await pool.query('SELECT NOW() as current_time');
    res.json({ success: true, data: result.rows });
  } catch (error) {
    console.error('Database error:', error);
    res.status(500).json({ success: false, error: 'Database error' });
  }
});

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

