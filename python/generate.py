#!/usr/bin/env python

import base64
import csv
import argparse
import dataclasses
import os
import subprocess
import secrets
import json
from turtle import st
from helpers.merkle import MerkleTree
from eth_account import Account
from helpers.common import Metadata
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519
from cryptography.hazmat.backends import default_backend
import csv
import cryptography.exceptions as exceptions

DEFAULT_OUTPUT_DIR = os.path.join(os. getcwd(), "output")
DEFAULT_FRACTION = 1000


@dataclasses.dataclass
class User:
    name: str
    pubKey: str


def validate_key(key: str):
    try:
        public_key = serialization.load_ssh_public_key(
            key.encode(),
            backend=default_backend()
        )
    except exceptions.UnsupportedAlgorithm as e:
        return False
    except ValueError as e:
        return False

    if isinstance(public_key, rsa.RSAPublicKey):
        if public_key.key_size < 2048:
            return False
        return True
    elif isinstance(public_key, ed25519.Ed25519PublicKey):
        return True
    else:
        return False


def read_csv(filename):
    users = []
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        i = 1
        totalInvalidCount = 0
        totalSkippedCount = 0
        for row in reader:
            print(
                f"Progress: {i} valid, {totalSkippedCount} skipped, {totalInvalidCount} invalid keys",
                end="\r")

            if len(row) != 2:
                totalSkippedCount += 1
                continue

            is_valid = validate_key(row[1])
            if not is_valid:
                totalInvalidCount += 1
                continue

            i += 1
            users.append(User(name=row[0], pubKey=row[1]))

    print(f"Total skipped keys: {totalSkippedCount}")
    print(f"Total invalid keys: {totalInvalidCount}")
    return users


def gen_eth_keys(users):
    addresses = []
    privateKeys = {}

    i = 0
    fraction001 = int(len(users) / DEFAULT_FRACTION)
    for user in users:
        username = user.name
        privateKey = privateKeys.get(username)

        print(f"Progress: {(i / fraction001 / 10):.2f}%", end="\r")

        i += 1
        if privateKey is not None:
            continue

        privateKey = "0x" + secrets.token_hex(32)
        privateKeys[username] = privateKey
        addresses.append(Account.from_key(privateKey).address.lower())

    return addresses, privateKeys


def encrypt_data_with_ssh(data, sshPubKey):
    result = subprocess.run(["age",
                             "--encrypt",
                             "--recipient",
                             sshPubKey,
                             "-o",
                             "-",
                             "--armor"],
                            capture_output=True,
                            input=data.encode(),
                            env=env)
    if result.returncode != 0:
        raise OSError(result.stderr)
    return result.stdout.decode()


def random_sort(addresses):
    length = len(addresses)

    for i in range(length):
        j = secrets.randbelow(length)
        addresses[i], addresses[j] = addresses[j], addresses[i]


def encrypt_for_standart_output(users, privateKeys):
    encryptedKeys: dict[str, dict[str, str]] = {}

    fraction001 = int(len(users) / DEFAULT_FRACTION)
    i = 0
    totalFailedCount = 0
    for user in users:
        username = user.name
        sshPubKey = user.pubKey
        privateKey = privateKeys[username]

        print(f"Progress: {(i / fraction001 / 10):.2f}%", end="\r")
        i += 1

        try:
            encrypted_data = encrypt_data_with_ssh(
                privateKey, sshPubKey
            )
            if username not in encryptedKeys:
                encryptedKeys[username] = {}

            encryptedKeys[username][sshPubKey] = encrypted_data
        except OSError as e:
            totalFailedCount += 1
            print(f"Failed to encrypt key for {username} with {sshPubKey}")
            print(e)

    return encryptedKeys


def encrypt_for_sh_output(tree, users, addresses, privateKeys):
    encryptedKeys = {}
    indexes = {}

    for i in range(len(addresses)):
        indexes[addresses[i]] = i

    fraction001 = int(len(addresses) / DEFAULT_FRACTION)
    i = 0
    for user in users:
        username = user.name
        sshPubKey = user.pubKey
        privateKey = privateKeys[username]
        address = Account.from_key(privateKeys[username]).address.lower()

        print(f"Progress: {(i / fraction001 / 10):.2f}%", end="\r")
        i += 1

        if username not in encryptedKeys:
            encryptedKeys[username] = []

        index = indexes[address]

        proof = base64.b64encode(json.dumps(
            tree.get_proof(index)).encode()
        ).decode()

        key = ec.derive_private_key(int(privateKey, base=16), ec.SECP256K1())
        openSSLPrivKey = "0x" + key.private_bytes(
            crypto_serialization.Encoding.DER,
            crypto_serialization.PrivateFormat.TraditionalOpenSSL,
            crypto_serialization.NoEncryption()
        ).hex()

        try:
            encryptedData = encrypt_data_with_ssh(
                f"{index},{address},{openSSLPrivKey},{proof}", sshPubKey)\
                .replace("-----BEGIN AGE ENCRYPTED FILE-----", "")\
                .replace("-----END AGE ENCRYPTED FILE-----", "")
            encryptedKeys[username].append(
                base64.b64decode(encryptedData).hex())
        except OSError as e:
            print(f"Failed to encrypt key for {username} with {sshPubKey}")
            print(e)

    return encryptedKeys


def write_output(filePath, root, addresses, encryptedKeys):
    metadata = Metadata(root=root, addresses=addresses,
                        encryptedKeys=encryptedKeys)

    with open(filePath, 'w') as f:
        json.dump(metadata.to_dict(), f, ensure_ascii=False, indent=4)


def write_output_for_sh_script(filePath, encryptedKeys):
    with open(filePath, 'w') as f:
        writer = csv.writer(f, delimiter=",")
        for username in encryptedKeys:
            for key in encryptedKeys[username]:
                writer.writerow([username, key])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=str)
    parser.add_argument('-o', '--output', type=str, default=DEFAULT_OUTPUT_DIR)

    args = parser.parse_args()
    inputFilePath = args.input
    outputFilePath = args.output

    metadataFilePath = os.path.join(outputFilePath, "metadata.json")
    shOutputFILEPath = os.path.join(outputFilePath, "metadata.bin")

    if not os.path.exists(outputFilePath):
        os.mkdir(outputFilePath)

    print(f"Reading from {inputFilePath}")
    users = read_csv(inputFilePath)

    print(f"Generating keys for {len(users)} users")
    addresses, privateKeys = gen_eth_keys(users)

    print(f"Suffling addresses")
    random_sort(addresses)

    print(f"Generating Merkle tree")
    tree = MerkleTree(addresses)

    write_output(metadataFilePath, tree.get_root(), addresses,
                 encrypt_for_standart_output(users, privateKeys))
    write_output_for_sh_script(shOutputFILEPath, encrypt_for_sh_output(
        tree, users, addresses, privateKeys))

    print(f"Metadata file written to {metadataFilePath}")


if __name__ == '__main__':
    main()
