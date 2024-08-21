#!/bin/bash

for i in $(git diff --name-only | grep src); do
    ./scripts/upload.sh ${i};
done

