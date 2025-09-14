#!/bin/bash

echo "Starting the backend server in the background..."

# Navigate to backend, activate venv, and start server
(cd backend && source venv/Scripts/activate && uvicorn main:app --reload) &

echo "Waiting for server to launch..."
sleep 3

echo "Opening the frontend in your browser..."

# Open the URL with the /frontend/ path
start http://127.0.0.1:5500/frontend/index.html

echo "Backend is running. To stop it, close this terminal window."