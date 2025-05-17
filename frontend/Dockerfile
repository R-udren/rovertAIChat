# use the official Bun image
FROM oven/bun:alpine AS base
WORKDIR /usr/src/app

# install dependencies into temp directory
FROM base AS install
RUN mkdir -p /temp/dev
COPY package.json /temp/dev/
RUN cd /temp/dev && bun install --frozen-lockfile

# install with --production (exclude devDependencies)
RUN mkdir -p /temp/prod
COPY package.json /temp/prod/
RUN cd /temp/prod && bun install --frozen-lockfile --production

# Build stage
FROM base AS build
COPY --from=install /temp/dev/node_modules node_modules
COPY . .
ENV NODE_ENV=production
RUN bun run build

# Production stage - using nginx to serve static files
FROM nginx:alpine AS release
# Copy nginx configuration
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
# Copy built static files from build stage
COPY --from=build /usr/src/app/dist /usr/share/nginx/html

EXPOSE 80