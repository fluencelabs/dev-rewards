#!/usr/bin/env python
import base64
import json
import os
import sys
import subprocess
from web3 import Web3
from pathlib import Path
from eth_account.messages import encode_defunct
from web3.auto import w3
from helpers.common import Metadata
from helpers.merkle import MerkleTree

SSH_KEYS_DIR = os.path.join(Path.home(), ".ssh")
BIN_DIR= os.path.join(os.getcwd(), "./bin")
IGNORED_SSH_DIR_FILES = ['.DS_Store']

# Set PATH for python to find age
env = os.environ.copy()
env["PATH"] = BIN_DIR + os.pathsep + env["PATH"]

def error(msg):
    print(f"\033[31m{msg}\033[0m")
    sys.exit(1)


def parse_metadata(filename):
    with open(filename, 'r') as f:
        return Metadata.from_json(f.read())


def ask_user_info(metadata):
    username = input(
        "Enter your github username so we can check if you are participating in the airdrop:\n")
    if username not in metadata.encryptedKeys:
        error("This Github account is not eligible for claiming")

    ethereumAddress = input(
        '''
Ethereum wallet address is necessary to generate a proof that you will send through our web page.
\033[33mImportant notice: you need to make a claim transaction from the entered address!\033[0m

Enter the ethereum address to which you plan to receive the airdrop:
''')

    if not Web3.is_address(ethereumAddress):
        error("You entered an incorrect Ethereum address")

    return (username, ethereumAddress)


def choose_ssh_key():
    files = []
    try:
        files = os.listdir(SSH_KEYS_DIR)
    except FileNotFoundError:
        pass

    sshKeys = []
    for f in files:
        if f in IGNORED_SSH_DIR_FILES:
            continue

        path = os.path.join(SSH_KEYS_DIR, f)
        if not is_ssh_key(path):
            continue
        sshKeys.append(path)

    if len(sshKeys) > 0:
        print(f"\nYour ssh keys in ~/.ssh:")
        for key in sshKeys:
            print(key)

    sshKeyPath = input(
        '''
Now the script needs your ssh key to generate proof. Please, enter path for github SSH key:
''')
    pubKeyPath = sshKeyPath + ".pub"

    if not os.path.exists(sshKeyPath):
        error("Specified file does not exits")
    elif not is_ssh_key(sshKeyPath):
        error("Specified file is not a SSH private key")
    elif not os.path.isfile(pubKeyPath) or not os.path.exists(pubKeyPath):
        error(
            f"SSH public key ({pubKeyPath}) does not exist in current directory")

    pubKey = ""
    with open(pubKeyPath, 'r') as pubKeyFile:
        pubKey = " ".join(pubKeyFile.read().split(" ")[0:2])

    return pubKey.strip(), sshKeyPath


def is_ssh_key(path):
    if not os.path.isfile(path):
        return False

    with open(path, 'r') as file:
        try:
            key = file.read()
            return key.startswith("-----BEGIN")
        except Exception as e:
            print("Couldn't read the file:", file, "Reason:", e)
            return False


def decrypt_temp_eth_account(sshPubKey, sshPrivKey, username, metadata):
    if sshPubKey not in metadata.encryptedKeys[username]:
        error("Specified SSH key is not eligible for claiming. Only RSA and Ed25519 keys added before our Github snapshot are supported for proof generation.")

    data = metadata.encryptedKeys[username][sshPubKey]
    result = subprocess.run(["age",
                             "--decrypt",
                             "--identity",
                             sshPrivKey],
                            capture_output=True,
                            input=data.encode(),
                            env=env)
    if result.returncode != 0:
        age_stderr = result.stderr.replace('https://filippo.io/age/report', 'https://fluence.chat')
        raise OSError(age_stderr)

    return w3.eth.account.from_key(result.stdout.decode())


def get_merkle_proof(metadata, tempETHAccount):
    address = tempETHAccount.address.lower()
    if address not in metadata.addresses:
        raise ValueError("Invalid temp address")

    tree = MerkleTree(metadata.addresses)
    index = metadata.addresses.index(address)
    return index, tree.get_proof(index)


def main():
    metadataPath = "metadata.json"
    if not os.pathh.exists(metadataPath):
        os.system(
            "curl https://fluence-dao.s3.eu-west-1.amazonaws.com/metadata.json > metadata.json"
        )
    metadata = parse_metadata(metadataPath)

    print('''
Welcome to the proof generation script for Fluence Developer Reward Airdrop.
5% of the FLT supply is allocated to ~110,000 developers who contributed into open source web3 repositories during last year.
Public keys of selected Github accounts were added into a smart contract on Ethereum. Claim your allocation and help us build the decentralized internet together!

Check if you are eligible and proceed with claiming
''')

    username, receiverAddress = ask_user_info(metadata)
    sshPubKey, sshKeyPath = choose_ssh_key()
    tempETHAccount = decrypt_temp_eth_account(
        sshPubKey, sshKeyPath, username, metadata
    )
    index, merkleProof = get_merkle_proof(metadata, tempETHAccount)
    base64MerkleProof = base64.b64encode(
        json.dumps(merkleProof).encode()
    ).decode()

    sign = tempETHAccount.sign_message(encode_defunct(hexstr=receiverAddress))

    print("\nSuccess! Copy the line below and paste it in the fluence airdrop website.")
    print(f"{index},{tempETHAccount.address.lower()},{sign.signature.hex()},{base64MerkleProof}")


if __name__ == '__main__':
    main()
