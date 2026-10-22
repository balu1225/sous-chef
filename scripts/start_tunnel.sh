#!/usr/bin/env bash
# Starts a quick, public Cloudflare HTTPS tunnel exposing the Sous-Chef server on port 8000.
# The resulting https://*.trycloudflare.com URL can be plugged directly into Alexa Developer Console.
set -euo pipefail

PORT="${KITCHEN_PORT:-8000}"

echo "=========================================================="
echo " Starting Cloudflare Tunnel for Alexa+ / FastMCP Server"
echo " Local Target: http://127.0.0.1:${PORT}"
echo "=========================================================="

if command -v cloudflared &> /dev/null; then
    CLOUDFLARED_BIN="cloudflared"
elif [ -f "/opt/homebrew/bin/cloudflared" ]; then
    CLOUDFLARED_BIN="/opt/homebrew/bin/cloudflared"
else
    echo "Error: cloudflared is not installed or not in PATH."
    exit 1
fi

"$CLOUDFLARED_BIN" tunnel --url "http://127.0.0.1:${PORT}"
