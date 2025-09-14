#!/bin/bash
set -e

echo "Starting Blog API..."

# Run database initialization
echo "Initializing database..."
python /app/init_database.py

# Start the API server
echo "Starting uvicorn server..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload