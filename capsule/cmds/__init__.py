from .deploy import DeployCmd
from .local import LocalCmd
from .query import QueryCmd
from .execute import ExecuteCmd
from .verify import VerifyCmd


AVAILABLE_COMMANDS:list = [DeployCmd, LocalCmd, QueryCmd, ExecuteCmd,VerifyCmd]
