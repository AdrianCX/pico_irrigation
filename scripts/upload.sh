#!/bin/bash

. $(dirname "$0")/config.sh

if [ -z "$1" ]; then
    echo "Need first paramter to be file to upload"
else
    curl -vvv --data-binary @./"$1" "http://${TARGET_IP}:8080/sys/upload/$(basename $1)"
fi