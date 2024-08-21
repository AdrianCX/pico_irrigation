#!/bin/bash

. $(dirname "$0")/config.sh

curl "http://${TARGET_IP}:8080/sys/read/$1"