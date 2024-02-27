#!/usr/bin/env bash
set -o errexit -o nounset -o pipefail

if [[ "$OSTYPE" == "darwin"* ]]; then
    if [[ $(uname -m) == 'arm64' ]]; then
        AGE_URL="https://github.com/FiloSottile/age/releases/download/v1.1.1/age-v1.1.1-darwin-arm64.tar.gz"
    else
        AGE_URL="https://github.com/FiloSottile/age/releases/download/v1.1.1/age-v1.1.1-darwin-amd64.tar.gz"
    fi
else
    AGE_URL="https://github.com/FiloSottile/age/releases/download/v1.1.1/age-v1.1.1-linux-amd64.tar.gz"
fi

BIN_DIR="/usr/local/bin"
curl -Lo age.tar.gz $AGE_URL
tar xf age.tar.gz
sudo mv age/age age/age-keygen $BIN_DIR
rm -f age.tar.gz
rm -rf age

curl -o metadata.json https://fluence-dao.s3.eu-west-1.amazonaws.com/metadata.json
