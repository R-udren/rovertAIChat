# Simple Frontend Dockerfile for Caddy setup
# Build stage
FROM oven/bun:alpine AS build

WORKDIR /app
COPY package.json ./
RUN bun install --frozen-lockfile
COPY . .
RUN bun run build

# Serve stage - minimal static file server
FROM nginx:alpine

# Copy our custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built files
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
