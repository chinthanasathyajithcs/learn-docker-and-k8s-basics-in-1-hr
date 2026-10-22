#!/usr/bin/env bash
ready=$(kubectl get deploy healthy -o jsonpath='{.status.readyReplicas}' 2>/dev/null)
[ "${ready:-0}" = "3" ] || { echo "FAIL: healthy should have 3 ready replicas, got ${ready:-0}"; exit 1; }
phase=$(kubectl get pod memhog -o jsonpath='{.status.phase}' 2>/dev/null)
[ "$phase" = "Running" ] || { echo "FAIL: memhog should be Running (raise its memory limit), got '${phase}'"; exit 1; }
cl=$(kubectl get deploy crashloop -o jsonpath='{.status.readyReplicas}' 2>/dev/null)
[ "${cl:-0}" = "1" ] || { echo "FAIL: crashloop should have 1 ready replica (fix it)"; exit 1; }
echo "PASS: all three scenarios fixed"
