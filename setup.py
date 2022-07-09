import io
from os import path

from setuptools import find_packages, setup

this_directory = path.abspath(path.dirname(__file__))

with io.open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    readme_text = f.read()
    long_description = readme_text


setup(
    name='capsule_terra',
    license='MIT',
    version='0.2.0',
    packages=find_packages(),
    include_package_data=True,
    # Add command line: capsule and terra_deploy
    entry_points={
        'console_scripts': ['capsule=capsule.cli:main',
        'terra_deploy=capsule.cli:main']
    },

    # PyPI metadata
    author='0xFable',
    author_email='0xfable@protonmail.com',
    description='Capsule is small Python SDK tool you can use to deploy Terra CosmWasm contracts to a given Terra (Cosmos SDK Based) chain.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'argparse',
        'requests',
        'terra_sdk',
        'toml',
        'GitPython'
    ],
    keywords='cosmwasm terra',
)