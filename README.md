# Fluence Developer Rewards

This repo allows the one to generate proof signature for Fluence dev reward claiming.

The methods for generating signature are described below:

## Generate proof in docker

1. Build docker image

   > `docker build -t dev-reward-script .`

2. If your ssh keys are in ~/.ssh, run the script:

   > `docker run -it --rm --network none -v ~/.ssh:/root/.ssh:ro dev-reward-script`

   If your ssh keys are in other directories, replace
   {dir_path_for_your_ssh_keys} with your directory path:

   > `docker run -it --rm --network none -v /{dir_path_for_your_ssh_keys}:/root/.ssh:ro dev-reward-script`

## Generate proof via local sh script

1. Install dependencies

   > `./install.sh`

2. Run the script

   > `./proof-sh/proof.sh`

## Generate proof via local python script

1. Install python

   > https://www.python.org/downloads/

2. Install dependencies

   > `./install.sh`

   > `python3 -m venv claim-venv`

   > `source claim-venv/bin/activate`

   > `pip3 install -r python/requirements.txt`

3. Run the script

   > `python3 python/proof.py`

## Notes:

Also check out [paranoid](./MANUAL_INSTRUCTIONS.md) instruction
in case you have any security concerns regarding the methods above.