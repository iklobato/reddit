#!/bin/bash

# server.sh - Run this on the REMOTE machine
# Sets up ngrok tunnel to expose SSH

set -e

SSH_PORT=${SSH_PORT:-22}
NGROK_REGION=${NGROK_REGION:-us}

cleanup() {
    if [ ! -z "$NGROK_PID" ]; then
        kill "$NGROK_PID" 2>/dev/null
    fi
    exit
}

trap cleanup SIGINT SIGTERM EXIT

if ! command -v ngrok >/dev/null; then
    echo "Error: ngrok not found" >&2
    echo "Install from: https://ngrok.com/download" >&2
    exit 1
fi

echo "Checking SSH service..."
if ! pgrep -x "sshd" >/dev/null; then
    echo "Warning: SSH daemon (sshd) not running" >&2
    echo "Start it with: sudo systemctl start sshd (Linux) or sudo launchctl load -w /System/Library/LaunchDaemons/ssh.plist (macOS)" >&2
fi

echo "Checking SSH configuration..."
SSH_CONFIG="/etc/ssh/sshd_config"
if [ -f "$SSH_CONFIG" ]; then
    if grep -q "^PasswordAuthentication no" "$SSH_CONFIG" 2>/dev/null; then
        echo "Warning: Password authentication is disabled in SSH config" >&2
        echo "Client will need SSH keys for authentication" >&2
    fi
    if grep -q "^PubkeyAuthentication no" "$SSH_CONFIG" 2>/dev/null; then
        echo "Warning: Public key authentication is disabled" >&2
        echo "Only password authentication will work" >&2
    fi
fi

echo "Checking authorized keys..."
AUTHORIZED_KEYS="$HOME/.ssh/authorized_keys"
if [ -f "$AUTHORIZED_KEYS" ]; then
    KEY_COUNT=$(wc -l < "$AUTHORIZED_KEYS" 2>/dev/null || echo "0")
    echo "Found $KEY_COUNT authorized key(s) for $(whoami)"
else
    echo "No authorized_keys file found"
    echo "To allow key-based authentication, create: $AUTHORIZED_KEYS"
fi

if [ ! -z "$NGROK_AUTH_TOKEN" ]; then
    ngrok config add-authtoken "$NGROK_AUTH_TOKEN" >/dev/null 2>&1
fi

echo "Starting ngrok tunnel..."
ngrok tcp "$SSH_PORT" --region "$NGROK_REGION" >/dev/null 2>&1 &
NGROK_PID=$!

sleep 4

TUNNELS_JSON=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null)
PUBLIC_URL_LINE=$(echo "$TUNNELS_JSON" | grep -o '"public_url":"[^"]*tcp://[^"]*"' | head -1)
PUBLIC_URL=$(echo "$PUBLIC_URL_LINE" | cut -d'"' -f4)
NGROK_URL=$(echo "$PUBLIC_URL" | sed 's|tcp://||')

if [ -z "$NGROK_URL" ]; then
    echo "Error: Failed to retrieve ngrok URL" >&2
    exit 1
fi

IFS=':'
read -r HOST PORT <<< "$NGROK_URL"

echo ""
echo "=========================================="
echo "Server ready! Tunnel established"
echo "=========================================="
echo ""
echo "Copy these details to your CLIENT machine:"
echo ""
echo "  Host: $HOST"
echo "  Port: $PORT"
echo "  User: $(whoami)"
echo ""
echo "On your CLIENT machine, run:"
echo "  ./client.sh $HOST $PORT $(whoami)"
echo ""
echo "AUTHENTICATION SETUP (if needed):"
echo "  If client gets 'Permission denied', set up SSH keys:"
echo "  On CLIENT machine, run:"
echo "    ssh-copy-id -p $PORT $(whoami)@$HOST"
echo ""
echo "Press Ctrl+C to stop the tunnel"
echo ""

while kill -0 "$NGROK_PID" 2>/dev/null; do
    sleep 1
done
