import unittest
import hashlib
import csv
import os
import asn1
import shutil
import python.proof as proof
import sys
import json
import secrets
import subprocess
import python.generate as generate
import base64
from unittest import mock
from web3.auto import w3
from eth_account.messages import encode_defunct
from hexbytes import HexBytes
from helpers.common import Metadata
from helpers.merkle import MerkleTree
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend

TEST_FILES_PATH = os.path.join(os. getcwd(), "__test_cache__")
CSV_TEST_PATH = os.path.join(TEST_FILES_PATH, "test.csv")
USERS = ["user_1", "user_2", "user_3"]
USERS_WITH_DOUBLE_KEYS = ["user_4"]
SECOND_KEY_POSTFIX = "_second"

# https://github.com/ethereum/EIPs/blob/master/EIPS/eip-2.md
SECP256K1_N = int(
    0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141
)
SECP256K1_HALF_N = int(
    SECP256K1_N/2
)


def init():
    if (os.path.exists(TEST_FILES_PATH)):
        shutil.rmtree(TEST_FILES_PATH, ignore_errors=False, onerror=None)

    os.mkdir(TEST_FILES_PATH)

    with open(CSV_TEST_PATH, 'w') as f:
        writer = csv.writer(f, delimiter=",")
        for user in USERS:
            pubKey = create_key(user)
            writer.writerow([user, pubKey])

        for user in USERS_WITH_DOUBLE_KEYS:
            pubKey = create_key(user)
            writer.writerow([user, pubKey])

            pubKey = create_key(user + SECOND_KEY_POSTFIX)
            writer.writerow([user, pubKey])
    return


def create_key(name):
    key = rsa.generate_private_key(
        backend=crypto_default_backend(),
        public_exponent=65537,
        key_size=2048
    )
    privateKey = key.private_bytes(
        crypto_serialization.Encoding.PEM,
        crypto_serialization.PrivateFormat.PKCS8,
        crypto_serialization.NoEncryption()
    )

    publicKey = key.public_key().public_bytes(
        crypto_serialization.Encoding.OpenSSH,
        crypto_serialization.PublicFormat.OpenSSH
    )

    with open(os.path.join(TEST_FILES_PATH, name), 'w') as f:
        f.write(privateKey.decode())

    with open(os.path.join(TEST_FILES_PATH, name + ".pub"), 'w') as f:
        f.write(publicKey.decode())

    return publicKey.decode()


def call_generate():
    sys.argv = ["", "--output", f"{TEST_FILES_PATH}",
                os.path.join(TEST_FILES_PATH, "test.csv")]

    generate.main()

    with open(os.path.join(TEST_FILES_PATH, "metadata.json"), "r") as f:
        return hashlib.sha256(f.read().encode('utf-8')).hexdigest()


def call_proof():
    sys.argv = ["", os.path.join(TEST_FILES_PATH, "metadata.json")]
    proof.main()


def call_proof_sh(user, address, keyPath):
    result = subprocess.run([
        "./proof-sh/proof.sh",
        user,
        address,
        os.path.join(TEST_FILES_PATH, "metadata.bin"), keyPath
    ], capture_output=True)
    if result.returncode != 0:
        raise OSError(result)

    return result.stdout.decode()


def assert_error(test, fn, err, msg):
    try:
        fn()
    except err as e:
        test.assertEqual(msg, str(e))
        return

    test.fail("Did not raise the exception")


def parse_print_out(address, print_mock):
    printList = print_mock.call_args_list
    out = printList[len(printList)-1].args[0].split(",")

    index = int(out[0])
    tempAddress = out[1]
    signature = out[2]
    merkleProof = json.loads(str(base64.b64decode(out[3]).decode()))

    return index, tempAddress, signature, merkleProof


def parse_sh_out(out):
    result = out.split('\n')
    result = result[len(result)-2].split(",")

    index = int(result[0])
    tempAddress = result[1]
    asn1Signature = result[2]
    merkleProof = json.loads(str(base64.b64decode(result[3]).decode()))

    return index, tempAddress, asn1Signature, merkleProof


