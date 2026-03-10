#!/bin/bash

# ssh_tunnel_browser.sh - Connect via ngrok SSH and forward port for browser access
# Usage: ./ssh_tunnel_browser.sh <ngrok_host> <ngrok_port> <remote_host> <remote_port> [local_port]

if [ $# -lt 4 ]; then
    echo "Usage: $0 <ngrok_host> <ngrok_port> <remote_host> <remote_port> [local_port]"
    echo "Example: $0 0.tcp.ngrok.io 12345 192.168.1.100 80 8080"
    exit 1
fi

NGROK_HOST=$1
NGROK_PORT=$2
REMOTE_HOST=$3
REMOTE_PORT=$4

if [ -z "$5" ]; then
    LOCAL_PORT=$REMOTE_PORT
else
    LOCAL_PORT=$5
fi

USER=$(whoami)

if [ "$REMOTE_PORT" = "443" ]; then
    PROTOCOL="https"
else
    PROTOCOL="http"
fi

echo "Forwarding local port $LOCAL_PORT to $REMOTE_HOST:$REMOTE_PORT via ngrok"
echo "Connect: ssh -p $NGROK_PORT -L $LOCAL_PORT:$REMOTE_HOST:$REMOTE_PORT $USER@$NGROK_HOST"
echo "Then open: $PROTOCOL://localhost:$LOCAL_PORT"
if [ "$REMOTE_PORT" = "443" ]; then
    echo ""
    echo "For HTTPS with original hostname, add to /etc/hosts:"
    echo "  127.0.0.1 $REMOTE_HOST"
    echo "Then open: $PROTOCOL://$REMOTE_HOST:$LOCAL_PORT"
fi
echo ""
echo "Press Ctrl+C to stop the tunnel"
echo ""

ssh -p "$NGROK_PORT" -L "$LOCAL_PORT:$REMOTE_HOST:$REMOTE_PORT" "$USER@$NGROK_HOST"
