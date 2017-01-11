#!/usr/bin/env bash
APP_DIR=$1
# TODO:// grab it via readlink
project_dir=""
# OSX
# TODO:// iterate files:
for f in `find tests -name '*.py' | awk -F':' '{print $1}'`; do
`sed -i '' -e $'s/import/import sys \\\\\\nsys.path.append('$project_dir') ^^^^/' $f`
sed -i '' -e $'s/ ^^^^/\\\nfrom transResponseTime import measure_time ^^^^/' $f
sed -i '' -e $'s/ ^^^^/\\\nimport/' $f
sed -i '' -e $'s/def/@measure_time()\\\n    def/g' $f;
done

#CentOS
# TODO:// we need to add this.