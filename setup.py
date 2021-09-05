from setuptools import setup, find_packages

setup(
    name="capsule_terra",
    license="MIT",
    version="0.0.1",
    packages=find_packages(),
    include_package_data=True,
    # Add command line: capsule and terra_deploy
    entry_points={
        "console_scripts": ["capsule=capsule.cli:main",
        "terra_deploy=capsule.cli:main"]
    },

    # PyPI metadata
    author="0xFable",
    author_email="0xfable@protonmail.com",
    description="Capsule is small Python SDK tool you can use to deploy Terra CosmWasm contracts to a given Terra (Cosmos SDK Based) chain.",
    install_requires=[
        'argparse',
        'requests',
        'terra_sdk',
        'toml'
    ],
    keywords="cosmwasm terra",
)