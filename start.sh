#!/bin/bash

# Wait for Neo4j to be ready
echo "Waiting for Neo4j to be ready..."
while ! nc -z neo4j 7687; do
  sleep 1
done
echo "Neo4j is ready!"

# Install backend dependencies
echo "Installing backend dependencies..."
cd /app/backend
pip install --no-cache-dir -r requirements.txt

# Load data into Neo4j
echo "Loading data into Neo4j..."
python load_data.py

# Start backend
echo "Starting backend..."
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start frontend
echo "Starting frontend..."
cd /app/frontend
npm run start -- -p 3000 &
FRONTEND_PID=$!

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID 