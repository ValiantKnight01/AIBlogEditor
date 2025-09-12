-- Initialize database for Personal Blog
-- This script runs automatically when PostgreSQL container starts

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create database user if not exists (Docker will create the database)
-- Additional initialization can be added here as needed

-- Create indexes for performance (will be managed by Alembic)
-- This is just a placeholder for any initial setup

SELECT 'Database initialized successfully' as status;
