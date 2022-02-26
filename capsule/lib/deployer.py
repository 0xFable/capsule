import base64
import json
import requests

from terra_sdk.core import Coins
from terra_sdk.client.lcd import LCDClient, Wallet
from terra_sdk.key.mnemonic import MnemonicKey
from terra_sdk.util.contract import read_file_as_b64, get_code_id, get_contract_address
from terra_sdk.core.auth import StdFee
from terra_sdk.core.wasm import MsgStoreCode, MsgInstantiateContract, MsgExecuteContract
import pathlib
import sys
import requests 
from capsule.lib.credential_handler import get_mnemonic
from capsule.lib.logging_handler import LOG
import asyncio
from capsule.abstractions.ADeployer import ADeployer

sys.path.append(pathlib.Path(__file__).parent.resolve())


class Deployer(ADeployer):
    """Deployer is a simple facade object
    providing an interface towards general deployment
    actions such as sending messages, getting addresses,
    uploading code objects, instantiating them into contracts
    and also executing or querying those contracts
    """

    def __init__(self, client: LCDClient) -> None:
        
        self.client = client
        self.mnemonic = asyncio.run(get_mnemonic())
        LOG.debug(self.mnemonic)
        self.deployer = Wallet(lcd=self.client, key=MnemonicKey(self.mnemonic))
        self.std_fee = StdFee(4000000, "600000uluna")

    async def send_msg(self, msg):
        """send_msg attempts to create 
        and sign a transaction with the provided
        msg and then broadcasts the tx

        """
        tx = self.deployer.create_and_sign_tx(
            msgs=[msg], fee=self.std_fee
        )
        # estimated = self.client.tx.estimate_fee(tx, fee_denoms=["uusd"], msgs=[msg])
        # LOG.info(f'estimated fee: {estimated}')
        return self.client.tx.broadcast(tx)

    async def store_contract(self, contract_name:str, contract_path:str="") -> str:
        """store_contract attempts to 
        gather a given wasm artifact file 
        and upload it to the given chain as a StoredCodeObject
        The storage operation is done using the send_msg helper

        Args:
            contract_name (str): The name of the contract to deploy
            contract_path (str, optional): The path to a wasm contract artifact to deploy. Defaults to "".

        Returns:
            str: The contract storage result is parsed and just the code id of the stored code object is returned
        """
        # If the full path was provided, use it else assume its located in artifacts
        bytes = read_file_as_b64(contract_path if contract_path else f"artifacts/{contract_name}.wasm")
        msg = MsgStoreCode(self.deployer.key.acc_address, bytes)
        contract_storage_result = await self.send_msg(msg)
        LOG.info(contract_storage_result)
        return get_code_id(contract_storage_result)
    
    async def instantiate_contract(self, code_id: str, init_msg:dict) -> str:
        """instantiate_contract attempts to 
        instantiate a code object with an init msg 
        into a live contract on the network. 

        Args:
            code_id (str): The code_id of the stored wasm contract artifact
            init_msg (dict): The init msg to send to setup the contract

        Returns:
            str: The contracts address
        """
        msg = MsgInstantiateContract(
            sender=self.deployer.key.acc_address,
            admin=self.deployer.key.acc_address,
            code_id=code_id,
            init_msg=init_msg
        )

        instantiation_result = await self.send_msg(msg)
       
        LOG.info(instantiation_result)
        return get_contract_address(instantiation_result)
    
    async def execute_contract(self, contract_addr: str, execute_msg, coins = []):
        """Execute a message to perform an action on a given contract, returning the result

        Args:
            contract_addr (str): The contract to execute a msg on 
            execute_msg (dict): The msg to execute on the contract
            coins (list, optional): Coins which may be needed for the execution tx. Defaults to [].

        Returns:
            dict: execution results
        """
        msg = MsgExecuteContract(
            sender=self.deployer.key.acc_address,
            contract=contract_addr,
            execute_msg=execute_msg,
            coins=coins
        )
        exe_result = await self.send_msg(msg)
        LOG.debug(exe_result)
        return exe_result
    
    async def query_contract(self, contract_addr: str, query_msg: dict):
        """Perform a query on a given contract, returning the result

        Args:
            contract_addr (str): The contract to perform the query on 
            query_msg (dict): The query to perform

        Returns:
            dict: Query Result
        """
        LOG.info(f"Query to be ran {query_msg}")
        query_result = self.client.wasm.contract_query(contract_addr, query_msg)
        
        LOG.info(query_result)
        return query_result
    
    async def query_code_id(self, code_id: int):
        """
        """
        LOG.info(f"Query to be ran {code_id}")
        # query_result = self.client.wasm.code_info(code_id)
        # query_two = self.client.wasm._c._get(f"/wasm/codes/{code_id}")

        query_raw = requests.get(f"https://bombay-lcd.terra.dev/wasm/codes/{code_id}").json()
        return query_raw

    async def query_code_bytecode(self, code_id: int):
        """
        """
        LOG.info(f"Query to be ran {code_id}")
        # query_result = self.client.wasm.code_info(code_id)
        # query_two = self.client.wasm._c._get(f"/wasm/codes/{code_id}")
        # TODO: This query is not cross-chain capable 
        query_raw = requests.get(f"https://bombay-lcd.terra.dev/terra/wasm/v1beta1/codes/36374/byte_code").json()
        return query_raw
        

