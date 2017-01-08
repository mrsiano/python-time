#!/usr/bin/env bash
APP_DIR=$1

# OSX
# TODO:// iterate files:
for f in `find tests -name '*.py' | awk -F':' '{print $1}'`; do
sed -i '' -e $'s/import/from transResponseTime import measure_time \\\nimport/g' $f
sed -i '' -e $'s/def/@measure_time()\\\n    def/g' $f;
done

#CentOS
# TODO:// we need to add this.