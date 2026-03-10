#!/bin/bash

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
    exit 1
fi

if [ ! -z "$NGROK_AUTH_TOKEN" ]; then
    ngrok config add-authtoken "$NGROK_AUTH_TOKEN" >/dev/null 2>&1
fi

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
echo "Ngrok tunnel established successfully!"
echo "=========================================="
echo ""
echo "IMPORTANT: Copy these connection details to your LOCAL machine"
echo ""
echo "Connection details:"
echo "  Host: $HOST"
echo "  Port: $PORT"
echo "  User: $(whoami)"
echo ""
echo "=========================================="
echo "ON YOUR LOCAL MACHINE - Run this command:"
echo "=========================================="
echo ""
echo "  ./connect_remote_browser.sh $HOST $PORT chrome"
echo ""
echo "This will:"
echo "  1. Connect to this remote machine via ngrok"
echo "  2. Start a SOCKS proxy"
echo "  3. Launch your browser with proxy configured"
echo "  4. Allow you to access webpages automatically"
echo ""
echo "Then open in your browser:"
echo "  https://dt-fe-app-rivianos.dev.ue1.dc.goriv.co/order/collision"
echo ""
echo "=========================================="
echo "ALTERNATIVE: Manual connection"
echo "=========================================="
echo ""
echo "BASIC SSH CONNECTION:"
echo "  From your local machine, run:"
echo "  ssh -p $PORT $(whoami)@$HOST"
echo ""
echo "BROWSER ACCESS (SOCKS Proxy - AUTOMATIC for all domains):"
echo "  This method AUTOMATICALLY routes ALL traffic through SSH:"
echo "  - ALL hostnames are automatically resolved on remote side"
echo "  - NO /etc/hosts configuration needed"
echo "  - Works with ANY domain/hostname automatically"
echo ""
echo "  MANUAL SETUP:"
echo "    1. On your LOCAL machine, start SOCKS proxy:"
echo "       ssh -p $PORT -D 1080 -N -f $(whoami)@$HOST"
echo ""
echo "    2. Configure browser to use SOCKS proxy:"
echo "       - Chrome/Edge: chrome --proxy-server=\"socks5://127.0.0.1:1080\""
echo "       - Firefox: Settings > Network Settings > Manual proxy > SOCKS v5 > 127.0.0.1:1080"
echo ""
echo "    3. Access ANY URL directly - all domains work automatically:"
echo "       https://dt-fe-app-rivianos.dev.ue1.dc.goriv.co/order/collision"
echo "       https://any-other-domain.internal/any/path"
echo ""
echo "BROWSER ACCESS (Port Forwarding):"
echo "  To access remote intranet services in your browser:"
echo "  1. Connect with port forwarding:"
echo "     ssh -p $PORT -L <local_port>:<remote_host>:<remote_port> $(whoami)@$HOST"
echo ""
echo "  2. Open your browser and go to:"
echo "     http://localhost:<local_port>  (for HTTP)"
echo "     https://localhost:<local_port>  (for HTTPS)"
echo ""
echo "EXAMPLES:"
echo "  HTTP Web server (192.168.1.100:80):"
echo "    ssh -p $PORT -L 8080:192.168.1.100:80 $(whoami)@$HOST"
echo "    Then open: http://localhost:8080"
echo ""
echo "  HTTPS Web server (dt-fe-app-rivianos.dev.ue1.dc.goriv.co:443):"
echo "    Option 1 - SOCKS proxy (recommended, no /etc/hosts):"
echo "      ssh -p $PORT -D 1080 $(whoami)@$HOST"
echo "      Configure browser SOCKS proxy to 127.0.0.1:1080"
echo "      Then open: https://dt-fe-app-rivianos.dev.ue1.dc.goriv.co/order/collision"
echo ""
echo "    Option 2 - Port forwarding (requires /etc/hosts or use localhost):"
echo "      ssh -p $PORT -L 8443:dt-fe-app-rivianos.dev.ue1.dc.goriv.co:443 $(whoami)@$HOST"
echo "      Then open: https://localhost:8443/order/collision"
echo ""
echo "  Web service (10.0.0.5:3000):"
echo "    ssh -p $PORT -L 3000:10.0.0.5:3000 $(whoami)@$HOST"
echo "    Then open: http://localhost:3000"
echo ""
echo "  Database (172.16.0.10:5432):"
echo "    ssh -p $PORT -L 5432:172.16.0.10:5432 $(whoami)@$HOST"
echo "    Then connect to: localhost:5432"
echo ""
echo "NOTES:"
echo "  - SOCKS proxy method: No /etc/hosts configuration needed, works with all hostnames"
echo "  - Port forwarding method: Requires /etc/hosts for original hostnames, or use localhost"
echo "  - Keep the SSH connection open while using proxy or port forwarding"
echo "  - For HTTPS, you may need to accept self-signed certificates in your browser"
echo "  - SOCKS proxy port 1080 is standard, but you can use any available port"
echo ""
echo "Press Ctrl+C to stop the ngrok tunnel"
echo ""

while kill -0 "$NGROK_PID" 2>/dev/null; do
    sleep 1
done
