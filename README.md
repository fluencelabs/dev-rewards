# Fluence Developer Rewards

# Get proof for web (docker)

1. Build docke image

   > `docker build -t dev-reward-script .`

2. If your ssh keys in ~/.ssh then run script:

> `docker run -it -v ~/.ssh:/root/.ssh dev-reward-script`

    If your ssh key in different directories then replace {dir_path_for_your_ssh_keys} to your directory:

> `docker run -it -v /{dir_path_for_your_ssh_keys}:/{dir_path_for_your_ssh_keys} dev-reward-script`

2. Run script if your ssh keys in ~/.ssh

3. Enter gihub name, receiving wallet address, and `/ssh-key/{your_ssh_key}`

# Get proof for web (local script)

1. Install cargo

   > https://doc.rust-lang.org/cargo/getting-started/installation.html

2. Install python

   > https://www.python.org/downloads/

3. Install other dependencies

   > `./install_utils.sh`

4. Run python script

   > `pip install -r python/requirements.txt --require-hashes`

   > `python3 python/proof.py metadata.json`
