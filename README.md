# Super32 - Designing our own Microprocessor

This repository contains the source code for a simple assembler/compiler for our educational processor as well as an emulator.

`super32assembler` is an assembler, written in [Python](https://www.python.org/).
`super32emu` is an emulator, written in Python as well. Qt is used for the GUI.

## Getting Started

These instructions will help you to get your environment ready to build, develop and run the project on your local machine.

### Installation

You'll need Python and Pip installed on your machine.

The Python packages are currently not available via PyPi.
To install the package you first have to clone the git repository:

```Bash
git clone https://github.com/xsjad0/Super32.git
```

After you successfully cloned the repository, switch to the latest [release](https://github.com/Projektstudium-Mikroprozessor/Super32) and run the installation process via pip

```Bash
git checkout X.Y.Z
pip install ./super32utils
pip install ./super32assembler
pip install ./super32emu
```

### Write assembler code

Take a look at the [instructionset](super32assembler/instructionset.json) of the Super32 processor.
Also, feel free to include [these fancy assembler directives](super32assembler/preprocessor/asmdirectives.py) to improve your code.

Here are some rules you always have to keep in mind when you write some assembler code:

Your code always has to start with

```Assembler
ORG [address]
START
```

and end with an

```Assembler
END
```

assembler directives, where address MUST be greater than and be able to divide by 4.

Define constants in your memory like this:

```Assembler
DEFINE 0
```

For easier referencing the constants in your code, put a label in front of your constant:

```Assembler
[constantname]: DEFINE [value]
```

See the `examples/` directory

### Usage

Provide the path to an assembler code file as command line argument:

```Bash
super32assembler example_code.s32
```

If you want to define a custom output name / path, use the '-o' argument flag.
All available options are listed in the table below.

Option | Default | Description
-|-|-
-h/--help | - | Display help information
-o/--output | \<input-file\>.o | Custom output name / path
-g/--generator | lines | Specify output format. use ```lines``` to generate 32bit machine-code each line. Use ```stream``` to generate one single line machine-code.
-a/--architecture | single | Specify processor architecture. use ```single``` to select single-memory architecture. Use ```multi``` to select dual-memory architecture.

## Development

### Setup

Install the required packages:

```Bash
pip install -r requirements.txt
pip install -r requirements/development.txt
```

Install our packages as well (Super32emu has dependencies on assembler and utils):

```Bash
pip install ./super32utils
pip install ./super32assembler
```

### Running our modules

```Bash
cd super32assembler && python -m super32assembler
```

or

```Bash
cd super32emu && python -m super32emu
```

### Running the tests

We use [pytest](https://docs.pytest.org/en/latest/) for testing.
To run these test use:

```Bash
pytest test_{test_name}.py
```

## Versioning

We use [SemVer](http://semver.org/) for versioning.
For the versions available, see the [releases on this repository](https://github.com/Projektstudium-Mikroprozessor/Super32/releases).

## Authors

- *Marcel Freiberg* - [freib98](https://github.com/freib98)
- *Marius Schenzle* - [xsjad0](https://github.com/xsjad0)
- *Thomas Schöller* - [MaxAtoms](https://github.com/MaxAtoms)
- *Noah Ströhle* - [DrNochi](https://github.com/DrNochi)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
