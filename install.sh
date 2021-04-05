#!/usr/bin/env bash
set -o errexit

version=$(curl -sS https://update.tabnine.com/bundles/version)
case $(uname -s) in
    'Darwin')
        targets='x86_64-apple-darwin
            aarch64-apple-darwin'
        ;;
    'Linux')
        targets="$(uname -m)-unknown-linux-musl"
        ;;
esac

echo "$targets" | while read target
do
    cd $(dirname $0)
    zip=$version/$target/TabNine.zip
    path=$version/$target/TabNine
    if [ -f binaries/$path ]; then
        exit
    fi
    echo Downloading version $version $target
    curl https://update.tabnine.com/bundles/$zip --create-dirs -o binaries/$zip
    pushd $(dirname binaries/$zip)
    unzip -o TabNine.zip
    chmod +x WD-TabNine TabNine TabNine-deep-local TabNine-deep-cloud
    rm TabNine.zip
    popd
done
