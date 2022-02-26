
import argparse

import pytest

from capsule.abstractions import ACmd
from capsule.cmds import DeployCmd
from capsule.cmds.deploy import DeployCmd
from capsule.parser import get_main_parser, get_subcommmand_parser


class TestCommandAbstraction():
    def test_interface_with_impl_methods(self):
        """test that ACmd can be inherited from
        provided that its minimum attributes and methods 
        are dealt with.
        """
        class GoodImpl(ACmd):
            CMD_NAME = 'good'
            CMD_DESCRIPTION = 'a very useful command'
            CMD_HELP = 'help instructions when you get a common problem'
            CMD_USAGE = '$ capsule command [options]'

            def run_command():
                pass

            def initialise(self):
                pass
        main_parser = get_main_parser()

        sub_parser = get_subcommmand_parser(main_parser)

        GoodImpl.__init__(GoodImpl, sub_parser=sub_parser)

    def test_interface_without_std_attributes(self):
        """test to confirm an Attribute error is provided
        to the developer if they do not define 
        each of the required attributes
        """
        main_parser = get_main_parser()

        sub_parser = get_subcommmand_parser(main_parser)
        DeployCmd.__init__(DeployCmd, sub_parser=sub_parser)

        class BadImpl(ACmd):
            pass

        with pytest.raises(AttributeError):
            BadImpl.__init__(BadImpl, sub_parser=sub_parser)

    def test_interface_without_std_methods(self):
        """test to confirm a NotImplementedError is provided
        to the developer if they do not define 
        each of the required methods 
        """
        main_parser = get_main_parser()

        sub_parser = get_subcommmand_parser(main_parser)
        DeployCmd.__init__(DeployCmd, sub_parser=sub_parser)

        class BadImpl(ACmd):
            CMD_NAME = 'alpha'
            CMD_DESCRIPTION = 'its nearly ready for prod!'
            CMD_HELP = 'help instructions when you get a common problem'
            CMD_USAGE = '$ capsule command [options]'

            # Note none of the needed methods are defined

        with pytest.raises(NotImplementedError):
            BadImpl.__init__(BadImpl, sub_parser=sub_parser)

