import asyncio
import json
import pathlib
import sys

import requests
from terra_sdk.client.lcd import LCDClient
from terra_sdk.core import Coins

from capsule.abstractions import ACmd
from capsule.lib.config_handler import get_config, get_networks
from capsule.lib.deployer import Deployer
from capsule.lib.logging_handler import LOG

sys.path.append(pathlib.Path(__file__).parent.resolve())

DEFAULT_TESTNET_CHAIN = "bombay-12"

class DeployCmd(ACmd):

    CMD_NAME = "deploy"
    CMD_HELP = "Deploy a wasm contract artifact to a specified Terra Chain"
    CMD_USAGE = """
    $ capsule deploy -p ./my_contract.wasm -c columbus-5
    $ capsule deploy --path ./artifacts/my_contract.wasm --chain tequila-0004
    $ capsule deploy -p artifacts/capsule_test.wasm -i '{"count":17}' -c bombay-12"""
    CMD_DESCRIPTION = "Helper tool which enables you to programatically deploy a Wasm contract artifact to a chain as a code object and instantiate it"

    def initialise(self):
        # Define usage and description
        self.parser.usage = self.CMD_USAGE
        self.parser.description = self.CMD_DESCRIPTION

        # Add any positional or optional arguments here
        self.parser.add_argument("-p", "--package",
                                 type=str,
                                 help="(required) Name of new or path to existing package")
        
        # Add any positional or optional arguments here
        self.parser.add_argument("-i", "--initmsg",
                                 type=str,
                                 default={},
                                 help="(Optional) The initialization message for the contract you are trying to deploy. Must be a json-like str")

        self.parser.add_argument("-c", "--chain",
                                 type=str,
                                 default="",
                                 help="(Optional) A chain to deploy too. Defaults to localterra")


        
        
    def run_command(self, args):
        
        """Schema:
            Read Mnemonic from env as well as host to deploy on 
            any specified chain/account 

            Prepare defaults for the above

            Perform a store call for the wasm contract that was specified

            Verify the contract was stored with a new API call

            Instantiate the code object into a contract 

            Return success. 
        """
        LOG.info("Starting deployment")
        network_info = asyncio.run(get_networks())
        # By default, fall back to a Terra testnet network, in this case the bombay-12 network. This could be anything in theory. But its the best option at the time
        chain_to_use = args.chain or DEFAULT_TESTNET_CHAIN
 
        # # TODO: Review setting up a list of urls in project rather than just depending on settings in config
        chain_url = network_info.get(chain_to_use).get("chain_url")
        chain_fcd_url = network_info.get(chain_to_use).get("chain_fcd_url")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # TODO: Validate Init_msg is wellformed json 

        deployer = Deployer(client=LCDClient(
            url=chain_url, 
            chain_id=chain_to_use,
            gas_prices=Coins(requests.get(f"{chain_fcd_url}/v1/txs/gas_prices").json())))
        # # Attempt to store the provided package as a code object, the response will be a code ID if successful
        stored_code_id = asyncio.run(deployer.store_contract(contract_name="test", contract_path=args.package))
        # Instantiate a contract using the stored code ID for our contract bundle
        # and an init msg which will be different depending on the contract.
        instantiation_result = asyncio.run(deployer.instantiate_contract(stored_code_id, init_msg=json.loads(args.initmsg)))
        LOG.info(f"Successfully deployed contract artifact located at {args.package}. Contract address of instantiated contract is {instantiation_result}")



    

        
