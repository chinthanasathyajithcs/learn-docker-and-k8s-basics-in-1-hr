#!/usr/bin/env bash
code=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8081)
if [ "$code" = "200" ]; then echo "PASS: stall sign reachable on :8081"; else echo "FAIL: got HTTP $code"; exit 1; fi
kubectl get secret secret-sauce >/dev/null 2>&1 && echo "PASS: secret-sauce exists" || { echo "FAIL: secret-sauce missing"; exit 1; }
