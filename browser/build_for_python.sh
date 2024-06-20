#!/bin/bash
set -e
cd `dirname $0`/traceview

npm run build

TARGET_PATH=../../src/nicetrace/html/static

rm -rf ${TARGET_PATH:?}/*
cp -r dist/assets/* ${TARGET_PATH}
git add ${TARGET_PATH}
