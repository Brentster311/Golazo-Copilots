const { PrismaClient } = require('@prisma/client');
const path = require('path');
const fs = require('fs');

const TEST_DB_PATH = path.join(__dirname, '..', 'test.db');

let prisma;

function getTestPrisma() {
  if (!prisma) {
    prisma = new PrismaClient({
      datasources: {
        db: { url: `file:${TEST_DB_PATH}` },
      },
    });
  }
  return prisma;
}

async function setupTestDb() {
  const { execSync } = require('child_process');
  // Only create if it doesn't exist — avoids EBUSY on Windows
  if (!fs.existsSync(TEST_DB_PATH)) {
    execSync('npx prisma migrate deploy', {
      cwd: path.join(__dirname, '..'),
      env: { ...process.env, DATABASE_URL: `file:${TEST_DB_PATH}` },
      stdio: 'pipe',
    });
  }
}

async function teardownTestDb() {
  if (prisma) {
    await prisma.$disconnect();
    prisma = null;
  }
}

async function cleanTestDb() {
  const p = getTestPrisma();
  await p.user.deleteMany();
}

module.exports = { getTestPrisma, setupTestDb, teardownTestDb, cleanTestDb, TEST_DB_PATH };
