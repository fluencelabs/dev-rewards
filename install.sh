#!/usr/bin/env bash
set -o errexit -o nounset -o pipefail

BIN_DIR="./bin"
TEMP_DIR="$(mktemp -d)"
OS="$(uname -s)-$(uname -m)"

# cleanup on exit
trap 'cleanup' EXIT INT TERM

# check_program_in_path "program"
check_program_in_path() {
  program="${1}"
  if ! type -p "${program}" &>/dev/null; then
      printf '%s\n' "error: ${program} is not installed."
      printf '%s\n' "Use your package manager to install it."
      exit 1
  fi
}

# check that everything installed
PATH="${PATH}:./bin"
for i in curl tar; do
  check_program_in_path $i
done

cleanup() {
  rm -r ${TEMP_DIR}
}

# metadata "file"
metadata() {
  file="${1}"
  echo "Downloading ${file}"
  if [[ -f ${file} ]]; then
    echo "${file} already exists"
  else
    curl --progress-bar -o "${file}" "https://fluence-dao.s3.eu-west-1.amazonaws.com/${file}"
  fi
}

# setup "name" "url"
setup() {
  name="$1"
  url="$2"
  echo "Downloading ${name} from ${url}"
  curl --progress-bar -L -S -o "${TEMP_DIR}/${name}.tar.gz" "${url}"
  tar xf "${TEMP_DIR}/${name}.tar.gz" -C "${TEMP_DIR}"

  # move all executables to BIN_DIR
  [[ ! -d "${BIN_DIR}" ]] && mkdir "${BIN_DIR}" -p
  find "${TEMP_DIR}" -type f -exec file {} + | grep 'executable' | grep -v 'shell script' | cut -d: -f1 | xargs -I {} mv {} "${BIN_DIR}"
  chmod +x "${BIN_DIR}"/*
}

case "$OS" in
    Linux-x86_64)
        SHA3SUM_URL="https://gitlab.com/kurdy/sha3sum/uploads/95b6ec553428e3940b3841fc259d02d4/sha3sum-x86_64_Linux-1.1.0.tar.gz"
        AGE_URL="https://github.com/FiloSottile/age/releases/download/v1.1.1/age-v1.1.1-linux-amd64.tar.gz"
        ;;
    Darwin-x86_64)
        SHA3SUM_URL="https://gitlab.com/kurdy/sha3sum/uploads/47a60658d30743fba6ea6dd99c48da98/sha3sum-x86_64-AppleDarwin-1.1.0.tar.gz"
        AGE_URL="https://github.com/FiloSottile/age/releases/download/v1.1.1/age-v1.1.1-darwin-amd64.tar.gz"
        ;;
    Darwin-arm64)
        SHA3SUM_URL="https://gitlab.com/kurdy/sha3sum/uploads/47a60658d30743fba6ea6dd99c48da98/sha3sum-x86_64-AppleDarwin-1.1.0.tar.gz"
        AGE_URL="https://github.com/FiloSottile/age/releases/download/v1.1.1/age-v1.1.1-darwin-arm64.tar.gz"
        ;;
    *)
        echo "Error: Unsupported OS ${OS}"
        exit 1
        ;;
esac

setup age "${AGE_URL}"
setup sha3sum "${SHA3SUM_URL}"

metadata metadata.bin
metadata metadata.json
