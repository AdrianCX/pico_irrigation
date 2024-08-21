#!/bin/bash

. $(dirname "$0")/config.sh

curl -vvv "http://${TARGET_IP}:8080/$1"
