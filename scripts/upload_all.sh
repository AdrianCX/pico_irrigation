#!/bin/bash

#for i in $(git diff --name-only | grep src); do
#    ./scripts/upload.sh ${i};
#done

for i in $(find ./src/ -iname *.py); do
    ./scripts/upload.sh ${i};
done