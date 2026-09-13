# Development stage - with hot reload support
FROM node:18-alpine as development

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy application code
COPY . .

# Create non-root user
RUN addgroup -g 1000 nodejs && \
    adduser -S nextjs -u 1000
USER nextjs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=5 --start-period=20s \
    CMD wget --quiet --tries=1 --spider http://localhost:3000 || exit 1

# Run development server with hot reload
CMD ["npm", "run", "dev"]

# Builder stage - for production builds
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Build application
RUN npm run build

# Production stage - optimized runtime
FROM node:18-alpine as production

WORKDIR /app

# Install only production dependencies
COPY package*.json ./
RUN npm ci --omit=dev

# Copy built application from builder stage
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.js ./

# Create non-root user for security
RUN addgroup -g 1000 nodejs && \
    adduser -S nextjs -u 1000
USER nextjs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=5 --start-period=20s \
    CMD wget --quiet --tries=1 --spider http://localhost:3000 || exit 1

# Run production server
CMD ["npm", "start"]
