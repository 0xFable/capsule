import argparse as argparse
from argparse import HelpFormatter

class ACmd(object):
    """ACmd is an abstraction that helps to
    define a consistant minimal interface for
    each command in this CLI.
    When a class is a subclass of this you have the assurance:
    The class is-a command of some sort
    It has info for its Name, Description, Example Usage and Help
    It has a run_command function to execute
    """
    REQUIRED_FIELDS = ['cmd_name', 'cmd_description', 'cmd_help', 'cmd_usage']


    def __init__(self, sub_parser):
        # Raise an exception if a subclass does not set values for all of the required fields
        if not all(getattr(self, field.upper()) is not None for field in self.REQUIRED_FIELDS):
            raise Exception("Command did not implement all the required fields")

        self.parser = sub_parser.add_parser(self.CMD_NAME,
                            help=self.CMD_HELP,
                            formatter_class=HelpFormatter,
                            parents=[])
        self.initialise(self)


    def initialise(self):
        raise NotImplementedError()

    def run_command(self, args):
        raise NotImplementedError()
