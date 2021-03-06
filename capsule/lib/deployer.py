import asyncio
import base64
import json
import pathlib
import sys

import requests
from terra_sdk.client.lcd import LCDClient, Wallet
from terra_sdk.core import Coins
from terra_sdk.core.fee import Fee as StdFee
from terra_sdk.client.lcd.api.tx import CreateTxOptions

from terra_sdk.core.wasm import (MsgExecuteContract, MsgInstantiateContract,
                                 MsgStoreCode)
from terra_sdk.core.wasm.data import AccessConfig
from terra_proto.cosmwasm.wasm.v1 import AccessType

from terra_sdk.key.mnemonic import MnemonicKey
from terra_sdk.util.contract import (get_code_id, get_contract_address,
                                     read_file_as_b64)

from capsule.abstractions.ADeployer import ADeployer
from capsule.lib.credential_handler import get_mnemonic
from capsule.lib.logging_handler import LOG

sys.path.append(pathlib.Path(__file__).parent.resolve())

import enum
from enum import auto 
class SupportedChains(enum.Enum):
   TERRA = auto()
   JUNO = auto()
   OSMOSIS = auto()

class Deployer(ADeployer):
    """Deployer is a simple facade object
    providing an interface towards general deployment
    actions such as sending messages, getting addresses,
    uploading code objects, instantiating them into contracts
    and also executing or querying those contracts
    """
    
    def __init__(self, client, target_chain: enum.Enum = SupportedChains.TERRA) -> None:
        """__init__ takes only a client which is expected to be an already instantiated LCDClient for a network of your choice.
        By default it is expected you will provide a LCDClient configured for use with the Terra Network as this is the original target network. 
        In the event you want to use this deployer in a multi-chain sense for any other CosmWasm enabled chain you should also provide a different value for the 
        `target_chain` param. Provided the target_chain is a SupportedChain, a relevant chain specific implementation of each of 
        the abstractmethods defined in ADeployer should be provided. 

        Args:
            client (oneOf terra_sdk.client.lcd.LCDClient | OtherClient): An instantiated LCDClient class for the chain you want to use.
            target_chain (enum.Enum, optional): Optional, used only when you want to target a chain other than Terra such as Juno. Defaults to SupportedChains.TERRA.
        """
        self.target_chain = target_chain
        self.client = client
        self.mnemonic = asyncio.run(get_mnemonic())
        self.deployer = Wallet(lcd=self.client, key=MnemonicKey(self.mnemonic))
        # TODO: Use constants here 
        self.std_fee = StdFee(3969390, Coins.from_str("700000uusd"))

    async def send_msg(self, msg):
        """send_msg attempts to create 
        and sign a transaction with the provided
        msg and then broadcasts the tx

        """
        tx = self.deployer.create_and_sign_tx(CreateTxOptions(
            msgs=[msg])
        )
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
        LOG.info(contract_path if contract_path else f"artifacts/{contract_name}.wasm")
        bytes = read_file_as_b64(contract_path if contract_path else f"artifacts/{contract_name}.wasm")
        msg = MsgStoreCode(self.deployer.key.acc_address, bytes, instantiate_permission=AccessConfig(permission=AccessType.ACCESS_TYPE_ONLY_ADDRESS, address=self.deployer.key.acc_address))
        contract_storage_result = await self.send_msg(msg)
        LOG.info(contract_storage_result)
        return get_code_id(contract_storage_result)
    
    async def instantiate_contract(self, code_id: str, init_msg:dict, label: str = "Contract deployed with Capsule") -> str:
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
            msg=init_msg,
            label=label
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
    
    async def query_code_id(self, chain_url: str, code_id: int, target_chain=SupportedChains.TERRA):
        """query_code_id is used to make a REST request to the relevant chain_url 
        to specifically query the `code_details` of a given code_id

        Args:
            chain_url (str): The Chain Host of the chain to interact with e.g 
            code_id (int): The code_id to query 
            target_chain (SupportedChains Enum, optional): Only used when you wish to target a chain other than Terra. 
                Each chain can have different methods or URLs to request the same info and this option decides which way to perform queries  Defaults to SupportedChains.TERRA.

        Returns:
            Dict: `code_details` structure containing a hash with a certain encoding.
        """
        LOG.info(f"Query to be ran {code_id}")
        # query_result = self.client.wasm.code_info(code_id)
        # query_two = self.client.wasm._c._get(f"/wasm/codes/{code_id}")
        if target_chain == SupportedChains.TERRA:
            query_raw = requests.get(f"{chain_url}/wasm/codes/{code_id}").json()

        elif target_chain in SupportedChains:
            LOG.info("Chain which should be support")
            if target_chain == SupportedChains.JUNO:
                LOG.info(f"Running query against the Juno chain with Chain URL of {chain_url}")
                query_raw = requests.get(f"{chain_url}/cosmwasm/wasm/v1/code/{code_id}").json()
        else: 
            LOG.info("Chain not supported")
        return query_raw

    async def query_code_bytecode(self, chain_url: str, code_id: int, target_chain=SupportedChains.TERRA):
        """query_code_bytecode is used to make a REST request to the relevant chain_url 
        to query the actualy bytecode of the stored code object for the given code_id 

        Args:
            chain_url (str): The Chain Host of the chain to interact with e.g 
            code_id (int): The code_id to query 
            target_chain (SupportedChains Enum, optional): Only used when you wish to target a chain other than Terra. 
                Each chain can have different methods or URLs to request the same info and this option decides which way to perform queries  Defaults to SupportedChains.TERRA.

        Returns:
            dict: Dictionary containing the byte_code in base64
        """
        LOG.info(f"Query to be ran {code_id}")

        if target_chain == SupportedChains.TERRA:
        
            # TODO: This query is not cross-chain capable 
            query_raw = requests.get(f"{chain_url}/terra/wasm/v1beta1/codes/{code_id}/byte_code").json()
            LOG.info(query_raw)
        elif target_chain in SupportedChains:
            LOG.info("Chain which should be support")
            if target_chain == SupportedChains.JUNO:
                LOG.info(f"Running query against the Juno chain with Chain URL of {chain_url}")
                query_raw = requests.get(f"{chain_url}/cosmwasm/wasm/v1/code/{code_id}").json()
                # In order to maintain similar outputs, cut off everything but the datahere
                query_raw = {
                    "byte_code": query_raw["data"]
                }
        else: 
            LOG.info("Chain not supported")
        return query_raw
        

