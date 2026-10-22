#!/usr/bin/env bash
phase=$(kubectl get pvc logger-data -o jsonpath='{.status.phase}' 2>/dev/null)
[ "$phase" = "Bound" ] || { echo "FAIL: PVC not Bound (got '${phase}')"; exit 1; }
lines=$(kubectl exec deploy/logger -- wc -l /data/log.txt 2>/dev/null | awk '{print $1}')
[ "${lines:-0}" -gt 0 ] && echo "PASS: PVC bound and $lines log lines present" || { echo "FAIL: no data in /data/log.txt"; exit 1; }
