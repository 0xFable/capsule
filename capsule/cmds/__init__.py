from .deploy import DeployCmd
from .local import LocalCmd
AVAILABLE_COMMANDS:list = [DeployCmd, LocalCmd]
