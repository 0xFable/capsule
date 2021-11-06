"""Query command -- Used to perform queries on MultiChain contracts"""
import os
import pathlib
# Used to call docker-compose shell command
import subprocess
import sys
from subprocess import PIPE, STDOUT

# Used to clone localterra repo
import git

from capsule.abstractions import ACmd
from capsule.lib.logging_handler import LOG

sys.path.append(pathlib.Path(__file__).parent.resolve())

DEFAULT_TESTNET_CHAIN = "bombay-12"
DEFAULT_CLONE_PATH = os.path.expanduser(
    os.path.join("~", ".capsule", "localterra-clones"))


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
        LOG.info("Performing query on contract addr {args.address}")


   