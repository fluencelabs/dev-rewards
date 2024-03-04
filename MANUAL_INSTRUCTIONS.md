# Manual instructions for the paranoid

The following can be done in a Docker container for additional isolation, including disconnecting its network once required components are installed, but is not necessary.

1. Setup and run in Docker (optional)
   - `docker run -ti --rm ubuntu:latest bash` to start a very basic docker container
   - `apt-get update && apt-get dist-upgrade -y`
   - `apt-get install -y golang-go curl xxd` to install Go, curl, and xxd
   - `curl https://sh.rustup.rs -sSf | sh` to install rust
2. `go install filippo.io/age/cmd/age@latest` to install the "age" encryption tool that understands this format (see https://github.com/FiloSottile/age)
3. `~/.cargo/bin/cargo install sha3sum` to install the sha3sum tool with keccak256
4. `curl -LO https://fluence-dao.s3.eu-west-1.amazonaws.com/metadata.bin` to download the metadata file to your current directory
5.  Optional: if running in Docker, disconnect it from the network, on the host: `docker network disconnect bridge <container id>` (use `docker ps` to find the container id)
6. `grep '^githubusername,' metadata.bin (if no output, you are not eligible)
7. Take one of the output lines, minus 'githubusername,' at the begining, this is your encrypted blob in hex
8. `echo <encrypted blob in hex> | xxd -r -p -c 1000 > enc.bin` to convert the hex to binary
9.  If running in Docker, copy your private ssh key inside the docker (e.g. `docker cp path/to/local/private/key/file <container id>:/path/to/private/key/file`, or just use copy/paste in your terminal to a file)
10.  `~/go/bin/age --decrypt --identity <path to private key file> --output dec.bin enc.bin` to decrypt the binary file
11. The file `dec.bin` has one line with 4 comma-separated entries, extract each of them to a variable:
    - `USER_ID=$(cat dec.bin | cut -d, -f1)`
    - `ETH_ADDR=$(cat dec.bin | cut -d, -f2)`
    - `ETH_KEY_SRC=$(cat dec.bin | cut -d, -f3)`
    - `MERKLE_PROOF=$(cat dec.bin | cut -d, -f4)`
12. Create a DER form of the Eth key: `echo -n $ETH_KEY_SRC | xxd -r -p -c 118 > eth_key.der`
13. `openssl ec -inform der -in eth_key.der > eth.key`
14. Prepare a message to sign:
    - Take your ethereum address _without_ the '0x' prefix.
    - `UNSIGNED_MSG="$(echo -n $'\x19Ethereum Signed Message:\n'20 | xxd -p)<your ethereum address without 0x>"`
    - `echo -n "$UNSIGNED_MSG" | xxd -r -p | ~/.cargo/bin/sha3sum -a Keccak256` to get your signed message hash. The first part of this output is your hash, set it as `$HASH`. The short-form of this is (the nbsp separator makes this look odd): `HASH=$(echo -n "$UNSIGNED_MSG" | xxd -r -p | ~/.cargo/bin/sha3sum -a Keccak256 | awk -F $'\xC2\xA0' '{ print $1 }')`
15. With HASH as the hex output of the signed message hash above, `SIGNATURE_HEX=$(echo $HASH | xxd -r -p | openssl pkeyutl -sign -inkey eth.key | xxd -p -c 72)`
16. You now have all elements of your proof, make a CSV form of them: `echo "${USER_ID},${ETH_ADDR},${SIGNATURE_HEX},${MERKLE_PROOF}"`
