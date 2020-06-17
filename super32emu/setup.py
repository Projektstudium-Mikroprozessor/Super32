"""
Usage:

    pip install .

    to locally install the package via pip.
"""

import setuptools

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name='super32emu',
    version='0.3.0',
    description='Super32 Emulator',
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url='https://github.com/Projektstudium-Mikroprozessor/Super32',
    include_package_data=True,
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': ['super32emu=super32emu.__main__:main'],
    },
    install_requires=[
        'bitstring',
        'python-dotenv',
        'pyside2',
        'super32assembler',
        'super32utils'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
