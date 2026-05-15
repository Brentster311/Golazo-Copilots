const request = require('supertest');
const { setupTestDb, teardownTestDb, cleanTestDb, TEST_DB_PATH } = require('./helpers');

process.env.JWT_SECRET = 'test-secret-key-for-integration';
process.env.JWT_EXPIRES_IN = '1h';
process.env.DATABASE_URL = `file:${TEST_DB_PATH}`;

let app;

beforeAll(async () => {
  await setupTestDb();
  // Clear module cache so app picks up test DATABASE_URL
  delete require.cache[require.resolve('../src/services/authService')];
  delete require.cache[require.resolve('../src/app')];
  app = require('../src/app');
});

afterAll(async () => {
  await teardownTestDb();
});

beforeEach(async () => {
  await cleanTestDb();
});

describe('POST /api/auth/register', () => {
  it('TC-1.1: should register a new user and return 201 with user and token', async () => {
    const res = await request(app)
      .post('/api/auth/register')
      .send({ email: 'pilot@test.com', password: 'securepass1', name: 'Test Pilot' });

    expect(res.status).toBe(201);
    expect(res.body).toHaveProperty('user');
    expect(res.body).toHaveProperty('token');
    expect(res.body.user).toHaveProperty('id');
    expect(res.body.user.email).toBe('pilot@test.com');
    expect(res.body.user.name).toBe('Test Pilot');
    expect(res.body.user).not.toHaveProperty('password');
  });

  it('TC-1.2: should reject duplicate email with 409', async () => {
    await request(app)
      .post('/api/auth/register')
      .send({ email: 'pilot@test.com', password: 'securepass1', name: 'Test Pilot' });

    const res = await request(app)
      .post('/api/auth/register')
      .send({ email: 'pilot@test.com', password: 'otherpass1', name: 'Dupe Pilot' });

    expect(res.status).toBe(409);
    expect(res.body).toHaveProperty('error');
  });

  it('TC-1.3: should return 400 for missing required fields', async () => {
    const res = await request(app)
      .post('/api/auth/register')
      .send({ email: 'pilot@test.com' });

    expect(res.status).toBe(400);
    expect(res.body).toHaveProperty('error');
  });

  it('TC-1.4: should return 400 for invalid email format', async () => {
    const res = await request(app)
      .post('/api/auth/register')
      .send({ email: 'not-an-email', password: 'securepass1', name: 'Bad Email' });

    expect(res.status).toBe(400);
    expect(res.body).toHaveProperty('error');
  });

  it('TC-1.5: should return 400 for password too short', async () => {
    const res = await request(app)
      .post('/api/auth/register')
      .send({ email: 'short@test.com', password: 'abc', name: 'Short Pass' });

    expect(res.status).toBe(400);
    expect(res.body).toHaveProperty('error');
  });

  it('TC-1.6: should reject case-variant duplicate emails', async () => {
    await request(app)
      .post('/api/auth/register')
      .send({ email: 'Pilot@Test.COM', password: 'securepass1', name: 'First' });

    const res = await request(app)
      .post('/api/auth/register')
      .send({ email: 'pilot@test.com', password: 'securepass1', name: 'Second' });

    expect(res.status).toBe(409);
  });
});

describe('POST /api/auth/login', () => {
  beforeEach(async () => {
    await request(app)
      .post('/api/auth/register')
      .send({ email: 'pilot@test.com', password: 'securepass1', name: 'Test Pilot' });
  });

  it('TC-2.1: should login with valid credentials and return 200', async () => {
    const res = await request(app)
      .post('/api/auth/login')
      .send({ email: 'pilot@test.com', password: 'securepass1' });

    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('user');
    expect(res.body).toHaveProperty('token');
    expect(res.body.user.email).toBe('pilot@test.com');
    expect(res.body.user).not.toHaveProperty('password');
  });

  it('TC-2.2: should return 401 for wrong password with generic message', async () => {
    const res = await request(app)
      .post('/api/auth/login')
      .send({ email: 'pilot@test.com', password: 'wrongpassword' });

    expect(res.status).toBe(401);
    expect(res.body.error).toBe('Invalid email or password');
  });

  it('TC-2.3: should return 401 for non-existent email with same generic message', async () => {
    const res = await request(app)
      .post('/api/auth/login')
      .send({ email: 'nobody@test.com', password: 'anything' });

    expect(res.status).toBe(401);
    expect(res.body.error).toBe('Invalid email or password');
  });

  it('TC-2.4: should return 400 for missing password', async () => {
    const res = await request(app)
      .post('/api/auth/login')
      .send({ email: 'pilot@test.com' });

    expect(res.status).toBe(400);
  });

  it('TC-2.5: should login case-insensitively for email', async () => {
    const res = await request(app)
      .post('/api/auth/login')
      .send({ email: 'PILOT@TEST.COM', password: 'securepass1' });

    expect(res.status).toBe(200);
    expect(res.body.user.email).toBe('pilot@test.com');
  });
});

describe('GET /api/auth/me', () => {
  let token;

  beforeEach(async () => {
    const res = await request(app)
      .post('/api/auth/register')
      .send({ email: 'pilot@test.com', password: 'securepass1', name: 'Test Pilot' });
    token = res.body.token;
  });

  it('TC-3.1: should return user data for authenticated request', async () => {
    const res = await request(app)
      .get('/api/auth/me')
      .set('Authorization', `Bearer ${token}`);

    expect(res.status).toBe(200);
    expect(res.body.user.email).toBe('pilot@test.com');
    expect(res.body.user.name).toBe('Test Pilot');
    expect(res.body.user).not.toHaveProperty('password');
  });

  it('TC-3.2: should return 401 when no token provided', async () => {
    const res = await request(app).get('/api/auth/me');
    expect(res.status).toBe(401);
  });

  it('TC-3.3: should return 401 for invalid token', async () => {
    const res = await request(app)
      .get('/api/auth/me')
      .set('Authorization', 'Bearer invalid.token.here');

    expect(res.status).toBe(401);
  });

  it('TC-3.5: should never include password in response', async () => {
    const res = await request(app)
      .get('/api/auth/me')
      .set('Authorization', `Bearer ${token}`);

    expect(res.status).toBe(200);
    expect(res.body.user).not.toHaveProperty('password');
    expect(JSON.stringify(res.body)).not.toContain('$2b$');
    expect(JSON.stringify(res.body)).not.toContain('$2a$');
  });
});
