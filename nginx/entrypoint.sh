#!/bin/sh

# Create the directory for certificates
mkdir -p /etc/nginx/certs

# Generate self-signed certificate if it doesn't exist
if [ ! -f /etc/nginx/certs/self-signed.crt ]; then
    echo "🔐 Generating self-signed SSL certificate..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/nginx/certs/self-signed.key \
        -out /etc/nginx/certs/self-signed.crt \
        -subj "/C=US/ST=State/L=City/O=Localhost/CN=localhost"
    echo "✅ Certificate generated."
else
    echo "✅ Certificate already exists."
fi

# Start Nginx
exec nginx -g "daemon off;"