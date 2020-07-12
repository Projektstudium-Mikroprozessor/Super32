"""
Usage:

    pip install .

    to locally install the package via pip.
"""

import setuptools

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name='super32assembler',
    version='0.4.0',
    description='Super32 Assembler',
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url='https://github.com/Projektstudium-Mikroprozessor/Super32',
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': ['super32assembler=super32assembler.__main__:main'],
    },
    install_requires=[
        'bitstring',
        'python-dotenv',
        'docopt==0.6.2',
        'super32utils'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
