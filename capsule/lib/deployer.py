import base64
import json
import requests

from terra_sdk.core import Coins
from terra_sdk.client.lcd import LCDClient, Wallet
from terra_sdk.key.mnemonic import MnemonicKey
from terra_sdk.util.contract import read_file_as_b64, get_code_id
from terra_sdk.core.auth import StdFee
from terra_sdk.core.wasm import MsgStoreCode, MsgInstantiateContract, MsgExecuteContract

import pathlib
import sys
from capsule.lib.credential_handler import get_mnemonic
from capsule.lib.logging_handler import LOG
import asyncio
sys.path.append(pathlib.Path(__file__).parent.resolve())


class Deployer():
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

    def get_contract_address(instantiation_result):
        """get_contract_address takes a contract result
        and attempts to gather the contract address
        TODO: Refactor to make more general

        Args:
            instantiation_result ([type]): [description]

        Returns:
            str: The contracts address
        """
        log = json.loads(instantiation_result.raw_log)
        
        contract_address = ''
        for entry in log[0]['events'][0]['attributes']:
            if entry['key'] == 'contract_address':
                contract_address = entry['value']
        return contract_address

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
    
    async def instantiate_contract(self, code_id: str, init_msg) -> str:
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
            owner=self.deployer.key.acc_address,
            code_id=code_id,
            init_msg=init_msg
        )
        instantiation_result = await self.send_msg(msg)
       
        LOG.debug(instantiation_result)
        return self.get_contract_address(instantiation_result)
