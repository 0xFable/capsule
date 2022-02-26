from .deploy import DeployCmd
from .execute import ExecuteCmd
from .local import LocalCmd
from .new import NewCmd
from .query import QueryCmd
from .verify import VerifyCmd

AVAILABLE_COMMANDS:list = [DeployCmd, LocalCmd, QueryCmd, ExecuteCmd,VerifyCmd, NewCmd]
