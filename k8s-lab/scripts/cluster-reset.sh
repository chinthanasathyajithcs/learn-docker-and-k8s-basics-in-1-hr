#!/usr/bin/env bash
# Wipes and recreates the lab cluster. Use when students break something.
set -euo pipefail
kind delete cluster --name lab
bash "$(dirname "$0")/cluster-up.sh"
