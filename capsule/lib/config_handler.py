"""Load configuration from .toml file."""
import toml
import os

def get_config_file(filename=None):
    """Attempts to get the location of 
    the capsule config. 
    One of 4 things occurs here, either:
    - A config location is gathered from the environment
    - A specified filename is provided and a config file with this name is created
    - A specified filename is provided and if a config file with this name if found in the current dir then this is used
    - A default config file is created in the ~/.capsule directory

    Args:
        filename ([str], optional): A specified filename to create for config. Defaults to None.

    Returns:
        [str]: [The config files path.]
    """

    # First check if there is a specified location in the env
    env_config_file = os.environ.get("CAPSULE_CONFIG_FILE", None)

    # If a config was specified in the env, this takes priority
    if env_config_file: return env_config_file

    # If a filename was provided use this as the config file name
    if filename: return os.path.expandvars(os.path.expanduser(filename))

    # Otherwise use a default one located in the .capsule directory at the home dir
    config_file = os.path.expanduser(os.path.join("~", ".capsule", filename))
    capsule_dir = os.path.dirname(config_file)
    # Check if the capsule directory has been created and if not, create it.
    if not os.path.exists(capsule_dir):
        os.makedirs(capsule_dir)
    return config_file


# Read local `config.toml` file.
config = toml.load(get_config_file(filename="settings/config.toml"))
print(config)

# Retrieving a dictionary of values
config['project']
config.get('project')

# Retrieving a value
config['project']['author']
config.get('project').get('author')