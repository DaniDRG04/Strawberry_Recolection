const express = require('express');
const mysql = require('mysql2');
const cors = require('cors');

const app = express();
app.use(cors()); // Allow requests from Ionic app
app.use(express.json());

// MySQL connection
const db = mysql.createConnection({
  host: '10.25.15.228',   // Your DB IP
  user: 'starwberry',
  password: '1234567890',
  database: 'stawberries',
  port: 3306
});

db.connect(err => {
  if (err) {
    console.error('MySQL connection error:', err);
  } else {
    console.log('Connected to MySQL');
  }
});

// Example endpoint to get all data
app.get('/data', (req, res) => {
  db.query('SELECT * FROM plant_images', (err, results) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    res.json(results);
  });
});

// Start server
app.listen(3000, () => {
  console.log('Server running on http://localhost:3000');
});
