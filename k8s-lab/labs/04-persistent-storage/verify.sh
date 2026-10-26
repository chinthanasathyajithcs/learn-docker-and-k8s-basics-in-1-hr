#!/usr/bin/env bash
phase=$(kubectl get pvc notebook-locker -o jsonpath='{.status.phase}' 2>/dev/null)
[ "$phase" = "Bound" ] || { echo "FAIL: locker not Bound (got '${phase}')"; exit 1; }
lines=$(kubectl exec deploy/notebook -- wc -l /notebook/visitors.log 2>/dev/null | awk '{print $1}')
[ "${lines:-0}" -gt 0 ] && echo "PASS: locker bound and $lines notebook lines present" || { echo "FAIL: no lines in /notebook/visitors.log"; exit 1; }
