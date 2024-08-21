#!/bin/bash

. $(dirname "$0")/config.sh

curl -X POST -v "http://${TARGET_IP}:8080/sys/restart"