#!/bin/bash

# client.sh - Run this on your LOCAL machine
# Connects to remote machine via ngrok and sets up browser proxy

set -e

if [ $# -lt 2 ]; then
    echo "Usage: $0 <ngrok_host> <ngrok_port> [username] [browser] [socks_port]"
    echo ""
    echo "Get the connection details from the remote machine running server.sh"
    echo ""
    echo "Example:"
    echo "  ./client.sh 2.tcp.ngrok.io 19829 henriquelobato chrome"
    echo ""
    echo "Parameters:"
    echo "  <ngrok_host> - Host from server.sh output"
    echo "  <ngrok_port> - Port from server.sh output"
    echo "  [username]   - SSH username (from server.sh output, default: current user)"
    echo "  [browser]    - chrome, firefox, edge (default: chrome)"
    echo "  [socks_port]  - SOCKS proxy port (default: 1080)"
    exit 1
fi

NGROK_HOST=$1
NGROK_PORT=$2

if [ $# -ge 3 ] && [[ ! "$3" =~ ^(chrome|firefox|edge)$ ]]; then
    SSH_USER=$3
    BROWSER=${4:-chrome}
    SOCKS_PORT=${5:-1080}
else
    SSH_USER=$USER
    BROWSER=${3:-chrome}
    SOCKS_PORT=${4:-1080}
fi

cleanup() {
    if [ ! -z "$SSH_PID" ]; then
        kill "$SSH_PID" 2>/dev/null
        echo "Proxy stopped"
    fi
    exit
}

trap cleanup SIGINT SIGTERM EXIT

echo "Connecting to remote machine..."
echo "  Host: $NGROK_HOST"
echo "  Port: $NGROK_PORT"
echo "  User: $SSH_USER"
echo ""

echo "Testing SSH connection..."
SSH_OPTS="-p $NGROK_PORT -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new"

if ssh $SSH_OPTS -o BatchMode=yes "$SSH_USER@$NGROK_HOST" exit 2>/dev/null; then
    echo "SSH key authentication working"
    echo "Starting SOCKS proxy on port $SOCKS_PORT..."
    ssh $SSH_OPTS -D "$SOCKS_PORT" -N -f "$SSH_USER@$NGROK_HOST"
else
    echo ""
    echo "SSH key authentication not set up."
    echo ""
    echo "SETUP REQUIRED:"
    echo "  Option 1 - Set up SSH keys (recommended):"
    echo "    ssh-copy-id -p $NGROK_PORT $SSH_USER@$NGROK_HOST"
    echo "    (You'll be prompted for password once)"
    echo ""
    echo "  Option 2 - Use password authentication:"
    echo "    Run this script in an interactive terminal, or"
    echo "    manually connect: ssh -p $NGROK_PORT $SSH_USER@$NGROK_HOST"
    echo ""
    echo "Attempting connection with password (if in interactive terminal)..."
    ssh $SSH_OPTS -D "$SOCKS_PORT" -N "$SSH_USER@$NGROK_HOST" &
    SSH_PID=$!
    sleep 2
    
    if ! kill -0 "$SSH_PID" 2>/dev/null; then
        echo ""
        echo "Connection failed. Please set up SSH keys first:"
        echo "  ssh-copy-id -p $NGROK_PORT $SSH_USER@$NGROK_HOST"
        exit 1
    fi
fi

sleep 2
SSH_PID=$(pgrep -f "ssh -p $NGROK_PORT -D $SOCKS_PORT.*$SSH_USER@$NGROK_HOST")

if [ -z "$SSH_PID" ]; then
    echo "Error: Failed to start SOCKS proxy" >&2
    echo "" >&2
    echo "Troubleshooting:" >&2
    echo "  1. Test SSH connection manually:" >&2
    echo "     ssh -p $NGROK_PORT $SSH_USER@$NGROK_HOST" >&2
    echo "  2. Make sure SSH keys are set up or password authentication works" >&2
    echo "  3. Verify the username matches the server output" >&2
    exit 1
fi

echo "SOCKS proxy started (PID: $SSH_PID)"
echo ""

echo "Launching browser with proxy configuration..."

case "$BROWSER" in
    chrome)
        if command -v google-chrome >/dev/null; then
            google-chrome --proxy-server="socks5://127.0.0.1:$SOCKS_PORT" >/dev/null 2>&1 &
        elif command -v chromium >/dev/null; then
            chromium --proxy-server="socks5://127.0.0.1:$SOCKS_PORT" >/dev/null 2>&1 &
        elif [ -d "/Applications/Google Chrome.app" ]; then
            /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --proxy-server="socks5://127.0.0.1:$SOCKS_PORT" >/dev/null 2>&1 &
        else
            echo "Chrome not found. Launch manually with:"
            echo "  chrome --proxy-server=\"socks5://127.0.0.1:$SOCKS_PORT\""
            BROWSER_LAUNCHED=false
        fi
        ;;
    firefox)
        if command -v firefox >/dev/null; then
            firefox >/dev/null 2>&1 &
        elif [ -d "/Applications/Firefox.app" ]; then
            /Applications/Firefox.app/Contents/MacOS/firefox >/dev/null 2>&1 &
        else
            echo "Firefox not found. Launch manually and configure:"
            echo "  Settings > Network Settings > Manual proxy > SOCKS v5 > 127.0.0.1:$SOCKS_PORT"
            BROWSER_LAUNCHED=false
        fi
        if [ "$BROWSER_LAUNCHED" != false ]; then
            echo "Firefox launched. Configure proxy:"
            echo "  Settings > Network Settings > Manual proxy > SOCKS v5 > 127.0.0.1:$SOCKS_PORT"
        fi
        ;;
    edge)
        if command -v microsoft-edge >/dev/null; then
            microsoft-edge --proxy-server="socks5://127.0.0.1:$SOCKS_PORT" >/dev/null 2>&1 &
        elif [ -d "/Applications/Microsoft Edge.app" ]; then
            /Applications/Microsoft\ Edge.app/Contents/MacOS/Microsoft\ Edge --proxy-server="socks5://127.0.0.1:$SOCKS_PORT" >/dev/null 2>&1 &
        else
            echo "Edge not found. Launch manually with:"
            echo "  edge --proxy-server=\"socks5://127.0.0.1:$SOCKS_PORT\""
            BROWSER_LAUNCHED=false
        fi
        ;;
    *)
        echo "Unknown browser: $BROWSER"
        echo "Available: chrome, firefox, edge"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "Ready! Tunnel is active"
echo "=========================================="
echo ""
echo "You can now access any URL on the remote intranet:"
echo "  https://dt-fe-app-rivianos.dev.ue1.dc.goriv.co/order/collision"
echo "  https://any-domain.internal/any/path"
echo ""
echo "All domains are automatically routed through the tunnel."
echo "No /etc/hosts configuration needed."
echo ""
echo "Proxy running (PID: $SSH_PID)"
echo "Press Ctrl+C to stop"

while true; do
    if ! kill -0 "$SSH_PID" 2>/dev/null; then
        echo "Proxy connection lost"
        break
    fi
    sleep 1
done
