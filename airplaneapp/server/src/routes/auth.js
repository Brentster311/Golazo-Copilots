const express = require('express');
const authService = require('../services/authService');
const authMiddleware = require('../middleware/auth');

const router = express.Router();

// Simple email regex for basic validation
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

router.post('/register', async (req, res) => {
  try {
    const { email, password, name } = req.body;

    // Validate required fields
    const errors = [];
    if (!email) errors.push('Email is required');
    if (!password) errors.push('Password is required');
    if (!name) errors.push('Name is required');
    if (errors.length > 0) {
      return res.status(400).json({ error: errors.join(', ') });
    }

    // Validate email format
    if (!EMAIL_REGEX.test(email)) {
      return res.status(400).json({ error: 'Invalid email format' });
    }

    // Validate password length
    if (password.length < 8) {
      return res.status(400).json({ error: 'Password must be at least 8 characters' });
    }

    const result = await authService.register(email, password, name);
    return res.status(201).json(result);
  } catch (err) {
    if (err.code === 'DUPLICATE_EMAIL') {
      return res.status(409).json({ error: err.message });
    }
    console.error('Registration error:', err.message);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password are required' });
    }

    const result = await authService.login(email, password);
    return res.status(200).json(result);
  } catch (err) {
    if (err.message === 'Invalid email or password') {
      return res.status(401).json({ error: err.message });
    }
    console.error('Login error:', err.message);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

router.get('/me', authMiddleware, async (req, res) => {
  return res.status(200).json({ user: req.user });
});

module.exports = router;
