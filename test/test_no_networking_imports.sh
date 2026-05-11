#!/bin/bash
# test_no_networking_imports.sh — exercises LZ-005 (Apple Vision
# local-only).
#
# Grep-lints the face-comparison sources (face_compare.swift +
# face_sentinel.py) for any networking-symbol substrings. If
# any appear, the local-only claim is violated and the test
# fails.
#
# Honest framing: this is a source-text regression check, not a
# security guarantee. A determined adversary who obfuscates,
# minifies, or dynamically dispatches networking calls could
# bypass the lint. The defensive value is catching accidental
# introduction of network dependencies during refactoring.
#
# Patterns:
#   Swift  — URLSession, URLProtocol, NSURLConnection,
#            import Network, NWConnection, NWListener, CFNetwork
#   Python — import socket / from socket
#            import urllib / from urllib
#            import requests / from requests
#            import http. / from http
#            urlopen
#
# Runs locally on macOS or Linux: bash test/test_no_networking_imports.sh
# Exit 0 on PASS, non-zero on FAIL.

set -u

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FACE_COMPARE_SWIFT="$REPO_ROOT/face_compare.swift"
FACE_SENTINEL_PY="$REPO_ROOT/face_sentinel.py"

if [ ! -f "$FACE_COMPARE_SWIFT" ]; then
    echo "FAIL: $FACE_COMPARE_SWIFT not found"
    exit 1
fi
if [ ! -f "$FACE_SENTINEL_PY" ]; then
    echo "FAIL: $FACE_SENTINEL_PY not found"
    exit 1
fi

# Patterns are extended regex (-E) so we can use alternation.
SWIFT_PATTERNS='URLSession|URLProtocol|NSURLConnection|import[[:space:]]+Network[[:space:]]*$|NWConnection|NWListener|CFNetwork'
PYTHON_PATTERNS='^[[:space:]]*import[[:space:]]+socket([[:space:]]|$)|^[[:space:]]*from[[:space:]]+socket[[:space:]]|^[[:space:]]*import[[:space:]]+urllib|^[[:space:]]*from[[:space:]]+urllib|^[[:space:]]*import[[:space:]]+requests|^[[:space:]]*from[[:space:]]+requests|^[[:space:]]*import[[:space:]]+http\.|^[[:space:]]*from[[:space:]]+http[[:space:]]|urlopen'

FAIL=0

SWIFT_HITS=$(grep -nE "$SWIFT_PATTERNS" "$FACE_COMPARE_SWIFT" 2>/dev/null || true)
if [ -n "$SWIFT_HITS" ]; then
    echo "FAIL: networking symbol(s) found in face_compare.swift:"
    echo "$SWIFT_HITS"
    FAIL=1
fi

PY_HITS=$(grep -nE "$PYTHON_PATTERNS" "$FACE_SENTINEL_PY" 2>/dev/null || true)
if [ -n "$PY_HITS" ]; then
    echo "FAIL: networking symbol(s) found in face_sentinel.py:"
    echo "$PY_HITS"
    FAIL=1
fi

if [ "$FAIL" = "1" ]; then
    exit 1
fi

# Positive check: the test only matters if there's substantial source
# to lint. Guard against the case where the files exist but are
# empty / stub-replaced — that would silently pass the negative test.
SWIFT_LINES=$(wc -l < "$FACE_COMPARE_SWIFT" | tr -d ' ')
PY_LINES=$(wc -l < "$FACE_SENTINEL_PY" | tr -d ' ')
if [ "$SWIFT_LINES" -lt 50 ]; then
    echo "FAIL: face_compare.swift has only $SWIFT_LINES lines (expected ≥50)"
    exit 1
fi
if [ "$PY_LINES" -lt 200 ]; then
    echo "FAIL: face_sentinel.py has only $PY_LINES lines (expected ≥200)"
    exit 1
fi

echo "PASS test_no_networking_imports.sh"
