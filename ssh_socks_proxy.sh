#!/bin/bash

# ssh_socks_proxy.sh - Connect via ngrok SSH and create SOCKS proxy for browser access
# Usage: ./ssh_socks_proxy.sh <ngrok_host> <ngrok_port> [socks_port]

if [ $# -lt 2 ]; then
    echo "Usage: $0 <ngrok_host> <ngrok_port> [socks_port]"
    echo "Example: $0 0.tcp.ngrok.io 12345 1080"
    exit 1
fi

NGROK_HOST=$1
NGROK_PORT=$2

if [ -z "$3" ]; then
    SOCKS_PORT=1080
else
    SOCKS_PORT=$3
fi

USER=$(whoami)

echo "Starting SOCKS proxy on port $SOCKS_PORT"
echo "Connect: ssh -p $NGROK_PORT -D $SOCKS_PORT $USER@$NGROK_HOST"
echo ""
echo "Browser configuration:"
echo "  Chrome/Edge: chrome --proxy-server=\"socks5://127.0.0.1:$SOCKS_PORT\""
echo "  Firefox: Settings > Network Settings > Manual proxy > SOCKS v5 > 127.0.0.1:$SOCKS_PORT"
echo ""
echo "After configuring browser proxy, you can access URLs directly:"
echo "  https://dt-fe-app-rivianos.dev.ue1.dc.goriv.co/order/collision"
echo ""
echo "Press Ctrl+C to stop the proxy"
echo ""

ssh -p "$NGROK_PORT" -D "$SOCKS_PORT" "$USER@$NGROK_HOST"
