#!/bin/bash

set -euo pipefail

# Toggle this to true/false to control virtual environment creation
VENV=true

REQUIRED_TOOLS=(
  python3
  pip3
  virtualenv
  checkov
  kustomize
  kubectl
  helm
  git
  jq
)

# Detects the platform package manager
get_package_manager() {
  if command -v apt &>/dev/null; then
    echo "apt"
  elif command -v yum &>/dev/null; then
    echo "yum"
  elif command -v brew &>/dev/null; then
    echo "brew"
  else
    echo "❌ Unsupported platform or missing package manager. Exiting." >&2
    exit 1
  fi
}

# Load the appropriate installer script based on package manager
load_installer() {
  local manager=$1
  case $manager in
    apt)
      source ./install_env_apt.sh
      ;;
    yum)
      source ./install_env_yum.sh
      ;;
    brew)
      source ./install_env_brew.sh
      ;;
    *)
      echo "❌ Unsupported package manager: $manager" >&2
      exit 1
      ;;
  esac
}

check_and_install() {
  local tool=$1
  if ! command -v "$tool" &>/dev/null; then
    echo "🔧 $tool not found. Installing..."
    "install_$tool"
  else
    echo "✅ $tool is already installed."
  fi
}

main() {
  echo "🔍 Detecting package manager..."
  PM=$(get_package_manager)
  echo "📦 Using package manager: $PM"

  echo "📥 Loading installer..."
  load_installer "$PM"

  echo "🔍 Checking and installing required tools..."
  for tool in "${REQUIRED_TOOLS[@]}"; do
    check_and_install "$tool"
  done

  if [ "$VENV" = true ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created in ./venv"
    echo "👉 Activate it using: source ./venv/bin/activate"
  else
    echo "ℹ️ Skipping virtual environment creation (VENV=$VENV)"
  fi

  echo "🎉 Environment setup complete."
}

main "$@"

