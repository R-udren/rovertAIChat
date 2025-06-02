#!/bin/sh
set -e

# Check if DOMAIN environment variable is set
if [ -z "$DOMAIN" ]; then
    echo "ERROR: DOMAIN environment variable is not set"
    exit 1
fi

echo "Configuring nginx for domain: $DOMAIN"

# Substitute environment variables in nginx configuration template
envsubst '${DOMAIN}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

# Validate nginx configuration
nginx -t

echo "Starting nginx..."
# Start nginx
exec nginx -g 'daemon off;'
