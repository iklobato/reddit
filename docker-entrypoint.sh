#!/bin/sh
set -e

# Print container info
echo "Starting camera scanner container..."
echo "Python version: $(python --version)"
echo "Environment: TZ=${TZ:-UTC}, PYTHONFAULTHANDLER=${PYTHONFAULTHANDLER:-0}"

# Sleep to ensure Tor service is fully initialized
DELAY=${TOR_STARTUP_DELAY:-10}
echo "Waiting ${DELAY} seconds for Tor to initialize..."
sleep ${DELAY}

# Try to verify Tor connection is ready
if grep -q "enabled: true" /app/config.yaml; then
  echo "Tor is enabled in config. Checking connection..."
  TOR_HOST=$(grep -A 2 "tor_proxy:" /app/config.yaml | grep "host:" | awk '{print $2}')
  TOR_PORT=$(grep -A 3 "tor_proxy:" /app/config.yaml | grep "port:" | awk '{print $2}')
  
  echo "Checking Tor proxy at ${TOR_HOST}:${TOR_PORT}..."
  # Simple connection test with netcat
  if command -v nc >/dev/null 2>&1; then
    if nc -z ${TOR_HOST} ${TOR_PORT} >/dev/null 2>&1; then
      echo "Tor appears to be running and accessible!"
    else
      echo "WARNING: Cannot connect to Tor proxy at ${TOR_HOST}:${TOR_PORT}"
      echo "The application will still try to connect using its retry mechanism"
    fi
  else
    echo "Netcat not available, skipping Tor connection pre-check"
  fi
fi

# Run OpenCV check
echo "Verifying OpenCV setup..."
python /app/check_opencv.py || { echo "OpenCV check failed!"; exit 1; }

# Execute the main application
echo "Starting camera scanner..."
exec python /app/t1.py 