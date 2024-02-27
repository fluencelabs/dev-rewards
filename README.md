# Fluence Developer Rewards

# Generate proof (docker)

1. Build docke image

   > `docker build -t dev-reward-script .`

2. If your ssh keys are in ~/.ssh, run the script:

   > `docker run -it -v ~/.ssh:/root/.ssh dev-reward-script`

   If your ssh keys are in other directories, replace {dir_path_for_your_ssh_keys} with your directory path:

   > `docker run -it -v /{dir_path_for_your_ssh_keys}:/root/.ssh dev-reward-script`

# Generate proof (local python script)

1. Install cargo

   > https://doc.rust-lang.org/cargo/getting-started/installation.html

2. Install dependencies

   > `./install_for_sh.sh`

3. Run the script

   > `./proof-sh/proof.sh`

# Generate proof (local sh script)

1. Install python

   > https://www.python.org/downloads/

2. Install dependencies

   > `./install_for_sh.sh`

   > `pip install -r python/requirements.txt`

3. Run the script

   > `python3 python/proof.py`
