# capsule

capsule is a small tool with a simple but noble goal; to make deployment of CosmWasm contracts easier.

Firstly we are targeting [Terra](https://terra.money) as the Sponsor User chain as we build out the capsule tool. Eventually we aim to make capsule one of the tools of choice for deploying CosmWasm contracts on all chains!

[Quick video detailing how it works](https://www.youtube.com/watch?v=swBKSpBrz2c)
## Installation

### Install from pypi

```bash
pip install -i https://test.pypi.org/simple/ capsule
```

We have published the package also under capsule_terra. This is temporary until a final package namespace is chosen.

```bash
pip install -i https://test.pypi.org/simple/ capsule_terra
```

```bash
pip install -i https://test.pypi.org/simple/ capsule_terra
```

### Install locally

Git clone the project and change into its parent directory.

```bash
git clone
cd 
```

Install the project using setup tools.

```bash
python setup.py install
```

Access the tool using the command line.

```bash
capsule -h
```

Note: If you have an issue with the above an the command line tool, depending on your platform you will need to prepare a standard distribution and install that. To do so here is two commands together:

```bash
python setup.py sdist && pip install dist/capsule-0.0.0.tar.gz
```

## Available Commands and Usage

### Deploy

Deploy a given cosm wasm contract artifact to a chain of your choice

```bash
capsule deploy -h
usage: 
    $ capsule deploy -p ./my_contract.wasm -c columbus-5
    $ capsule deploy --path ./artifacts/my_contract.wasm --chain tequila-0004
    $ capsule deploy -p artifacts/capsule_test.wasm -i '{"count":17}' -c bombay-12

Helper tool which enables you to programatically deploy a Wasm contract artifact to a chain as a code object and instantiate it
```

#### Deploy - from contract template to live on testnet

Getting a brand new contract into a main net or even a testnet can seem like a daunting task at first. Here is a simple enough 4 step process to get your contract live with capsule:

- Generate a new contract using a template

```bash
cargo generate --git https://github.com/CosmWasm/cw-template.git --branch 0.16 --name capsule_test
```

- Run the rust-optimizer to make an optimized version of your contract for deployment

```bash
docker run --rm -v "$(pwd)":/code  --mount type=volume,source="$(basename "$(pwd)")_cache",target=/code/target  --mount type=volume,source=registry_cache,target=/usr/local/cargo/registry  cosmwasm/rust-optimizer:0.12.3
```

- Create a capsule config file and set values in it

```bash
touch ~/.capsule/config.toml
```

Capsule config  file example

```toml
[deploy_info]
mnemonic="my mem"
```

- Deploy your contract

```bash
capsule deploy -p artifacts/capsule_test.wasm -i '{"count":17}' -c bombay-12
```

```
usage: 
    $ capsule deploy -p ./my_contract.wasm -c columbus-5
    $ capsule deploy --path ./artifacts/my_contract.wasm --chain tequila-0004
    $ capsule deploy -p artifacts/capsule_test.wasm -i '{"count":17}' -c bombay-12

Helper tool which enables you to programmatically deploy a Wasm contract artifact to a chain as a code object and instantiate it

optional arguments:
  -h, --help            show this help message and exit
  -p PACKAGE, --package PACKAGE
                        (required) Name of new or path to existing package
  -i INITMSG, --initmsg INITMSG
                        (Optional) The initialization message for the contract you are trying to deploy. Must be a json-like str
  -c CHAIN, --chain CHAIN
                        (Optional) A chain to deploy too. Defaults to localterra
```

#### Local - get your own Ganache-CLI for Terra

Helper tool which attempts to git clone the localterra repo and then compose it as services which you can use for local dev env contract testing

- Install needed backing deps

For this one you need to ensure you have both Git and Docker with Docker started and ready to be used. Everything else is handled via python.

- Start up a locaterra instance using the capsule command

```bash
capsule local
```

And boom

- If you wanna spin it down again

```bash
capsule local --down
```

With this level of control there is a bunch of config options that could be exposed here, if you want any pls open an issue!

#### Query - perform queries on smart contracts without wasmd

Helper tool which exposes the ability to perform queries on chain specific contract addresses

```
usage: 
    $ capsule query --contract <addr> --chain=<> --query=<query>

optional arguments:
  -h, --help            show this help message and exit
  -a ADDRESS, --address ADDRESS
                        (required) Contract Address to perform query on
  -q QUERY, --query QUERY
                        (Optional) The query message for the contract you are trying to query. Must be a json-like str
  -c CHAIN, --chain CHAIN
                        (Optional) A chain to deploy too. Defaults to localterra
```

#### Execute - quickly test actions without making scripts

Helper tool which exposes the ability to prepare and sending ExecuteMsg's on chain specific contract addresses

```
usage: 
    $ capsule execute --contract <addr> --chain <chain> --msg <msg>

Helper tool which exposes the ability to prepare and sending ExecuteMsg's on chain specific contract addresses

optional arguments:
  -h, --help            show this help message and exit
  -a ADDRESS, --address ADDRESS
                        (required) Contract Address to perform query on
  -m MSG, --msg MSG     (Optional) The execution message for the contract you are trying to execute an action on. Must be a json-like str
  -c CHAIN, --chain CHAIN
                        (Optional) A chain to deploy too. Defaults to localterra
```

## Configuration

The capsule tool offers the ability to store details you need in a configuration file using the toml format.

The config file by default is located in a capsule specific hidden directory at the home dir level: `~/.capsule`
It is possible also to specify the path to a custom config file using the `CAPSULE_CONFIG_FILE` environment variable.

Something to be explored is also enabling both the Mnemonic and the chain to deploy too as env vars also. If this was to happen the
order of priority would then become Credentials in the environment -> Config file in the environment -> Default or specified config file.
Following this pattern in theory should make this tool very easy to use in CI/CD as a given user can just specify the Mnemonic and chain ID for as secrets in the job for a quick start.

## CI/CD

This project uses Github Actions to perform automatic testing on each push and PR as well as a deployment to both test and prod pypi.

Some notes:
When deploying to pypi, a version number can only be deployed once! All subsequent deployments will get a 400 and the job will fail.

As a procedure we should update the version number when a new deployed build is needed. Or have its patch versions done automatically.

Lastly the production build which pushes to Pypi only works with a tagged commit.