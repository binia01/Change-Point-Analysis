#!/usr/bin/env bash
# Start both backend and frontend for the Brent Oil Dashboard.
# Usage:  ./start.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "==> Starting Flask backend..."
cd "$SCRIPT_DIR/backend"
pip install -q -r requirements.txt
python app.py &
BACKEND_PID=$!
echo "    Backend PID: $BACKEND_PID  (http://localhost:5050)"

echo "==> Starting React frontend..."
cd "$SCRIPT_DIR/frontend"
if [ ! -d "node_modules" ]; then
  echo "    Installing packages (first run)..."
  pnpm install
fi
pnpm start &
FRONTEND_PID=$!
echo "    Frontend PID: $FRONTEND_PID  (http://localhost:3000)"

echo ""
echo "Dashboard is starting — open http://localhost:3000"
echo "Press Ctrl+C to stop both servers."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
