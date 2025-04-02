#!/bin/bash

set -euo pipefail

install_python3() {
  sudo yum install -y python3
}

install_pip3() {
  sudo yum install -y python3-pip
}

install_virtualenv() {
  sudo yum install -y python3-virtualenv || true
  python3 -m ensurepip --upgrade
  python3 -m pip install --upgrade virtualenv
}

install_checkov() {
  pip3 install --upgrade pip
  pip3 install checkov
}

install_kustomize() {
  curl -s https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh | bash
  sudo mv kustomize /usr/local/bin/
}

install_kubectl() {
  cat <<EOF | sudo tee /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=1
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
EOF

  sudo yum install -y kubectl
}

install_helm() {
  curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
}

install_git() {
  sudo yum install -y git
}

install_jq() {
  sudo yum install -y jq
}

