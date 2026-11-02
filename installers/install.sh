#!/usr/bin/env bash
# OpenPalm — fully automatic installer.
# Clones, installs deps, starts the server, and opens the browser.
# Usage: curl -fsSL https://raw.githubusercontent.com/RechargedIdeas/OpenPalm/main/installers/install.sh | bash

set -euo pipefail

NO_DEPS=0
CPU_ONLY=1
PREFIX="${HOME}/.openpalm"
PORT=8765

while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-deps) NO_DEPS=1 ;;
    --with-gpu) CPU_ONLY=0 ;;
    --prefix) PREFIX="$2"; shift ;;
  esac
  shift || true
done

echo "OpenPalm — automatic install"
mkdir -p "$PREFIX"

OS="$(uname -s)"
if [[ "$NO_DEPS" -eq 0 ]]; then
  echo "Installing system dependencies…"
  if [[ "$OS" == "Linux" ]]; then
    sudo apt-get update -qq
    sudo apt-get install -y python3 python3-pip python3-venv git curl
  elif [[ "$OS" == "Darwin" ]]; then
    command -v brew >/dev/null || /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    brew install python git
  fi
fi

if [[ -d "$PREFIX/OpenPalm" ]]; then
  git -C "$PREFIX/OpenPalm" pull --ff-only
else
  git clone --depth 1 https://github.com/RechargedIdeas/OpenPalm.git "$PREFIX/OpenPalm"
fi

cd "$PREFIX/OpenPalm/sidecar"
python3 -m venv .venv
source .venv/bin/activate
pip install -q --upgrade pip
if [[ -f requirements.txt ]]; then
  pip install -q -r requirements.txt
else
  pip install -q fastapi uvicorn
fi
if [[ "$CPU_ONLY" -eq 0 ]]; then
  pip install -q torch --index-url https://download.pytorch.org/whl/cu121 || true
fi

# Launcher
cat > "$PREFIX/openpalm" << LAUNCH
#!/usr/bin/env bash
cd "$PREFIX/OpenPalm/sidecar"
source .venv/bin/activate
export OPENPALM_CPU_ONLY=1
exec python -m uvicorn harness_sidecar.api.server:app --host 127.0.0.1 --port $PORT
LAUNCH
chmod +x "$PREFIX/openpalm"

# Start in background
echo "Starting OpenPalm…"
nohup "$PREFIX/openpalm" > "$PREFIX/openpalm.log" 2>&1 &
echo $! > "$PREFIX/openpalm.pid"

# Wait for health
for i in $(seq 1 30); do
  if curl -sf "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

# Open browser
URL="http://127.0.0.1:$PORT"
if command -v xdg-open >/dev/null; then
  xdg-open "$URL" >/dev/null 2>&1 || true
elif command -v open >/dev/null; then
  open "$URL" || true
fi

echo "OpenPalm is running at $URL"
echo "Log: $PREFIX/openpalm.log"
echo "Stop: kill \$(cat $PREFIX/openpalm.pid)"
