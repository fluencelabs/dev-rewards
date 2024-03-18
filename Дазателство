#!/usr/bin/env bash
set -o errexit -o nounset -o pipefail

# TODO: what about openssl versions? maybe use python for signing?
# TODO: tell user how to install utilities

# This script does the following:
# 1. Ask user for her GitHub username and Ethereum address (eth_addr)
# 2. Negotiate with user which SSH key to use
# 3. Find at least one match of key and encrypted_key that decrypts succesfully
# 4. Decrypt encrypted_key to tmp_eth_key
# 5. Sign sender ethereum address: sign[tmp_eth_key](eth_addr)
# 6. Encode signature (#5) and merkle proof and output result

# keys.bin format (CSV):
# GH UserName,Encrypted[userId,tmp_eth_addr,tmp_eth_key,merkle proof]

trap 'echo GOT IT ; exit 0' SIGTERM

# check_program_in_path "program"
check_program_in_path() {
  program="${1}"
  if ! type -p "${program}" &>/dev/null; then
      printf '%s\n' "error: ${program} is not installed."
      printf '%s\n' "You should run install script first"
      printf '%s\n' "or use your package manager to install it."
      exit 1
  fi
}

# while true; do :; done

# check that everything installed
PATH="./bin:${PATH}"
for i in age base64 sha3sum; do
  check_program_in_path $i
done

SSH_KEYS_DIR="$HOME/.ssh"

ask_ssh_key() {
    SSH_KEYS=()
    # list all files from ~/.ssh, except for *.pub, known_hosts, config and log files (tmux sometimes puts logs there)
    while IFS= read -r -d $'\0'; do
        SSH_KEYS+=("$REPLY")
    done < <(find "$SSH_KEYS_DIR" -mindepth 1 -maxdepth 1 ! -name "*.pub" ! -name "known_hosts*" ! -name "config" ! -name "*.log" -print0)

    select fname in "${SSH_KEYS[@]}"; do
        echo "$fname"
        break
    done
}

WORK_DIR="$(pwd)/__sh_cache__"
DECRYPTED_DATA="$WORK_DIR/decrypted.data"
ETH_KEY_DER="$WORK_DIR/tmp_eth.key.der"
ETH_KEY="$WORK_DIR/tmp_eth.key"
OPENSSL_STDERR="$WORK_DIR/openssl.stderr"
AGE_STDERR="$WORK_DIR/age.stderr"

mkdir -p $WORK_DIR

