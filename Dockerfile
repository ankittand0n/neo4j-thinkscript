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

# Copy backend files and install dependencies
COPY backend/api/src/requirements.txt ./backend/
RUN pip install --no-cache-dir -r ./backend/requirements.txt
COPY backend/api/src/ ./backend/

# Copy frontend build
COPY --from=frontend-build /app/frontend/.next ./frontend/.next
COPY --from=frontend-build /app/frontend/public ./frontend/public
COPY --from=frontend-build /app/frontend/package*.json ./frontend/
COPY --from=frontend-build /app/frontend/node_modules ./frontend/node_modules

# Copy crawled data
COPY data/crawls/ ./data/crawls/

# Copy start script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Expose ports
EXPOSE 3000 8000

# Start the application
CMD ["/app/start.sh"] 