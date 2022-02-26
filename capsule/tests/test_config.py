import os
import pytest
import mock
from capsule.lib.config_handler import DEFAULT_CONFIG_FILE_ENV_VAR, get_config_file, get_config
import asyncio

TEST_CONFIG_FILE_RELATIVE_PATH = "./capsule/lib/settings/config.toml"
TEST_CONFIG_FILE_LOCATION = os.path.abspath(
                os.path.expandvars(
                    os.path.expanduser(TEST_CONFIG_FILE_RELATIVE_PATH)))
class TestConfigHandler():
    @mock.patch.dict(os.environ, {DEFAULT_CONFIG_FILE_ENV_VAR: "/Users/notyou"}, clear=True)
    def test_config_file_var_gathered_from_env(self):
        """test that ACmd can be inherited from
        provided that its minimum attributes and methods 
        are dealt with.
        """
        assert get_config_file() == "/Users/notyou"

    @pytest.mark.skip("No longer is a file not found raised, a file is created instead ")
    def test_config_fails_without_a_provided_path_or_created_default_file(self):
        """test when we try to run get_config without a provided path on
        an assumed fresh system that it will fail.

        This is expected as when no file is provided and None is found in the env 
        It will default to ~/.capsule/config.toml
        Which shouldn't exist on a fresh system
        """
        with pytest.raises(FileNotFoundError):
            asyncio.run(get_config())
    
    def test_config_with_specified_path(self):
        """test when we try to run get_config with a provided path
        that it will find the file, be able to parse the file
        And we can ensure values are within the file.
        """
        assert asyncio.run(get_config(TEST_CONFIG_FILE_RELATIVE_PATH))
        assert 'networks' in asyncio.run(get_config(TEST_CONFIG_FILE_RELATIVE_PATH))

    @mock.patch.dict(os.environ, {DEFAULT_CONFIG_FILE_ENV_VAR: TEST_CONFIG_FILE_LOCATION}, clear=True)
    def test_config_gathered_from_env(self):
        """test when a mocked environment variable is setup on the system
        this value is read and the function will find the file,
        be able to parse the file
        And we can ensure values are within the file.
        """
        assert asyncio.run(get_config())
        assert 'networks' in asyncio.run(get_config())
        