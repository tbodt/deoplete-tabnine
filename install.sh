#!/usr/bin/env bash
set -o errexit

version=$(curl -sS https://update.tabnine.com/version)

targets='i686-unknown-linux-musl
    x86_64-apple-darwin
    aarch64-apple-darwin
    x86_64-unknown-linux-musl'

echo "$targets" | while read target
do
    cd $(dirname $0)
    path=$version/$target/TabNine
    if [ -f binaries/$path ]; then
        exit
    fi
    echo Downloading version $version $target
    curl https://update.tabnine.com/$path --create-dirs -o binaries/$path
    chmod +x binaries/$path
done
