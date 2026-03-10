#!/bin/bash

# connect_remote_browser.sh - Connect to remote machine via ngrok and access webpages
# Run this on your LOCAL machine
# Usage: ./connect_remote_browser.sh <ngrok_host> <ngrok_port> [browser] [socks_port]

if [ $# -lt 2 ]; then
    echo "Usage: $0 <ngrok_host> <ngrok_port> [browser] [socks_port]"
    echo ""
    echo "First, get the connection details from the remote machine:"
    echo "  The remote machine running ngrok_ssh_proxy.sh will show:"
    echo "    Host: <ngrok_host>"
    echo "    Port: <ngrok_port>"
    echo ""
    echo "Then run this script on your LOCAL machine:"
    echo "  ./connect_remote_browser.sh <ngrok_host> <ngrok_port> chrome"
    echo ""
    echo "Example:"
    echo "  ./connect_remote_browser.sh 0.tcp.ngrok.io 12345 chrome"
    exit 1
fi

NGROK_HOST=$1
NGROK_PORT=$2
BROWSER=${3:-chrome}
SOCKS_PORT=${4:-1080}

echo "=========================================="
echo "Connecting to remote machine via ngrok"
echo "=========================================="
echo ""
echo "Connection details:"
echo "  Host: $NGROK_HOST"
echo "  Port: $NGROK_PORT"
echo "  SOCKS Proxy Port: $SOCKS_PORT"
echo ""

cleanup() {
    if [ ! -z "$SSH_PID" ]; then
        kill "$SSH_PID" 2>/dev/null
        echo "Proxy stopped"
    fi
    exit
}

trap cleanup SIGINT SIGTERM EXIT

echo "Step 1: Starting SOCKS proxy..."
ssh -p "$NGROK_PORT" -D "$SOCKS_PORT" -N -f "$USER@$NGROK_HOST"

sleep 2
SSH_PID=$(pgrep -f "ssh -p $NGROK_PORT -D $SOCKS_PORT")

if [ -z "$SSH_PID" ]; then
    echo "Error: Failed to start SOCKS proxy" >&2
    echo "Make sure you can SSH to the remote machine" >&2
    exit 1
fi

echo "SOCKS proxy started successfully (PID: $SSH_PID)"
echo ""

echo "Step 2: Launching browser with proxy configuration..."

case "$BROWSER" in
    chrome)
        if command -v google-chrome >/dev/null; then
            google-chrome --proxy-server="socks5://127.0.0.1:$SOCKS_PORT" >/dev/null 2>&1 &
            BROWSER_LAUNCHED=true
        elif command -v chromium >/dev/null; then
            chromium --proxy-server="socks5://127.0.0.1:$SOCKS_PORT" >/dev/null 2>&1 &
            BROWSER_LAUNCHED=true
        elif [ -d "/Applications/Google Chrome.app" ]; then
            /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --proxy-server="socks5://127.0.0.1:$SOCKS_PORT" >/dev/null 2>&1 &
            BROWSER_LAUNCHED=true
        else
            BROWSER_LAUNCHED=false
        fi
        ;;
    firefox)
        if command -v firefox >/dev/null; then
            firefox >/dev/null 2>&1 &
            BROWSER_LAUNCHED=true
        elif [ -d "/Applications/Firefox.app" ]; then
            /Applications/Firefox.app/Contents/MacOS/firefox >/dev/null 2>&1 &
            BROWSER_LAUNCHED=true
        else
            BROWSER_LAUNCHED=false
        fi
        if [ "$BROWSER_LAUNCHED" = true ]; then
            echo "Firefox launched. Configure proxy manually:"
            echo "  Settings > Network Settings > Manual proxy > SOCKS v5 > 127.0.0.1:$SOCKS_PORT"
        fi
        ;;
    edge)
        if command -v microsoft-edge >/dev/null; then
            microsoft-edge --proxy-server="socks5://127.0.0.1:$SOCKS_PORT" >/dev/null 2>&1 &
            BROWSER_LAUNCHED=true
        elif [ -d "/Applications/Microsoft Edge.app" ]; then
            /Applications/Microsoft\ Edge.app/Contents/MacOS/Microsoft\ Edge --proxy-server="socks5://127.0.0.1:$SOCKS_PORT" >/dev/null 2>&1 &
            BROWSER_LAUNCHED=true
        else
            BROWSER_LAUNCHED=false
        fi
        ;;
    *)
        echo "Unknown browser: $BROWSER"
        echo "Available: chrome, firefox, edge"
        exit 1
        ;;
esac

if [ "$BROWSER_LAUNCHED" = false ]; then
    echo "Browser not found. Configure proxy manually:"
    echo "  Chrome/Edge: chrome --proxy-server=\"socks5://127.0.0.1:$SOCKS_PORT\""
    echo "  Firefox: Settings > Network Settings > Manual proxy > SOCKS v5 > 127.0.0.1:$SOCKS_PORT"
fi

echo ""
echo "=========================================="
echo "Ready! You can now access webpages"
echo "=========================================="
echo ""
echo "The proxy is active. All domains are automatically routed through the tunnel."
echo ""
echo "Access your webpage:"
echo "  https://dt-fe-app-rivianos.dev.ue1.dc.goriv.co/order/collision"
echo ""
echo "Or any other URL on the remote intranet:"
echo "  https://any-domain.internal/any/path"
echo ""
echo "Proxy running in background (PID: $SSH_PID)"
echo "Press Ctrl+C to stop the proxy"
echo ""

while true; do
    if ! kill -0 "$SSH_PID" 2>/dev/null; then
        echo "Proxy connection lost"
        break
    fi
    sleep 1
done
