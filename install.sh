#!/usr/bin/env bash
set -o errexit

version=$(curl -sS https://update.tabnine.com/version)
case $(uname -s) in
    "Darwin")
        platform="apple-darwin"
        ;;
    "Linux")
        platform="unknown-linux-gnu"
        ;;
esac
triple="$(uname -m)-$platform"

cd $(dirname $0)
path=$version/$triple/TabNine
if [ -f binaries/$path ]; then
    exit
fi
echo Downloading version $version
curl https://update.tabnine.com/$path --create-dirs -o binaries/$path
chmod +x binaries/$path
