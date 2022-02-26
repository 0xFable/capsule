import code
import os
import pathlib
import subprocess
import sys
from email.mime import base
from multiprocessing.sharedctypes import Value

from capsule.abstractions import ACmd
from capsule.lib.config_handler import get_config
from capsule.lib.logging_handler import LOG

sys.path.append(pathlib.Path(__file__).parent.resolve())

DEFAULT_TESTNET_CHAIN = "bombay-12"


class NewCmd(ACmd):

    CMD_NAME = "new"
    CMD_HELP = "Simple command to create a new cosmwasm smart contract. Unless specified, will use x"
    CMD_USAGE = """
    $ capsule new -p ./<path_to_my_contracts_root> -n my_new_contract
    $ capsule new --path ./<path_to_my_contracts_root> -n my_new_contract
    $ capsule new -p <path_to_my_contracts_root> -n my_new_contract -u <other cosmwasm cargo codegen template>"""
    CMD_DESCRIPTION = "Simple command to create a new cosmwasm smart contract. Unless specified, will use x"

    def initialise(self):
        # Define usage and description
        self.parser.usage = self.CMD_USAGE
        self.parser.description = self.CMD_DESCRIPTION

        # Add any positional or optional arguments here
        self.parser.add_argument("-p", "--package",
                                 type=str,
                                 help="(required) Name of new or path to existing package")

        # Add any positional or optional arguments here
        self.parser.add_argument("-u", "--codeid",
                                 type=str,
                                 default="",
                                 help="URL of your own template to use")

        self.parser.add_argument("-n", "--name",
                                 type=str,
                                 default="",
                                 help="Name of your new smart-contract package")

        self.parser.add_argument("-b", "--branch",
                                 type=str,
                                 default="0.16",
                                 help="Branch/Version of your new smart-contract package")

    def run_command(self, args):
        """
        """
        LOG.info("Starting cargo generate of new package")
        output_dir = os.path.abspath(args.package)
        contract_dir = os.path.join(output_dir, args.name)

        if os.path.exists(contract_dir):
            raise ValueError("Directory exists, use a diff name boss")

        try:
            process = subprocess.run(['cargo', 'generate', '--git', 'https://github.com/CosmWasm/cw-template.git', '--branch',
                                     args.branch, '--name', args.name], cwd=output_dir, check=True, stdout=subprocess.PIPE, universal_newlines=True)
        except subprocess.CalledProcessError as grepexc:
            LOG.info("error code", grepexc.returncode, grepexc.output)
        LOG.info(process.stdout)
        LOG.info("[New Contract] Contract creation finished")
