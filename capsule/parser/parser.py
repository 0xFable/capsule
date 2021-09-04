from argparse import ArgumentParser, HelpFormatter


def get_main_parser():
    parser = ArgumentParser(
            prog="capsule",
            description="Python CLI which abstracts the deployment process into a small operation. Specify a config, run the deploy command while passing the location of the contract to deploy and let capsule handle the rest.",
            epilog="For support, please open a github issue.")

    parser.usage = """
    $ capsule <subcommand> ...
    $ capsule -v <subcommand> ...
    $ capsule -h
    """

    return parser

def get_subcommmand_parser(main_parser):
    # The subparser will act as a router for commands. 
    sub_parser = main_parser.add_subparsers(
        title="subcommands",
        description="one of these subcommands must be provided",
        metavar="",
        dest="cmd"
    )

    return sub_parser

