const express = require('express');
const app = express();
app.use(express.json());
app.get('/api/health', (req, res) => res.json({ status: 'ok' }));
app.listen(process.env.PORT || 4000, () => console.log('Backend listening on ' + (process.env.PORT || 4000)));
