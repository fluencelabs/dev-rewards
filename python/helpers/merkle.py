import math
from web3 import Web3


class MerkleTree:
    def __init__(self, accounts):
        self._tree = []
        self._total_depth = 0
        nodes = self._create_leafs(accounts)
        self._gen_tree(nodes)

    def _gen_tree(self, nodes):
        self._tree.append(nodes)
        self._total_depth = math.ceil(math.log(len(nodes), 2))

        while (len(nodes) > 1):
            nodes = self._gen_prev_nodes(nodes)
            self._tree.append(nodes)

    def _gen_prev_nodes(self, nodes):
        newNodes = []
        length = len(nodes)
        for i in range(0, length, 2):
            if length % 2 != 0 and i+1 >= length:
                newNodes.append(nodes[i])
                break

            a = nodes[i]
            b = nodes[i+1]

            if (int.from_bytes(a, byteorder='big') < int.from_bytes(b, byteorder='big')):
                newNodes.append(Web3.keccak(a + b))
            else:
                newNodes.append(Web3.keccak(b + a))

        return newNodes

    def _create_leafs(self, accounts):
        leafs = []
        for i, account in enumerate(accounts):
            leaf = Web3.solidity_keccak(
                ["uint32", "bytes20"],
                [
                    i,
                    account
                ]
            )
            leafs.append(leaf)

        return leafs

    def get_proof(self, index):
        proof = []
        for nodes in self._tree:
            length = len(nodes)

            if length == 1:
                break

            if length % 2 != 0 and index == length-1:
                index = index // 2
                continue

            if (index % 2 == 0):
                proof.append(nodes[index+1].hex())
            else:
                proof.append(nodes[index-1].hex())

            index = index // 2

        return proof

    def get_root(self):
        return (self._tree[self._total_depth][0]).hex()
