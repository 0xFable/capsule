from capsule.abstractions import ACmd

import pathlib
import sys
from capsule.lib.deployer import Deployer
sys.path.append(pathlib.Path(__file__).parent.resolve())


class DeployCmd(ACmd):

    CMD_NAME = "deploy"
    CMD_HELP = "Deploy a wasm contract artifact to a specified Terra Chain"
    CMD_USAGE = """
    $ capsule deploy -p ./my_contract.wasm -c columbus-5
    $ capsule deploy --path ./artifacts/my_contract.wasm --chain tequila-0004"""
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
                                 help="(Optional) The initialisation message for the contract you are trying to deploy. Must be a jsonlike str")

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
        # Setup the Deployer with its lcd, fcd urls as well as the desired chain.
        deployer = Deployer(chain_url='https://lcd.terra.dev', chain_fcd_url='https://fcd.terra.dev', chain_id=args.chain)

        # Attempt to store the provided package as a code object, the response will be a code ID if successful
        stored_code_id = deployer.store_contract(args.package)
        # Instantiate a contract using the stored code ID for our contract bundle
        # and an init msg which will be different depending on the contract.
        instantiation_result = deployer.instantiate_contract(stored_code_id, init_msg=args.initmsg)



    

        
