
from capsule.parser import get_main_parser, get_subcommmand_parser
from capsule.cmds import DeployCmd, AVAILABLE_COMMANDS
from capsule.lib.logging_handler import LOG

import sys 

def main():
    """This is the main entrypoint
    for the capsule tool.
    To comment briefly on its structure:
    - A main parser is established. This becomes the main router when a user enters the `capsule` command.
    - A subparser is added to the main parser. This becomes the keeper of each command
    - Each command is initialized with the subparser as a parent.
    - The main parse has all of its args parsed. Doing this after the above steps ensures we have all needed args for the help menu.
    """
    main_parser = get_main_parser()

    sub_parser = get_subcommmand_parser(main_parser)
    LOG.debug(AVAILABLE_COMMANDS)
    for cmd in AVAILABLE_COMMANDS:
        cmd.__init__(cmd, sub_parser=sub_parser)
    
    try:
        # Parse the arguments
        args = main_parser.parse_args()

        if args.cmd is None:
            main_parser.print_help()
            sys.exit()
    except Exception as e:
        main_parser.print_help()
        sys.exit()

    # Loop the commands again searching for the user-specified command
    for cmd in AVAILABLE_COMMANDS: 
        # If one of the available commands is the specified one       
        if cmd.CMD_NAME == args.cmd:
            # Run it with the provided args
            cmd.run_command(cmd, args)

    
        