def is_valid_asn1_sign(asn1Sign, tempAddress, address):
    decoder = asn1.Decoder()
    decoder.start(bytes.fromhex(asn1Sign))
    _, value = decoder.read()
    decoder.start(value)
    _, r = decoder.read()
    _, s = decoder.read()

    if (s > SECP256K1_HALF_N):
        s = SECP256K1_N - s

    rs = r.to_bytes(32, "big") + s.to_bytes(32, "big")
    sign = rs + int(27).to_bytes(1, "big")

    one = w3.eth.account.recover_message(
        encode_defunct(hexstr=address), signature=HexBytes(sign)
    ).lower() == tempAddress

    sign = rs + int(28).to_bytes(1, "big")
    two = w3.eth.account.recover_message(
        encode_defunct(hexstr=address), signature=HexBytes(sign)
    ).lower() == tempAddress

    return one or two


def verify_proof(test, index, tempAddress, signature, merkleProof, address, metadata):
    tree = MerkleTree(metadata.addresses)
    proof = tree.get_proof(index)
    test.assertEqual(proof, merkleProof)

    test.assertEqual(proof, merkleProof)
    test.assertEqual(
        w3.eth.account.recover_message(
            encode_defunct(hexstr=address), signature=HexBytes(signature)
        ).lower(),
        tempAddress
    )


def verify_proof_by_user(test, user, address, keyFileName, print_mock, metadata):
    path = os.path.join(TEST_FILES_PATH, keyFileName)
    with mock.patch(
        'builtins.input',
        side_effect=[user, address, path]
    ):
        call_proof()

    index1, tempAddress1, signature1, merkleProof1 = parse_print_out(
        address, print_mock
    )
    verify_proof(
        test,
        index1,
        tempAddress1,
        signature1,
        merkleProof1,
        address,
        metadata
    )

    result = call_proof_sh(user, address, path)
    index2, tempAddress2, asn1Signatrue, merkleProof2 = parse_sh_out(
        result
    )

    test.assertEqual(index1, index2)
    test.assertEqual(tempAddress1, tempAddress2)
    test.assertTrue(
        is_valid_asn1_sign(
            asn1Signatrue, tempAddress1, address
        )
    )
    test.assertEqual(merkleProof1, merkleProof2)


@mock.patch('builtins.print')
class Test(unittest.TestCase):
    @mock.patch('subprocess.run', side_effect=[subprocess.CompletedProcess([], 1, "", "age test error")])
    def test_generate_error(self, print_mock, subprocess_mock):
        assert_error(self, call_generate, OSError, "age test error")
        return

    def test_generate(self, print_mock):
        self.assertNotEqual(call_generate(), call_generate())

    @mock.patch('builtins.input', side_effect=["user_999"])
    def test_proof_user_not_found(self, print_mock, inputMock):
        assert_error(self, call_proof, ValueError, "User not found")

    @mock.patch('builtins.input', side_effect=[USERS[0], "invalidTestAddress"])
    def test_proof_invalid_eth_address(self, print_mock, inputMock):
        assert_error(self, call_proof, ValueError, "Invalid Ethereum address")

    @mock.patch('builtins.input', side_effect=[USERS[0], "0x0000000000000000000000000000000000000006", "key-path"])
    @mock.patch('os.path.exists', side_effect=lambda x: mock.DEFAULT if (x != "key-path") else False)
    def test_proof_file_is_not_exist(self, print_mock, inputMock, pathExistsMock):
        assert_error(self, call_proof, FileNotFoundError, "File is not exist")

    @mock.patch('builtins.input', side_effect=[USERS[0], "0x0000000000000000000000000000000000000006", "key-path"])
    @mock.patch('os.path.exists', side_effect=lambda x: mock.DEFAULT if (x != "key-path") else True)
    @mock.patch('os.path.isfile', side_effect=lambda x: mock.DEFAULT if (x != "key-path") else False)
    def test_proof_file_is_not_ssh_key(self, print_mock, inputMock, pathExistsMock, isFileMock):
        assert_error(self, call_proof, ValueError, "File is not a SSH key")

    def test_proof(self, print_mock):
        metadata = {}
        with open(os.path.join(TEST_FILES_PATH, "metadata.json"), "r") as f:
            metadata = Metadata.from_json(f.read())

        for user in USERS:
            verify_proof_by_user(
                self,
                user,
                secrets.token_bytes(20).hex(),
                user,
                print_mock,
                metadata
            )

        for user in USERS_WITH_DOUBLE_KEYS:
            verify_proof_by_user(
                self,
                user,
                secrets.token_bytes(20).hex(),
                user,
                print_mock,
                metadata
            )
            verify_proof_by_user(
                self,
                user,
                secrets.token_bytes(20).hex(),
                user + SECOND_KEY_POSTFIX,
                print_mock,
                metadata
            )


if __name__ == '__main__':
    init()
    unittest.main()
