FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache git curl

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --include=dev

# Copy application files
COPY . .

# Create directories with proper permissions
RUN mkdir -p /tmp/vite-cache && chmod -R 777 /tmp/vite-cache

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Start the dev server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]