METADATA_BIN="metadata.bin"
# $# is the number of arguments
if [ $# -gt 1 ]; then
    GITHUB_USERNAME="$1"
    ETHEREUM_ADDRESS="$2"
else
    if [ ! -f "$METADATA_BIN" ]; then
        echo "$METADATA_BIN doesn't exist"
        exit 1
    fi

    printf "\nWelcome to the proof generation script for Fluence Developer Reward Airdrop."
    printf "\n5%% of the FLT supply is allocated to ~110,000 developers who contributed into open source web3 repositories during last year."
    printf "\nPublic keys of selected Github accounts were added into a smart contract on Ethereum. Claim your allocation and help us build the decentralized internet together!"
    printf "\n"
    printf "\nCheck if you are eligible and proceed with claiming"

    read -r -p "Enter your github username so we can check if you are participating in the airdrop: " GITHUB_USERNAME

    printf "\nEthereum wallet address is necessary to generate a proof that you will send through our web page."
    printf "\n\033[33mImportant notice: you need to make a claim transaction from the entered address!\033[0m\n\n"

    read -r -p "Enter the ethereum address to which you plan to receive the airdrop: " ETHEREUM_ADDRESS

    STR_LENGTH=$(echo "$ETHEREUM_ADDRESS" | sed -e 's/^0x//' | awk '{ print length }')
    if [ "$STR_LENGTH" -ne 40 ]; then
        echo "$ETHEREUM_ADDRESS is not an Ethereum address. Must be of 40 or 42 (with 0x) characters, was $STR_LENGTH chars"
        exit 1
    fi
    NON_HEX_BYTES_LENGTH=$(echo "$ETHEREUM_ADDRESS" | sed -e 's/^0x//' | tr -d "[:xdigit:]" | awk '{ print length }')
    if [ "$NON_HEX_BYTES_LENGTH" -ne 0 ]; then
        echo "$ETHEREUM_ADDRESS is not an Ethereum address. Must be hexadecimal, has non-hexadecimal symbols."
        exit 1
    fi
fi

KEY_ARG_PATH=''
if [ $# -gt 2 ]; then
    KEY_ARG_PATH="$3"
fi

ENCRYPTED_KEYS=()
while IFS='' read -r line; do ENCRYPTED_KEYS+=("$line"); done < <(grep -i "^${GITHUB_USERNAME}," "${METADATA_BIN}" || true)

# ${#ENCRYPTED_KEYS[@]} -- calculates number of elements in the array
if [ ${#ENCRYPTED_KEYS[@]} -gt 1 ]; then
    echo "Found ${#ENCRYPTED_KEYS[@]} encrypted keys for your GitHub username. That means you have several SSH keys published on GitHub"
#    echo "Any of your keys would work. We have encrypted a temporary keypair for each of your SSH keys."
elif [ ${#ENCRYPTED_KEYS[@]} -gt 0 ]; then
    echo "Found an encrypted key for your GitHub username"
else
    echo "This'$GITHUB_USERNAME' Github account is not eligible for claiming"
    exit 1
fi

printf "\n\tNOTE: your SSH key is used ONLY LOCALLY to decrypt a message and generate Token Claim Proof."
printf "\n\tScript will explicitly ask your consent before using the key."
printf "\n\tIf you have any technical issues, take a look at $OPENSSL_STDERR and $AGE_STDERR files and report to https://fluence.chat \n\n"

printf "Now the script needs your ssh key to generate proof. \n"

while true; do
    if [ -n "$KEY_ARG_PATH" ] && [ -f "$KEY_ARG_PATH" ]; then
        KEY_PATH=$KEY_ARG_PATH
    else
        if [ -d "$SSH_KEYS_DIR" ]; then
            # shellcheck disable=SC2162 # user can have spaces in the path to ssh key and use backslashes to escape them
            read -p "Enter path to the private SSH key to use or just press Enter to show existing keys: " KEY_PATH
            if [ -z "$KEY_PATH" ]; then
                KEY_PATH=$(ask_ssh_key)
            fi
        else
            # shellcheck disable=SC2162 # user can have spaces in the path to ssh key and use backslashes to escape them
            read -p "Enter path to the private SSH key to use: " KEY_PATH
            if [ -z "$KEY_PATH" ]; then
                continue
            fi
        fi

        if ! [ -f "$KEY_PATH" ]; then
            echo "Specified $KEY_PATH  file does not exits or not a SSH private key"
            continue
        fi

        read -p "Will use SSH key to generate proof data. Press enter to proceed. "
        printf "\n"
    fi

    rm -f "$DECRYPTED_DATA"
    printf "\n"

    for encrypted in "${ENCRYPTED_KEYS[@]}"; do
        # contains encrypted (user_id, eth_tmp_key, merkle proof)
        ENCRYPTED_DATA=$(echo "$encrypted" | cut -d',' -f2)

        set +o errexit
        echo "$ENCRYPTED_DATA" | xxd -r -p -c 1000 | age --decrypt --identity "$KEY_PATH" --output "$DECRYPTED_DATA" 2>$OPENSSL_STDERR
        exit_code=$?
        set -o errexit

        if [ $exit_code -ne 0 ]; then
            continue
        else
            break
        fi
    done

    if [ -e "$DECRYPTED_DATA" ]; then
        # echo "Decrypted succesfully! Decrypted data is at $DECRYPTED_DATA"
        break
    else
        echo "Couldn't decrypt with that SSH key, please choose another one."
        echo "Possible causes are:"
        echo "You have specified the file which doesn't contain valid private key."
        echo "Your private key doesn't match your public key in GitHub. It could happen if you've changed local ssh key recently."
        echo "Internal ape error:"
        cat $OPENSSL_STDERR
    fi
done

## Prepare real ethereum addres to be hashed and signed
ETH_ADDR_HEX_ONLY=$(echo -n "$ETHEREUM_ADDRESS" | sed -e 's/^0x//')
# length of ETH key is always 20 bytes
LENGTH="20"
PREFIX_HEX=$(echo -n $'\x19Ethereum Signed Message:\n'${LENGTH} | xxd -p)
DATA_HEX="${PREFIX_HEX}${ETH_ADDR_HEX_ONLY}"

## '|| true' is needed to work around this bug https://gitlab.com/kurdy/sha3sum/-/issues/2
HASH=$(echo -n "$DATA_HEX" | xxd -r -p | (sha3sum -a Keccak256 -t || true) | awk -F $'\xC2\xA0' '{ print $1 }')

## Write temporary eth key to file in binary format (DER)
cat "$DECRYPTED_DATA" | cut -d',' -f3 | xxd -r -p -c 118 >"$ETH_KEY_DER"

## Convert secp256k1 key from DER (binary) to textual representation

set +o errexit
openssl ec -inform der -in "$ETH_KEY_DER" 2>$OPENSSL_STDERR >"$ETH_KEY"
exit_code=$?
set -o errexit

if [ $exit_code -ne 0 ]; then
    echo "Failed to parse $ETH_KEY_DER with OpenSSL. Errors below may be relevant."
    echo "==="
    cat $OPENSSL_STDERR
    echo "==="
    exit 1
fi

## Sign hash of the real ethereum address with the temporary one
SIGNATURE_HEX=$(echo "$HASH" | xxd -r -p | openssl pkeyutl -sign -inkey "$ETH_KEY" | xxd -p -c 72)

USER_ID=$(cat "$DECRYPTED_DATA" | cut -d',' -f1)
TMP_ETH_ADDR=$(cat "$DECRYPTED_DATA" | cut -d',' -f2)
MERKLE_PROOF=$(cat "$DECRYPTED_DATA" | cut -d',' -f4)

echo -e "Success! Copy the line below and paste it in the browser.\n"

# userId, tmpEthAddr, signatureHex, merkleProofHex
echo "${USER_ID},${TMP_ETH_ADDR},${SIGNATURE_HEX},${MERKLE_PROOF}"
