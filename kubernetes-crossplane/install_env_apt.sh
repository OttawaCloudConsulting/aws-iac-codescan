#!/bin/bash

set -euo pipefail

install_python3() {
  sudo apt-get update -y
  sudo apt-get install -y python3
}

install_pip3() {
  sudo apt-get install -y python3-pip
}

install_virtualenv() {
  sudo apt-get install -y python3-venv
}

install_checkov() {
  pip3 install --upgrade pip
  pip3 install checkov
}

install_kustomize() {
  if ! command -v kustomize &>/dev/null; then
    echo "Installing kustomize from official GitHub binary..."
    curl -s https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh | bash
    sudo mv kustomize /usr/local/bin/
  fi
}

install_kubectl() {
  sudo apt-get install -y apt-transport-https ca-certificates curl
  sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
  echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
  sudo apt-get update -y
  sudo apt-get install -y kubectl
}

install_helm() {
  curl https://baltocdn.com/helm/signing.asc | sudo apt-key add -
  sudo apt-get install -y apt-transport-https --no-install-recommends
  echo "deb https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
  sudo apt-get update -y
  sudo apt-get install -y helm
}

install_git() {
  sudo apt-get install -y git
}

install_jq() {
  sudo apt-get install -y jq
}

