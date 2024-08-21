#!/bin/bash

if [ -z "$1" ]; then
    echo "open operation requires duration in seconds as first parameter"
else
    . $(dirname "$0")/config.sh
    curl -vvv "http://${TARGET_IP}:8080/api/open/$1"
fi
