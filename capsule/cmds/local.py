"""Local command -- Used to spin up a local instance of localterra or your favorite multi-chain dev-env"""
import os
import pathlib
# Used to call docker-compose shell command
import subprocess
import sys
from subprocess import PIPE, STDOUT

# Used to clone localterra repo
import git

from capsule.abstractions import ACmd
from capsule.lib.logging_handler import LOG

sys.path.append(pathlib.Path(__file__).parent.resolve())

DEFAULT_TESTNET_CHAIN = "bombay-12"
DEFAULT_CLONE_PATH = os.path.expanduser(
    os.path.join("~", ".capsule", "localterra-clones"))


class LocalCmd(ACmd):
    """
        Local command -- Used to spin up a local instance of localterra or your favorite multi-chain dev-env
    """

    CMD_NAME = "local"
    CMD_HELP = "Attempt to setup a local chain instance using Git and Docker."
    CMD_USAGE = """
    $ capsule local"""
    CMD_DESCRIPTION = "Helper tool which attempts to git clone the localterra repo and then compose it as services which you can use for local dev env contract testing"

    def initialise(self):
        # Define usage and description
        self.parser.usage = self.CMD_USAGE
        self.parser.description = self.CMD_DESCRIPTION

        # Add any positional or optional arguments here
        self.parser.add_argument("-p", "--package",
                                 type=str,
                                 help="(required) Name of new or path to existing package")

        # Add any positional or optional arguments here
        self.parser.add_argument("-d", "--down",
                                 action='store_false',
                                 help="(Optional) Whether to spin down, include to spin down an instance")

        self.parser.add_argument("-c", "--chain",
                                 type=str,
                                 default="",
                                 help="(Optional) A chain to deploy too. Defaults to localterra")

    def run_command(self, args):
        """Schema:
            Check if we already have a local terra, if so return the path

            If we don't git clone the localterra repo and then return the path

            Pass path to docker-compose and attempt to interact

            Return success.
        """
        LOG.info("Starting local setup of localterra")
        # Start by doing a git clone
        # Check if the repo is already cloned in the default location
        repo = self.get_localterra_repo(self)
        LOG.info(
            "Localterra repo actions finished, now attempting to use its compose-file")
        # Spin up or down via compose
        self.run_docker_compose(args, dirname=repo.working_tree_dir)
        LOG.info("Finish docker interaction")

        LOG.info("Command run finished")

    def get_localterra_repo(self, CLONE_LOCATION=DEFAULT_CLONE_PATH, CLONE_REMOTE_URL="git@github.com:terra-money/LocalTerra.git"):
        """Attempts to get a localterra repository so that localterra can be interacted with.
        Note: Any compose spun up away from the capsule tool may not be accessible by the tool.
        You need to ensure you are passing the correct Docker Compose in order to use this tool to interact with your already deployed services

        Args:
            CLONE_LOCATION (str, optional): Where the repos will go, defaults to DEFAULT_CLONE_PATH which is "~/.capsule/localterra-clones".
            CLONE_REMOTE_URL (str, optional): The git url to clone from. Defaults to "git@github.com:terra-money/LocalTerra.git".

        Returns:
            git.Repo: The repo to be worked with
        """
        if os.path.exists(os.path.realpath(CLONE_LOCATION)):
            LOG.info("localterra appears to be already cloned, skipped reclone")
            return git.Repo(os.path.realpath(CLONE_LOCATION))
        return git.Repo.clone_from(url=CLONE_REMOTE_URL, to_path=CLONE_LOCATION, depth=1)

    def run_docker_compose(args, dirname, filename="docker-compose.yml"):
        """Take a directory and a filename for the compose and attempt to
        interact with docker-compose

        Args:
            dirname ([type]): The directory of the project where the compose file is
            filename (str, optional): The compose file name. Defaults to "docker-compose.yml".

        Returns:
            process: The process
        """
        command_name = ["docker-compose", "-f",
                        os.path.join(dirname, filename), "up" if args.down else "down"]
        LOG.info(f"[Compose Command] {''.join(command_name)}")
        try:
            LOG.info("Starting compose command \n\n\n")
            with subprocess.Popen(command_name, stdin=PIPE, stdout=PIPE, stderr=STDOUT, universal_newlines=True) as process:
                while process.poll() is None:
                    line = process.stdout.readline()
                    LOG.info(line.rstrip())
        except KeyboardInterrupt:
            # process.terminate()
            sys.exit()
        except Exception as ex:
            print("Encountered an error : ", ex)
