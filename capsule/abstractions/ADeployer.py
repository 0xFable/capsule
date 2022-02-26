import abc
import sys

if sys.version_info >= (3, 4):
    ABC = abc.ABC
else:
    ABC = abc.ABCMeta('ABC', (), {})


class ADeployer(ABC):

    @abc.abstractmethod
    def store_contract(self, contract_name:str, contract_path:str):
        """
        store_contract should implement an attempt 
        to gather a given wasm artifact file provided via the command line args 
        and upload it ot the given chain as a StoredCodeObject.
        """
        pass

    @abc.abstractmethod
    def instantiate_contract(self, code_id: str, init_msg:dict):
        """instantiate_contract should implement the logic
        needed to complete the instantiate of a contract from a stored 
        code_id using the provided init_msg."""
        pass
     
    @abc.abstractmethod
    def execute_contract(self, contract_addr: str, execute_msg, coins):
        """execute_contract should implement the logic
        needed to complete the execution of an action on a contract using its
        contract address a provided execute_msg and when needed, a list of Coins objects."""
        pass

    @abc.abstractmethod
    def query_contract(self, contract_addr: str, query_msg):
        """query_contract should implement the logic
        needed to complete the query on a contract using its
        contract address and a provided query_msg"""
        pass

