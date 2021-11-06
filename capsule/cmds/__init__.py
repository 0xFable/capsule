from .deploy import DeployCmd
from .local import LocalCmd
from .query import QueryCmd
AVAILABLE_COMMANDS:list = [DeployCmd, LocalCmd, QueryCmd]
