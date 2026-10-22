#!/usr/bin/env bash
ready=$(kubectl get deploy web -o jsonpath='{.status.readyReplicas}' 2>/dev/null)
if [ "${ready:-0}" = "3" ]; then echo "PASS: web has 3 ready replicas"; else echo "FAIL: expected 3 ready replicas, got ${ready:-0}"; exit 1; fi
