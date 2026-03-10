#!/bin/bash

# auto_browser_proxy.sh - Automatically set up SOCKS proxy and launch browser
# Usage: ./auto_browser_proxy.sh <ngrok_host> <ngrok_port> [browser] [socks_port]

if [ $# -lt 2 ]; then
    echo "Usage: $0 <ngrok_host> <ngrok_port> [browser] [socks_port]"
    echo "Example: $0 0.tcp.ngrok.io 12345 chrome 1080"
    echo "Browsers: chrome, firefox, edge"
    exit 1
fi

NGROK_HOST=$1
NGROK_PORT=$2
BROWSER=${3:-chrome}
SOCKS_PORT=${4:-1080}

USER=$(whoami)

cleanup() {
    if [ ! -z "$SSH_PID" ]; then
        kill "$SSH_PID" 2>/dev/null
        echo "Proxy stopped"
    fi
    exit
}

trap cleanup SIGINT SIGTERM EXIT

echo "Starting SOCKS proxy on port $SOCKS_PORT..."
ssh -p "$NGROK_PORT" -D "$SOCKS_PORT" -N -f "$USER@$NGROK_HOST"

sleep 1
SSH_PID=$(pgrep -f "ssh -p $NGROK_PORT -D $SOCKS_PORT")

if [ -z "$SSH_PID" ]; then
    echo "Error: Failed to start SOCKS proxy" >&2
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
        elif command -v /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome >/dev/null; then
            /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --proxy-server="socks5://127.0.0.1:$SOCKS_PORT" >/dev/null 2>&1 &
        else
            echo "Chrome not found. Configure proxy manually:"
            echo "  chrome --proxy-server=\"socks5://127.0.0.1:$SOCKS_PORT\""
        fi
        ;;
    firefox)
        if command -v firefox >/dev/null; then
            firefox >/dev/null 2>&1 &
            echo "Firefox launched. Configure proxy:"
            echo "  Settings > Network Settings > Manual proxy > SOCKS v5 > 127.0.0.1:$SOCKS_PORT"
        elif command -v /Applications/Firefox.app/Contents/MacOS/firefox >/dev/null; then
            /Applications/Firefox.app/Contents/MacOS/firefox >/dev/null 2>&1 &
            echo "Firefox launched. Configure proxy:"
            echo "  Settings > Network Settings > Manual proxy > SOCKS v5 > 127.0.0.1:$SOCKS_PORT"
        else
            echo "Firefox not found. Configure proxy manually:"
            echo "  Settings > Network Settings > Manual proxy > SOCKS v5 > 127.0.0.1:$SOCKS_PORT"
        fi
        ;;
    edge)
        if command -v microsoft-edge >/dev/null; then
            microsoft-edge --proxy-server="socks5://127.0.0.1:$SOCKS_PORT" >/dev/null 2>&1 &
        elif command -v /Applications/Microsoft\ Edge.app/Contents/MacOS/Microsoft\ Edge >/dev/null; then
            /Applications/Microsoft\ Edge.app/Contents/MacOS/Microsoft\ Edge --proxy-server="socks5://127.0.0.1:$SOCKS_PORT" >/dev/null 2>&1 &
        else
            echo "Edge not found. Configure proxy manually:"
            echo "  edge --proxy-server=\"socks5://127.0.0.1:$SOCKS_PORT\""
        fi
        ;;
    *)
        echo "Unknown browser: $BROWSER"
        echo "Available: chrome, firefox, edge"
        exit 1
        ;;
esac

echo ""
echo "Proxy is active. All domains are automatically routed through the tunnel."
echo "You can now access any URL directly:"
echo "  https://dt-fe-app-rivianos.dev.ue1.dc.goriv.co/order/collision"
echo "  https://any-other-domain.internal/any/path"
echo ""
echo "Proxy running in background (PID: $SSH_PID)"
echo "To stop: kill $SSH_PID"
echo ""
echo "Press Ctrl+C to exit (proxy will continue running)"
echo "To stop proxy later, run: kill $SSH_PID"

while true; do
    if ! kill -0 "$SSH_PID" 2>/dev/null; then
        echo "Proxy stopped"
        break
    fi
    sleep 1
done
