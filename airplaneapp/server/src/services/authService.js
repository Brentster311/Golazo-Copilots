const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

const SALT_ROUNDS = 10;

function toUserResponse(user) {
  return {
    id: user.id,
    email: user.email,
    name: user.name,
    createdAt: user.createdAt,
  };
}

function generateToken(userId) {
  const secret = process.env.JWT_SECRET;
  if (!secret) {
    throw new Error('JWT_SECRET environment variable is required');
  }
  return jwt.sign({ userId }, secret, {
    expiresIn: process.env.JWT_EXPIRES_IN || '24h',
  });
}

async function register(email, password, name) {
  const normalizedEmail = email.toLowerCase().trim();

  const existing = await prisma.user.findUnique({
    where: { email: normalizedEmail },
  });
  if (existing) {
    const error = new Error('Email is already registered');
    error.code = 'DUPLICATE_EMAIL';
    throw error;
  }

  const hashedPassword = await bcrypt.hash(password, SALT_ROUNDS);

  const user = await prisma.user.create({
    data: {
      email: normalizedEmail,
      password: hashedPassword,
      name,
    },
  });

  const token = generateToken(user.id);
  return { user: toUserResponse(user), token };
}

async function login(email, password) {
  const normalizedEmail = email.toLowerCase().trim();

  const user = await prisma.user.findUnique({
    where: { email: normalizedEmail },
  });

  if (!user) {
    throw new Error('Invalid email or password');
  }

  const valid = await bcrypt.compare(password, user.password);
  if (!valid) {
    throw new Error('Invalid email or password');
  }

  const token = generateToken(user.id);
  return { user: toUserResponse(user), token };
}

async function verifyToken(token) {
  if (!token) return null;

  try {
    const secret = process.env.JWT_SECRET;
    const decoded = jwt.verify(token, secret);
    const user = await prisma.user.findUnique({
      where: { id: decoded.userId },
    });
    if (!user) return null;
    return toUserResponse(user);
  } catch {
    return null;
  }
}

module.exports = { register, login, verifyToken };
