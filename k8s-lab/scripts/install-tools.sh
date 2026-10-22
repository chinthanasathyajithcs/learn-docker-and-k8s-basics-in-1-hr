#!/usr/bin/env bash
# Installs kind and k9s. Runs once when the devcontainer is created.
set -euo pipefail

KIND_VERSION="v0.24.0"
K9S_VERSION="v0.32.5"
ARCH="$(dpkg --print-architecture)"

sudo curl -fsSL -o /usr/local/bin/kind \
  "https://kind.sigs.k8s.io/dl/${KIND_VERSION}/kind-linux-${ARCH}"
sudo chmod +x /usr/local/bin/kind

curl -fsSL "https://github.com/derailed/k9s/releases/download/${K9S_VERSION}/k9s_Linux_${ARCH}.tar.gz" \
  | sudo tar -xz -C /usr/local/bin k9s

echo 'source <(kubectl completion bash); alias k=kubectl; complete -o default -F __start_kubectl k' >> ~/.bashrc
echo "Tools installed."
