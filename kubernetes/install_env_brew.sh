#!/bin/bash

set -euo pipefail

install_python3() {
  brew install python
}

install_pip3() {
  # Comes with Homebrew Python, ensure pip3 is available
  command -v pip3 &>/dev/null || echo "❌ pip3 should be installed with python3 on brew."
}

install_virtualenv() {
  python3 -m ensurepip --upgrade
  python3 -m pip install --upgrade virtualenv
}

install_checkov() {
  pip3 install --upgrade pip
  pip3 install checkov
}

install_kustomize() {
  brew install kustomize
}

install_kubectl() {
  brew install kubectl
}

install_helm() {
  brew install helm
}

install_git() {
  brew install git
}

install_jq() {
  brew install jq
}