FROM nginx:alpine

# Install OpenSSL (needed for cert generation)
RUN apk add --no-cache openssl

# Copy our configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy startup script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Use our script as the entrypoint
ENTRYPOINT ["/entrypoint.sh"]