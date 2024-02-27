**What should be in the merkle tree?**
leaf = (userId, eth_temp_address)

**What should be signed on claim?**
NOTE: Signature should be made with `eth_temp_address` key.
- sender ethereum address
- ???

**Using temporary Ethereum wallet**
1. User takes temporary Ethereum wallet and generates a signature with it.
2. Using her main wallet, user sends a transaction that calls the following method:
devRewardDistributor.claim(
  transferTo = myRealWallet.address,
  delegateTo = famousHumanAddress,
  temporaryAddress = temporaryAddress,
  signature = signature,
  merkleProof
)
This way, user only uses temporaryWallet for generating the signature, and never for actual tx sending.
Now, a question arises on how to create that signature. I know 2 methods:
1. Through Metamask's interactive signTypedData_v3, in browser
1. Or through web3.personal.sign, in browser or in NodeJS CLI
I think that CLI is the most secure way to do that. Anyway, it's possible to decide as we go.
To check that signature, we'll use ECDSA.recover, as done here https://github.com/gitcoinco/governance/blob/d5362d31076e79e76503ff845d8475473b53a3fd/contracts/TokenDistributor.sol#L177-L180

**Counteract web-site highjacking**
On claim, users must sign their actual wallet address with the private key of temporary wallet and include that within proof.
And the Reward Contract must require that msg.sender is the address signed by temporary wallet.
This way, it would be impossible to steal the proof.
That's need in order to counteract web-site highjacking.

**Usernames in file**
It's possible to store encrypted private keys of temporary wallets along GitHub usernames. This will make proof generation way faster since there's no need to go through all the private keys trying to decrypt them. And that wouldn't reveal user's ethereum address cuz temporary wallet is still encrypted.

**Mermaid diagram**

Ref to the [DOC.md](../../contracts/DOC.md)

<details>
  <summary>Local copy</summary>

  ```mermaid
      sequenceDiagram
      title: Figure 2: Reward And Claim Process
  
      participant Fluence
      participant Data
      participant Website
      participant Developer
      participant DevRewardDistributor
  
  
      note right of Fluence: Prepare data
      Fluence ->> Fluence: Generate a temporary KeyPair for each SSH key
      Fluence ->> Data: Dump e2e-encrypted SKs to keys.bin
      Fluence ->> Data: Create MerkleTree from enumerated PKs
      note left of Data: Merkle Tree entry is (user_id, PK)
      Fluence ->> Data: List of all GitHub usernames awarded
      Data ->>+ Website: publish
  
      note left of Developer: Find if eligible and claim
      Developer ->> Website: Auth with GitHub
      Website ->> Website: check if user is among GitHub usernames
      Website ->> Developer: ask to run make_proof.sh
      Developer ->> Developer: run make_proof.sh
      note right of Developer: got Merkle Proof, leaf, signature, PK
      Developer ->> Website: submit Merkle Proof, leaf, signature, PK
      note left of Website: validate data
      Website ->> Website: validate offchain
  
      Website ->> DevRewardDistributor: call DevRewardDistributor.claim
      note right of DevRewardDistributor: user_id has not yet claimed
      note right of DevRewardDistributor: leaf == keccak(user_id, PK)
      note right of DevRewardDistributor: ECDSA.recover(leaf, signature) == PK
      note right of DevRewardDistributor: isValid(Merkle Proof, Merkle Root)
      DevRewardDistributor ->> DevRewardDistributor: FLT.transfer(transferToAddr)
      DevRewardDistributor ->> DevRewardDistributor: FLT.delegate(delegateToAddr)
      DevRewardDistributor ->> DevRewardDistributor: save user_id as claimed
      DevRewardDistributor ->> Website: success
  
      Website ->> Developer: notify that tokens are sent
  ```
</details>
