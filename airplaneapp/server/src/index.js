const app = require('./app');

const PORT = process.env.PORT || 3001;

if (!process.env.JWT_SECRET) {
  console.error('FATAL: JWT_SECRET environment variable is required. Set it in .env file.');
  process.exit(1);
}

app.listen(PORT, () => {
  console.log(`AirplaneApp server running on port ${PORT}`);
});
