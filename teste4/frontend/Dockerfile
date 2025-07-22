# Frontend Dockerfile
FROM node:18-alpine AS builder

# Set work directory
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy project
COPY . .

# Build app with proper PUBLIC_URL
ENV GENERATE_SOURCEMAP=false
ENV PUBLIC_URL=/
RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

# Install serve globally
RUN npm install -g serve

# Copy built app from builder stage
COPY --from=builder /app/build ./build

# Expose port
EXPOSE 3000

# Run the application with SPA fallback
CMD ["serve", "-s", "build", "-l", "3000", "--no-clipboard"]