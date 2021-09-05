
import os
from capsule.lib.config_handler import get_config

async def get_mnemonic(strict=False):
    """Attempt to gather a mnemonic from one of the available sources
    First, if a mnemonic is defined in the env, use that.
    Next, check the config file for the secret 
    If no mnemonic can be found, optionally raise an Exception
    

    Args:
        strict (bool, optional): When set to true, if no mnemonic is found an exception is raised. Defaults to False.

    Returns:
        str: The mnemonic found either in the env or in the config file
    """
    if os.getenv("CAPSULE_MNEMONIC", False):
        return os.environ["CAPSULE_MNEMONIC"]

    config = await get_config()
    if config.get("deploy_info", {}).get("mnemonic", False):
        return config.get("deploy_info", {}).get("mnemonic", False)
    
    if strict:
        raise Exception("No Mnemonic was found either in the specified config file or in the environment. Strict mode is set to true")
    return None
    



    
