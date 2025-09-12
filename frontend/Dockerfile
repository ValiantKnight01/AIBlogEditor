FROM node:18-alpine

# Set environment variables
ENV NODE_ENV=development

# Install system dependencies
RUN apk add --no-cache \
    git \
    curl

# Create app directory
WORKDIR /app

# Copy package files
COPY package.json ./

# Install dependencies (use npm install if no lock file exists)
RUN if [ -f package-lock.json ]; then \
        npm ci --include=dev; \
    else \
        npm install; \
    fi

# Copy source code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S appgroup \
    && adduser -S appuser -u 1001 -G appgroup \
    && chown -R appuser:appgroup /app

USER appuser

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Start command
CMD ["npm", "run", "dev"]