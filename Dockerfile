# Build stage for frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# Build stage for backend
FROM python:3.11-slim AS backend-build
WORKDIR /app/backend
COPY backend/api/src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim
WORKDIR /app

# Install Node.js for serving frontend
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    netcat-traditional \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend files
COPY --from=backend-build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY backend/api/src/ ./backend/

# Copy frontend build
COPY --from=frontend-build /app/frontend/.next ./frontend/.next
COPY --from=frontend-build /app/frontend/public ./frontend/public
COPY --from=frontend-build /app/frontend/package*.json ./frontend/
COPY --from=frontend-build /app/frontend/node_modules ./frontend/node_modules

# Copy crawled data
COPY data/crawls/ ./data/crawls/

# Create a script to run both services
COPY <<EOF /app/start.sh
#!/bin/bash
# Start Neo4j (assuming it's running in a separate container)
# Wait for Neo4j to be ready
echo "Waiting for Neo4j to be ready..."
while ! nc -z neo4j 7687; do
  sleep 1
done
echo "Neo4j is ready!"

# Load data into Neo4j
echo "Loading data into Neo4j..."
cd /app/backend
python load_data.py

# Start backend
cd /app/backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start frontend
cd /app/frontend
npm run start -- -p 3000 &
FRONTEND_PID=$!

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
EOF

RUN chmod +x /app/start.sh

# Expose ports
EXPOSE 3000 8000

# Start the application
CMD ["/app/start.sh"] 