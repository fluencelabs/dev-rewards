# Fluence Developer Rewards

# Generate proof (docker)

1. Build docke image

   > `docker build -t dev-reward-script .`

2. If your ssh keys are in ~/.ssh, run the script:

   > `docker run -it -v ~/.ssh:/root/.ssh dev-reward-script`

   If your ssh keys are in other directories, replace {dir_path_for_your_ssh_keys} with your directory path:

   > `docker run -it -v /{dir_path_for_your_ssh_keys}:/root/.ssh dev-reward-script`

# Generate proof (local script)

1. Install cargo

   > https://doc.rust-lang.org/cargo/getting-started/installation.html

2. Install python

   > https://www.python.org/downloads/

3. Install other dependencies

   > `./install.sh`

4. Run python script or bash

   For python:

   > `pip install -r python/requirements.txt`

   > `python3 python/proof.py metadata.json`

   For bash:

   > `./proof-sh/proof.sh`
