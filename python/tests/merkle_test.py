import unittest
from hexbytes import HexBytes
from helpers.merkle import MerkleTree


class Test(unittest.TestCase):
    def test_gen_merkle_root_one(self):
        tree = MerkleTree([
            "0xbb9c914731A9AA3E222e28d703cf4A4165747572",
            "0x30fc86c1802f67610DA9180D55426c314ae33DF1"
        ])

        self.assertEqual(
            tree.get_root(),
            "0x65a7482ec1e10d14aabb46dce0681c14693fd27e99496b90b88d18d942e69827"
        )

    def test_gen_merkle_root_two(self):
        tree = MerkleTree([
            "0xbb9c914731A9AA3E222e28d703cf4A4165747572",
            "0x30fc86c1802f67610DA9180D55426c314ae33DF1",
            "0x1bF09865467eE989b25b8177801bb14b758CA1EA",
            "0xFCED23957E60AcCc949BF021Ee4e98941c3A6EeA"
        ])

        self.assertEqual(
            tree.get_root(),
            "0x887d282fcf9b1b18f5d5ad073add82bb1f9b5947074f17b049423c43c2edc5eb"
        )

    def test_gen_merkle_root_three(self):
        tree = MerkleTree([
            "0xbb9c914731A9AA3E222e28d703cf4A4165747572",
            "0x30fc86c1802f67610DA9180D55426c314ae33DF1",
            "0x1bF09865467eE989b25b8177801bb14b758CA1EA",
            "0xFCED23957E60AcCc949BF021Ee4e98941c3A6EeA",
            "0xbE51f9928E498D018C18940FD1EbDBB04F493a45",
            "0x4Ee1279a8B1b553c25E008222A25e7FAb6feD1Df"
        ])
        self.assertEqual(
            tree.get_root(),
            "0x4c7b502da67f50d75e1ffdc8e9230f0766908a4f4bec41425c476992e175e539"
        )

    def test_gen_merkle_root_tour(self):
        tree = MerkleTree([
            "0xbb9c914731A9AA3E222e28d703cf4A4165747572",
            "0x30fc86c1802f67610DA9180D55426c314ae33DF1",
            "0x1bF09865467eE989b25b8177801bb14b758CA1EA",
            "0xFCED23957E60AcCc949BF021Ee4e98941c3A6EeA",
            "0xbE51f9928E498D018C18940FD1EbDBB04F493a45",
            "0x4Ee1279a8B1b553c25E008222A25e7FAb6feD1Df",
            "0x7d95dc520960c65cfd484c2b8a1Ca98f358dEe97"
        ])
        self.assertEqual(
            tree.get_root(),
            "0x3271eb7121b96c005fe3235f211b442a92f491c4c067e249e0ae0af655c96937"
        )

    def test_gen_merkle_root_tour(self):
        v = [
            "0xbb9c914731A9AA3E222e28d703cf4A4165747572",
            "0x30fc86c1802f67610DA9180D55426c314ae33DF1",
            "0x1bF09865467eE989b25b8177801bb14b758CA1EA",
            "0xFCED23957E60AcCc949BF021Ee4e98941c3A6EeA",
            "0xbE51f9928E498D018C18940FD1EbDBB04F493a45",
            "0x4Ee1279a8B1b553c25E008222A25e7FAb6feD1Df",
            "0x7d95dc520960c65cfd484c2b8a1Ca98f358dEe97"
        ]

        tree = MerkleTree(v)
        self.assertEqual(
            tree.get_root(),
            "0x3271eb7121b96c005fe3235f211b442a92f491c4c067e249e0ae0af655c96937"
        )

        proof = [
            [
                '0x12c17dcd8b8eac48894f491746f44bf8c8bdeab97b0fb42780d032af6a9bae74',
                '0x17a23e9275f7628e4fca74944437191dbe7a95cc9cefa865bfb3d54321ec7e00',
                '0xf8cd45cad8572d8dd0300ec8dee54aa2a3dcf7565c0c875234c779a04370c686'
            ],
            [
                '0x827ab251e8cf1433dd27f54b8a3d98174056749dd3ff67ecac0837e5f6cb3cd0',
                '0x17a23e9275f7628e4fca74944437191dbe7a95cc9cefa865bfb3d54321ec7e00',
                '0xf8cd45cad8572d8dd0300ec8dee54aa2a3dcf7565c0c875234c779a04370c686'
            ],
            [
                '0x64c3d348b53464e4cd091fb28a52c2a9d9026fd7be0177e8a58c18e9a1dd2698',
                '0x65a7482ec1e10d14aabb46dce0681c14693fd27e99496b90b88d18d942e69827',
                '0xf8cd45cad8572d8dd0300ec8dee54aa2a3dcf7565c0c875234c779a04370c686'
            ],
            [
                '0xe4207a74cd8eafd52a57d95be9c2397a1b33bcecba12442195705d441444b3a9',
                '0x65a7482ec1e10d14aabb46dce0681c14693fd27e99496b90b88d18d942e69827',
                '0xf8cd45cad8572d8dd0300ec8dee54aa2a3dcf7565c0c875234c779a04370c686'
            ],
            [
                '0xed2f78721594402e6757f4d5d8b491cc6f06c10d6cd3a99803db3f8932d36c4d',
                '0x8ac28980a9a848e172c74c57e2f7fff64e73c75799da7e619372ff3173c3be69',
                '0x887d282fcf9b1b18f5d5ad073add82bb1f9b5947074f17b049423c43c2edc5eb'
            ],
            [
                '0x2a06ae5e04fb1513e75d6fe541e3a39bfedca64b209a6c1016bc4af2cc3fa883',
                '0x8ac28980a9a848e172c74c57e2f7fff64e73c75799da7e619372ff3173c3be69',
                '0x887d282fcf9b1b18f5d5ad073add82bb1f9b5947074f17b049423c43c2edc5eb'
            ],
            [
                '0xfc4778b67ab8597a9c5d25e5e0062db02ed226352720db0d70b19c06a333ddf7',
                '0x887d282fcf9b1b18f5d5ad073add82bb1f9b5947074f17b049423c43c2edc5eb'
            ]
        ]

        for i, _ in enumerate(v):
            p = tree.get_proof(i)
            self.assertEqual(p, proof[i])


if __name__ == '__main__':
    unittest.main()
