const { setupTestDb, teardownTestDb, cleanTestDb, getTestPrisma, TEST_DB_PATH } = require('./helpers');

// Set env vars before requiring authService
process.env.JWT_SECRET = 'test-secret-key-for-unit-tests';
process.env.JWT_EXPIRES_IN = '1h';
process.env.DATABASE_URL = `file:${TEST_DB_PATH}`;

let authService;

beforeAll(async () => {
  await setupTestDb();
  // Require after DB is set up so Prisma client connects to test DB
  authService = require('../src/services/authService');
});

afterAll(async () => {
  await teardownTestDb();
});

beforeEach(async () => {
  await cleanTestDb();
});

describe('AuthService', () => {
  describe('register', () => {
    it('should register a new user and return user + token', async () => {
      const result = await authService.register('pilot@test.com', 'securepass1', 'Test Pilot');

      expect(result).toHaveProperty('user');
      expect(result).toHaveProperty('token');
      expect(result.user.email).toBe('pilot@test.com');
      expect(result.user.name).toBe('Test Pilot');
      expect(result.user).not.toHaveProperty('password');
    });

    it('should store password as bcrypt hash', async () => {
      await authService.register('pilot@test.com', 'securepass1', 'Test Pilot');

      const prisma = getTestPrisma();
      const user = await prisma.user.findUnique({ where: { email: 'pilot@test.com' } });
      expect(user.password).toMatch(/^\$2[ab]\$/); // bcrypt prefix
      expect(user.password.length).toBe(60);
    });

    it('should normalize email to lowercase', async () => {
      const result = await authService.register('PILOT@TEST.COM', 'securepass1', 'Test Pilot');
      expect(result.user.email).toBe('pilot@test.com');
    });

    it('should reject duplicate emails', async () => {
      await authService.register('pilot@test.com', 'securepass1', 'Test Pilot');
      await expect(
        authService.register('pilot@test.com', 'otherpass1', 'Dupe Pilot')
      ).rejects.toThrow();
    });

    it('should reject duplicate emails case-insensitively', async () => {
      await authService.register('pilot@test.com', 'securepass1', 'Test Pilot');
      await expect(
        authService.register('PILOT@TEST.COM', 'otherpass1', 'Dupe Pilot')
      ).rejects.toThrow();
    });
  });

  describe('login', () => {
    beforeEach(async () => {
      await authService.register('pilot@test.com', 'securepass1', 'Test Pilot');
    });

    it('should login with valid credentials and return user + token', async () => {
      const result = await authService.login('pilot@test.com', 'securepass1');

      expect(result).toHaveProperty('user');
      expect(result).toHaveProperty('token');
      expect(result.user.email).toBe('pilot@test.com');
      expect(result.user).not.toHaveProperty('password');
    });

    it('should login case-insensitively for email', async () => {
      const result = await authService.login('PILOT@TEST.COM', 'securepass1');
      expect(result.user.email).toBe('pilot@test.com');
    });

    it('should reject wrong password', async () => {
      await expect(
        authService.login('pilot@test.com', 'wrongpassword')
      ).rejects.toThrow('Invalid email or password');
    });

    it('should reject non-existent email with same error', async () => {
      await expect(
        authService.login('nobody@test.com', 'anything')
      ).rejects.toThrow('Invalid email or password');
    });
  });

  describe('verifyToken', () => {
    it('should verify a valid token and return user', async () => {
      const { token } = await authService.register('pilot@test.com', 'securepass1', 'Test Pilot');
      const user = await authService.verifyToken(token);

      expect(user).not.toBeNull();
      expect(user.email).toBe('pilot@test.com');
      expect(user).not.toHaveProperty('password');
    });

    it('should return null for invalid token', async () => {
      const user = await authService.verifyToken('invalid.token.here');
      expect(user).toBeNull();
    });

    it('should return null for empty token', async () => {
      const user = await authService.verifyToken('');
      expect(user).toBeNull();
    });
  });
});
