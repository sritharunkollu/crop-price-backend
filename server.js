// server.js
// FINAL DEPLOYMENT VERSION: Make sure your MONGO_URI is correct.

const express = require('express');
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const cors = require('cors');
const { spawn } = require('child_process');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 5000;

// --- CORS Configuration ---
// This allows your server to accept requests from ANY website.
// For better security in a real product, you would restrict this.
app.use(cors());
app.use(express.json());


// --- MongoDB Connection ---
// PASTE YOUR CORRECT MONGO_URI FROM ATLAS HERE
// Make sure you have replaced <password> with your actual password.
const MONGO_URI = 'mongodb://localhost:27017/crop_price_db';

mongoose.connect(MONGO_URI)
    .then(() => console.log(">>> MongoDB Connection Successful!"))
    .catch(err => {
        console.error("!!! FAILED TO CONNECT TO MONGODB !!!", err);
        process.exit(1);
    });

// --- Mongoose Schema and Model ---
const UserSchema = new mongoose.Schema({
    username: { type: String, required: true, unique: true },
    email: { type: String, required: true, unique: true },
    password: { type: String, required: true },
});
const User = mongoose.model('User', UserSchema);


// --- API Endpoints (No changes needed here) ---

app.post('/api/register', async (req, res) => {
    try {
        const { username, email, password } = req.body;
        const existingUser = await User.findOne({ $or: [{ email }, { username }] });
        if (existingUser) return res.status(400).json({ message: 'Username or email already exists.' });
        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash(password, salt);
        const newUser = new User({ username, email, password: hashedPassword });
        await newUser.save();
        res.status(201).json({ message: 'User registered successfully!', user: { username: newUser.username } });
    } catch (error) {
        res.status(500).json({ message: 'Server error during registration.' });
    }
});

app.post('/api/login', async (req, res) => {
    try {
        const { username, password } = req.body;
        const user = await User.findOne({ username });
        if (!user) return res.status(400).json({ message: 'Invalid credentials.' });
        const isMatch = await bcrypt.compare(password, user.password);
        if (!isMatch) return res.status(400).json({ message: 'Invalid credentials.' });
        res.status(200).json({ message: 'Login successful!', user: { username: user.username } });
    } catch (error) {
        res.status(500).json({ message: 'Server error during login.' });
    }
});

app.post('/api/predict', (req, res) => {
    const { state, district, crop } = req.body;
    const pythonExecutable = 'python';
    const pythonScriptPath = path.join(__dirname, 'predict.py');
    const pythonProcess = spawn(pythonExecutable, ['-u', pythonScriptPath, state, district, crop]);
    let predictionData = '';
    let errorData = '';
    pythonProcess.stdout.on('data', (data) => { predictionData += data.toString(); });
    pythonProcess.stderr.on('data', (data) => { errorData += data.toString(); });
    pythonProcess.on('close', (code) => {
        if (code !== 0) {
            return res.status(500).json({ message: 'Python script failed.', error: errorData });
        }
        try {
            const result = JSON.parse(predictionData);
            if (result.error) {
                return res.status(500).json({ message: 'Prediction failed inside Python script.', error: result.error });
            }
            res.status(200).json(result);
        } catch (e) {
            res.status(500).json({ message: 'Failed to parse prediction result from Python script.' });
        }
    });
});

app.listen(PORT, () => {
    console.log(`\n>>> SERVER IS LIVE AND LISTENING ON http://localhost:${PORT}`);
});