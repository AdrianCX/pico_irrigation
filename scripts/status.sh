#!/bin/bash

. $(dirname "$0")/config.sh

curl -v "http://${TARGET_IP}:8080/sys/status"