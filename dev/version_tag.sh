#!/bin/sh
#

usage() {
    echo "usage: version_tag.sh [-r] tag"
}

if [ $# -eq 0 ]; then
    usage
    exit 1
fi

git checkout master
git merge develop -X theirs

TAG="$1"
if [ "$1" = '-r' ]; then
    TAG="$2"
fi

if ! sed -i "s/^VERSION = '.*$/VERSION = '$TAG'/g" bin/smarthome.py; then
    echo "Could not replace VERSION variable." >&2
    exit 2
fi

#JS=examples/visu/js/smarthome
#if ! sed -i "s/^var shVersion = .*/var shVersion = '$TAG';/g" $JS.js; then
#   echo "Could not replace shVersion variable." >&2
#   exit 2
#fi
#cat $JS.js | grep -v 'console.log' > $JS.tmp.js
#java -jar ./dev/yuicompressor-*.jar $JS.tmp.js -o $JS.min.js --charset utf-8
#rm -f $JS.tmp.js

git add bin/smarthome.py # $JS.js $JS.min.js
git commit -m "set version to $TAG"

echo

git diff master..develop

if [ "$1" = '-r' ]; then
    git tag -a -m "set version to $TAG" "$TAG"
    git push origin tag "$TAG"
    git archive master --prefix='/usr/local/smarthome/' | gzip > release/`git describe master`.tgz
    git archive master --prefix='/usr/local/smarthome/' --format=zip > release/`git describe master`.zip
    echo "Want to remove a tag?"
    echo "git tag -d TAG"
    echo "git push origin :refs/tags/TAG"
    echo
fi
