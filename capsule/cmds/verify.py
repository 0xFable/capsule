import asyncio
import base64
import code
import hashlib
import json
import os
import pathlib
import platform
import subprocess
import sys
from email.mime import base

import requests
from terra_sdk.client.lcd import LCDClient
from terra_sdk.core import Coins

from capsule.abstractions import ACmd
from capsule.lib.config_handler import get_config
from capsule.lib.deployer import Deployer
from capsule.lib.logging_handler import LOG

sys.path.append(pathlib.Path(__file__).parent.resolve())

DEFAULT_TESTNET_CHAIN = "bombay-12"
# TODO: This enum is also in deployer, move to one place 
import enum
from enum import auto 
class SupportedChains(enum.Enum):
   TERRA = auto()
   JUNO = auto()
   OSMOSIS = auto()

# TODO: IS there a better way to handle theres network names ? Probably
IS_TERRA = lambda network: network in ["columbus-5", "bombay-12"]
IS_JUNO = lambda network: network in ["juno", "uni"]
class VerifyCmd(ACmd):

    CMD_NAME = "verify"
    CMD_HELP = "Attempt to perform a smart contract verification against a given code id. Attempts to perform a deterministic comparison by compiling the provided contract into an optmized wasm and then comparing its checksum with the code_hash of the provided code ID code object. Note if you are running an M1 Mac or an ARM based machine you will not get perfect matches on verification as most production deployments are done from a Intel based machine."
    CMD_USAGE = """
    $ capsule verify -p ./<path_to_my_contracts_root> -c columbus-5 -i 3
    $ capsule verify --path ./<path_to_my_contracts_root> --chain tequila-0004
    $ capsule verify -p <path_to_my_contracts_root> -c bombay-12 -i 300"""
    CMD_DESCRIPTION = "Helper tool which enables you to perform a Smart Contract Verification (SCV) by providing the path to a single smart-contract repo and providing a code id. The project path is passed either to `cargo run-script optimize` or to a custom docker invocation for ARM64 to create an optmized production wasm of the contract for comparison. The code id is used to query a stored code object's byte_code on the respective chain. Once the byte_code is gathered we get the SHA256 of this to compare to our locally prepared optimized wasm. If the SHA265 of on chain code object matches the SHA256 checksum on the optimized build we have verified the contact. Note: The outputted SHA256 and locally build optimized build will be different on ARM vs Intel. An ARM machine can only really be used to verify images which were built and uploaded from an ARM machine"

    def initialise(self):
        # Define usage and description
        self.parser.usage = self.CMD_USAGE
        self.parser.description = self.CMD_DESCRIPTION

        # Add any positional or optional arguments here
        self.parser.add_argument("-p", "--package",
                                 type=str,
                                 help="(required) Name of new or path to existing package")
        
        # Add any positional or optional arguments here
        self.parser.add_argument("-i", "--codeid",
                                 type=int,
                                 default=0,
                                 help="The code_id to compare the provided contract against")

        self.parser.add_argument("-c", "--chain",
                                 type=str,
                                 default="",
                                 help="(Optional) A chain to deploy too. Defaults to localterra")

        self.parser.add_argument("-n", "--nobuild",
                                 action='store_true',
                                 help="(Optional) Skip the building and go right to comparing the onchain code with your own. This assumes you already ran an optimized build and saves you rebuilding each time you run verify command")


        
        
    def run_command(self, args):
        
        """Schema:
            Read Mnemonic from env as well as host to deploy on 
            any specified chain/account 

            Prepare defaults for the above

            Prepare an optimized build using the appropiate technique 
            If nobuild is provided; skip above and go right to the checksums.txt

            Query the byte_code from the lcd client 

            Prepare a hash of the queried byte_code and compare 

            Return success. 
        """
        LOG.info("Starting verification")
        # Setup the Deployer with its lcd, fcd urls as well as the desired chain.
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        config = asyncio.run(get_config())
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # config = asyncio.run(get_config())
        # # TODO: Review setting up a list of urls in project rather than just depending on settings in config
        chain_url = config.get("networks", {}).get(args.chain, DEFAULT_TESTNET_CHAIN).get("chain_url")
        chain_fcd_url = config.get("networks", {}).get(args.chain, DEFAULT_TESTNET_CHAIN).get("chain_fcd_url")

        # TODO: Validate Init_msg is wellformed json 
        chain_to_use = args.chain or "bombay-12"
        
        deployer = Deployer(client=LCDClient(
            url=chain_url, 
            chain_id=chain_to_use,
            gas_prices=Coins(requests.get(f"{chain_fcd_url}/v1/txs/gas_prices").json())))
    


        contract_dir = os.path.abspath(args.package)
        print(contract_dir)
        # TODO: Refactor into a neater function 
        if not args.nobuild: 
            if platform.uname()[4] == "arm64":
                try:
                    # process = subprocess.run(['docker', 'run', '--rm', '-v', '"$(pwd)":/code',
                    # '--mount', 'type=volume,source="$(basename "$(pwd)")_cache",target=/code/target',
                    # '--mount', 'type=volume,source=registry_cache,target=/usr/local/cargo/registry',
                    # 'cosmwasm/rust-optimizer-arm64:0.12.4'], cwd=contract_dir, check=True, stdout=subprocess.PIPE, universal_newlines=True)

                    process = subprocess.run('docker run --rm -v "$(pwd)":/code \
                            --mount type=volume,source="$(basename "$(pwd)")_cache",target=/code/target \
                            --mount type=volume,source=registry_cache,target=/usr/local/cargo/registry \
                            cosmwasm/workspace-optimizer-arm64:0.12.5', cwd=contract_dir, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)

                    LOG.info(process.stdout)

                except subprocess.CalledProcessError as grepexc:                                                                                                   
                    LOG.info("error code", grepexc.returncode, grepexc.output)
            else:
                try:
                    process = subprocess.run(['cargo','run-script','optimize'], cwd=contract_dir, check=True, stdout=subprocess.PIPE, universal_newlines=True)

                    LOG.info(process.stdout)
                except subprocess.CalledProcessError as grepexc:                                                                                                   
                    LOG.info("error code", grepexc.returncode, grepexc.output)

        # By Default the target chain is terra 
        target_chain = SupportedChains.TERRA
        if IS_JUNO(args.chain):
            target_chain = SupportedChains.JUNO

        code_byte_code = asyncio.run(deployer.query_code_bytecode(chain_url, args.codeid, target_chain=target_chain))

        # Handle the code_byte_code and get a sha 
        on_chain = hashlib.sha256()
        on_chain.update(base64.b64decode(code_byte_code['byte_code']))
        # LOG.info(on_chain.digest())
        # LOG.info(base64.b16encode(on_chain.digest()))
        on_chain_code_sha = base64.b16encode(on_chain.digest())
        # Get the hash from artifacts 
        # TODO: Make less POC and more MVP, what if there are multiple checksums 
        with open(contract_dir+"/artifacts/checksums.txt", "r") as file:
            LOG.info(f"[SHA265 of code with id {args.codeid}] {on_chain_code_sha.lower()}")
            # Simple flag to see if we found a match at all 
            found = False
            for line in file:
                sha_to_compare = line.split("  ")[0].encode()
                contract_name = line.split("  ")[1].encode()
                LOG.debug(f"[SHA265 of code found in artifacts directory with name {contract_name}] {sha_to_compare}")

                if sha_to_compare == on_chain_code_sha.lower():
                    LOG.info("[Verification]: Success. The provided contract wasm matches the provided code ID's byte_code hash")
                    found = True
            
            if not found:
                LOG.info("[Verification]: Failed. The provided contract wasm does not match the provided code ID's byte_code hash")
            LOG.info("[Verification]: Command run finished")

        




    

        
