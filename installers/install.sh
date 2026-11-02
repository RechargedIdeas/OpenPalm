#!/usr/bin/env bash
# OpenPalm installer — auto-downloads and installs dependencies.
# Usage: curl -fsSL https://raw.githubusercontent.com/RechargedIdeas/OpenPalm/main/installers/install.sh | bash
#    or: ./install.sh [--no-deps] [--cpu-only]

set -euo pipefail

NO_DEPS=0
CPU_ONLY=1
PREFIX="${HOME}/.openpalm"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-deps) NO_DEPS=1 ;;
    --with-gpu) CPU_ONLY=0 ;;
    --prefix) PREFIX="$2"; shift ;;
  esac
  shift
done

echo "OpenPalm installer"
echo "  prefix: $PREFIX"
echo "  cpu-only: $CPU_ONLY"

mkdir -p "$PREFIX"

# Detect OS
OS="$(uname -s)"
case "$OS" in
  Linux)  PKG="apt" ;;
  Darwin) PKG="brew" ;;
  *)      echo "Unsupported OS: $OS"; exit 1 ;;
esac

install_deps() {
  echo "Installing dependencies…"
  if [[ "$OS" == "Linux" ]]; then
    sudo apt-get update -qq
    sudo apt-get install -y python3 python3-pip python3-venv git curl
  elif [[ "$OS" == "Darwin" ]]; then
    command -v brew >/dev/null || /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    brew install python git
  fi
}

if [[ "$NO_DEPS" -eq 0 ]]; then
  install_deps
fi

# Clone or update
if [[ -d "$PREFIX/OpenPalm" ]]; then
  echo "Updating existing install…"
  git -C "$PREFIX/OpenPalm" pull --ff-only
else
  echo "Cloning OpenPalm…"
  git clone --depth 1 https://github.com/RechargedIdeas/OpenPalm.git "$PREFIX/OpenPalm"
fi

# Python venv + deps
cd "$PREFIX/OpenPalm/sidecar"
python3 -m venv .venv
source .venv/bin/activate
pip install -q --upgrade pip
if [[ -f requirements.txt ]]; then
  pip install -q -r requirements.txt
else
  pip install -q fastapi uvicorn
fi

# Optional GPU
if [[ "$CPU_ONLY" -eq 0 ]]; then
  pip install -q torch --index-url https://download.pytorch.org/whl/cu121 || echo "GPU deps skipped"
fi

# Launcher
cat > "$PREFIX/openpalm" << 'LAUNCH'
#!/usr/bin/env bash
cd "$HOME/.openpalm/OpenPalm/sidecar"
source .venv/bin/activate
export OPENPALM_CPU_ONLY=1
exec python -m uvicorn harness_sidecar.api.server:app --host 127.0.0.1 --port 8765
LAUNCH
chmod +x "$PREFIX/openpalm"

echo ""
echo "Installed. Run: $PREFIX/openpalm"
echo "Then open http://127.0.0.1:8765"
