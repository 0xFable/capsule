"""Query command -- Used to perform queries on MultiChain contracts"""
import os
import pathlib
import sys
from capsule.lib.deployer import Deployer
from terra_sdk.client.lcd import LCDClient
from terra_sdk.core import Coins
import requests
import asyncio
import json
from capsule.abstractions import ACmd
from capsule.lib.logging_handler import LOG
from capsule.lib.config_handler import get_networks

sys.path.append(pathlib.Path(__file__).parent.resolve())

DEFAULT_TESTNET_CHAIN = "bombay-12"
DEFAULT_CLONE_PATH = os.path.expanduser(
    os.path.join("~", ".capsule", "localterra-clones"))
DEFAULT_TESTNET_CHAIN = "bombay-12"


class QueryCmd(ACmd):
    """
        Query command -- Used to perform queries on MultiChain contracts
    """

    CMD_NAME = "query"
    CMD_HELP = "Attempt to perform a query on a given contract address."
    CMD_USAGE = """
    $ capsule query --contract <addr> --chain=<> --query=<query>"""
    CMD_DESCRIPTION = "Helper tool which exposes the ability to perform queries on chain specific contract addresses"

    def initialise(self):
        # Define usage and description
        self.parser.usage = self.CMD_USAGE
        self.parser.description = self.CMD_DESCRIPTION

        # Add any positional or optional arguments here
        self.parser.add_argument("-a", "--address",
                                 type=str,
                                 help="(required) Contract Address to perform query on")

        # Add any positional or optional arguments here
        self.parser.add_argument("-q", "--query",
                                type=str,
                                default={},
                                help="(Optional) The query message for the contract you are trying to query. Must be a json-like str")

        self.parser.add_argument("-c", "--chain",
                                 type=str,
                                 default="",
                                 help="(Optional) A chain to deploy too. Defaults to localterra")

    def run_command(self, args):
        """
            
        """
        LOG.info(f"Performing query on contract addr {args.address}")
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
        query_result = asyncio.run(deployer.query_contract(args.address, json.loads(args.query)))
        LOG.info(f"Query Result {query_result} \n\n Query Finished.")
        



   