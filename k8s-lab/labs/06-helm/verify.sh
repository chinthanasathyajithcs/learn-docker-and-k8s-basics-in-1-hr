#!/usr/bin/env bash
helm status demo >/dev/null 2>&1 || { echo "FAIL: release 'demo' not installed"; exit 1; }
n=$(kubectl get deploy -l app.kubernetes.io/instance=demo -o jsonpath='{.items[0].status.readyReplicas}' 2>/dev/null)
img=$(kubectl get deploy -l app.kubernetes.io/instance=demo -o jsonpath='{.items[0].spec.template.spec.containers[0].image}' 2>/dev/null)
[ "${n:-0}" = "2" ] && echo "$img" | grep -q alpine && echo "PASS: 2 ready replicas of $img" || { echo "FAIL: expected 2 ready replicas of an alpine image, got ${n:-0} of '$img'"; exit 1; }
