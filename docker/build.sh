#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

docker build \
    --progress=plain \
    -t terra4mars:latest \
    -f "$SCRIPT_DIR/Dockerfile" \
    "$PROJECT_ROOT"
