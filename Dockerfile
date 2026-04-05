# Stage 1: Build React frontend
FROM node:22-alpine AS frontend
WORKDIR /app/client
COPY client/package*.json ./
RUN npm ci
COPY client/ ./
RUN npm run build

# Stage 2: Python runtime
FROM python:3.12-slim
WORKDIR /app
COPY server/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY server/ ./server/
COPY --from=frontend /app/client/dist ./client/dist
RUN adduser --disabled-password --uid 1001 appuser
USER appuser
EXPOSE 3616
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "3616"]
