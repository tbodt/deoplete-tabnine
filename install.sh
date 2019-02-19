#!/bin/bash -e
#
# Download the latest version of the TabNine binary for UNIX-like operating systems

# Determine client OS
case $(uname -s) in
    "Darwin")
        platform="apple-darwin"
        ;;
    "Linux")
        platform="unknown-linux-gnu"
        ;;
esac
triple="$(uname -m)-$platform"

# Go to folder where this script lives
cd $(dirname $0)

# Get latest binary version number from TabNine server
latest_binary_version=$(curl -sS https://update.tabnine.com/version)

# Declare latest binary path
binary_path=$latest_binary_version/$triple/TabNine

# Check if newest binary exist locally, if it doesn't then download it
if [ ! -f binaries/$binary_path ]; then

    # Inform user that we're now downloading the latest version
    echo "Downloading TabNine $latest_binary_version..."

    # Download latest binary
    curl -sS https://update.tabnine.com/$binary_path --create-dirs -o binaries/$binary_path

    # Set executable permissions on binary
    chmod +x binaries/$binary_path
fi
