FROM alpine:latest

# Install Tor and dependencies
RUN apk --no-cache add \
    tor \
    bash \
    curl \
    grep \
    procps \
    openrc

# Create necessary directories
RUN mkdir -p /var/log/tor && \
    chown -R tor:tor /var/log/tor && \
    chmod 700 /var/log/tor

# Copy torrc configuration and entrypoint script
COPY torrc /etc/tor/torrc
COPY tor-entrypoint.sh /entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /entrypoint.sh

EXPOSE 9050

# Healthcheck
HEALTHCHECK --interval=5s --timeout=30s --start-period=15s --retries=5 \
  CMD grep -q "Opened Socks listener on 0.0.0.0:9050" /var/log/tor/notices.log || exit 1

ENTRYPOINT ["/entrypoint.sh"] 