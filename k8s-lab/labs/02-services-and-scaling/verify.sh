#!/usr/bin/env bash
code=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8080)
if [ "$code" = "200" ]; then echo "PASS: service reachable on :8080"; else echo "FAIL: got HTTP $code"; exit 1; fi
