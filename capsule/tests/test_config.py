import os
import pytest
import mock
from capsule.lib.config_handler import DEFAULT_CONFIG_FILE, get_config_file


class TestConfigHandler():
    @mock.patch.dict(os.environ, {DEFAULT_CONFIG_FILE: "/Users/notyou"}, clear=True)
    def test_config_file_var_gathered_from_env(self):
        """test that ACmd can be inherited from
        provided that its minimum attributes and methods 
        are dealt with.
        """
        assert get_config_file() == "/Users/notyou"
