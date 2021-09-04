# capsule

## Configuration 
The capsule tool offers the ability to store details you need in a configuration file using the toml format. 

The config file by default is located in a capsule specific hidden directory at the home dir level: `~/.capsule`
It is possible also to specify the path to a custom config file using the `CAPSULE_CONFIG_FILE` environment variable.

Something to be explored is also enabling both the Mnemonic and the chain to deploy too as env vars also. If this was to happen the 
order of priority would then become Credentials in the environment -> Config file in the environment -> Default or specified config file.
Following this pattern in theory should make this tool very easy to use in CI/CD as a given user can just specify the Mnemonic and chain ID for as secrets in the job for a quick start.