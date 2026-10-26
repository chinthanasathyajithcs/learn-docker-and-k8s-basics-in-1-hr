#!/usr/bin/env bash
# small-stall: 2 ready cooks on an alpine image (step 6). big-stall: 4 ready cooks (step 3).
helm status small-stall >/dev/null 2>&1 || { echo "FAIL: release 'small-stall' not installed"; exit 1; }
helm status big-stall >/dev/null 2>&1 || { echo "FAIL: release 'big-stall' not installed"; exit 1; }
n=$(kubectl get deploy -l app.kubernetes.io/instance=small-stall -o jsonpath='{.items[0].status.readyReplicas}' 2>/dev/null)
img=$(kubectl get deploy -l app.kubernetes.io/instance=small-stall -o jsonpath='{.items[0].spec.template.spec.containers[0].image}' 2>/dev/null)
[ "${n:-0}" = "2" ] && echo "$img" | grep -q alpine || { echo "FAIL: small-stall should have 2 ready cooks on an alpine image, got ${n:-0} on '$img'"; exit 1; }
big=$(kubectl get deploy -l app.kubernetes.io/instance=big-stall -o jsonpath='{.items[0].status.readyReplicas}' 2>/dev/null)
[ "${big:-0}" = "4" ] || { echo "FAIL: big-stall should have 4 ready cooks, got ${big:-0}"; exit 1; }
echo "PASS: one recipe card, two stalls: small-stall has 2 cooks on $img, big-stall has 4"
