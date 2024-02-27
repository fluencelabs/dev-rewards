#!/usr/bin/env bash
set -o errexit -o nounset -o pipefail

if [[ "$OSTYPE" == "darwin"* ]]; then
    SHA3SUM_URL="https://gitlab.com/kurdy/sha3sum/uploads/47a60658d30743fba6ea6dd99c48da98/sha3sum-x86_64-AppleDarwin-1.1.0.tar.gz"
    if [[ $(uname -m) == 'arm64' ]]; then
        AGE_URL="https://github.com/FiloSottile/age/releases/download/v1.1.1/age-v1.1.1-darwin-arm64.tar.gz"
    else
        AGE_URL="https://github.com/FiloSottile/age/releases/download/v1.1.1/age-v1.1.1-darwin-amd64.tar.gz"
    fi
else
    SHA3SUM_URL="https://gitlab.com/kurdy/sha3sum/uploads/95b6ec553428e3940b3841fc259d02d4/sha3sum-x86_64_Linux-1.1.0.tar.gz"
    AGE_URL="https://github.com/FiloSottile/age/releases/download/v1.1.1/age-v1.1.1-linux-amd64.tar.gz"
fi

BIN_DIR="/usr/local/bin"
curl -Lo age.tar.gz $AGE_URL
curl -Lo sha3sum.tar.gz $SHA3SUM_URL
tar xf age.tar.gz
tar xf sha3sum.tar.gz
chmod +x sha3sum
sudo mv age/age age/age-keygen sha3sum $BIN_DIR
rm -f age.tar.gz sha3sum.tar.gz
rm -rf age sha3sum sha3sum.hash

curl -o metadata.bin https://fluence-dao.s3.eu-west-1.amazonaws.com/metadata.bin
