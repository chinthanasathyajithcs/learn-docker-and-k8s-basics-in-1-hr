#!/usr/bin/env bash
# Creates the lab cluster if it does not already exist. Safe to re-run.
set -euo pipefail

CLUSTER=lab
CONFIG="$(dirname "$0")/../kind-config.yaml"

# Docker-in-Docker can take a few seconds to come up
for _ in $(seq 1 30); do docker info >/dev/null 2>&1 && break; sleep 2; done

if kind get clusters 2>/dev/null | grep -qx "$CLUSTER"; then
  echo "Cluster '$CLUSTER' already exists."
else
  kind create cluster --name "$CLUSTER" --config "$CONFIG"
fi

kubectl cluster-info --context "kind-$CLUSTER"
kubectl get nodes
