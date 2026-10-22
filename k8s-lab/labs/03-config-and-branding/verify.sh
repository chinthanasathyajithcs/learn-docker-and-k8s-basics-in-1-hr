#!/usr/bin/env bash
code=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8081)
if [ "$code" = "200" ]; then echo "PASS: site reachable on :8081"; else echo "FAIL: got HTTP $code"; exit 1; fi
kubectl get secret site-secret >/dev/null 2>&1 && echo "PASS: site-secret exists" || { echo "FAIL: site-secret missing"; exit 1; }
