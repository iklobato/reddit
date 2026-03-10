#!/bin/sh
set -e

# Create and setup log directory
mkdir -p /var/log/tor
chown -R tor:tor /var/log/tor
chmod 700 /var/log/tor
touch /var/log/tor/notices.log
chown tor:tor /var/log/tor/notices.log

echo "Starting Tor..."
tor -f /etc/tor/torrc > /var/log/tor/notices.log 2>&1 &

echo "Waiting for Tor to start..."
for i in $(seq 1 30); do
  if grep -q "Opened Socks listener" /var/log/tor/notices.log; then
    echo "Tor started successfully!"
    break
  fi
  echo "Waiting... ($i/30)"
  sleep 1
done

echo "Tor log output:"
cat /var/log/tor/notices.log

echo "Entering daemon mode..."
tail -f /var/log/tor/notices.log 