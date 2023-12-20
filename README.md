[![Unit tests](https://github.com/rbaltrusch/python_interpreter/actions/workflows/pytest-unit-tests.yml/badge.svg)](https://github.com/rbaltrusch/python_interpreter/actions/workflows/pytest-unit-tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](https://opensource.org/licenses/MIT)

# Natscript Interpreter

This is Natscript, a custom interpreted language with a free, natural language-like syntax that lends itself to prosaic code, such as:

```powershell
define function main as {
    set squares to []
    for each number in range from 0 to 5 not equal to 3 {
        multiply it by itself, then append it to squares
    }
    return squares
}

# This will output [0, 1, 4, 16] to the console
print result of call main
```

The main implementation of the Natscript interpreter is currently written in Python, but may be shifted to [C++](https://github.com/rbaltrusch/python_interpreter/tree/main/README.md#1-c-implementation) in the future for improved performance.

## Available functionality

Currently available functionality includes:
- variables and operations
- conditionals
- loops (for-each, while)
- first-order functions
- module declarations and imports
- access modifiers (private, constant)
- recursion
- a bytecode compiler to speed up module loading
- precise stack traces for run-time exceptions

Language documentation can be found in the [doc](https://github.com/rbaltrusch/python_interpreter/tree/main/doc) folder.

## Getting started

To get a copy of this repository, clone it using git, then install all dependencies (currently none), as well as the interpreter package itself:

```batch
git clone https://github.com/rbaltrusch/python_interpreter
cd python_interpreter
python -m pip install -r requirements.txt
python -m pip install -e .
```

To run the interpreter, run the interpreter package, specifying a Natscript file to be executed, or nothing to enter an interactive shell session:
```batch
python -m interpreter
python -m interpreter examples\helloworld.nat
```

## Syntax highlighting

### Github / Linguist

Currently, Natscript is in its early stages and not supported yet by Linguist (which, e.g. provides the syntax highlighting on Github). Powershell syntax highlighting seems to be an acceptable alternative.

### Visual Studio Code

Language support in VS Code is in work, but not available yet. An early-stage VS Code extension with static syntax highlighting can be found [here](https://github.com/rbaltrusch/natscript-vscode), but at the moment needs to be manually added to the VS Code extensions folder.

### Notepad++

The syntax highlighting file for Natscript in Notepad++ can be found [here](https://github.com/rbaltrusch/python_interpreter/tree/main/tools/syntax_highlighting/notepad++/natscript.xml). It can be imported to Notepad++ in the Languages menu (Languages -> User Language -> Define Your Language... -> Import).

## Documentation

Language documentation, including examples and tutorials, can be found in the [doc](https://github.com/rbaltrusch/python_interpreter/tree/main/doc) folder. It is currently a work in progress.

### Examples

Below is one example of the natural syntax of Natscript:

```powershell
define function fibonacci expecting [limit] as {
    set old to 1
    set current to 1
    set numbers to [old current]

    while checked that current is less than the limit {
        set temp to current
        add old to current then set old to temp
        append current to numbers
    }
    return the numbers
}

define function main as {
    return result of call fibonacci with [1000000]
}

# prints all fibonacci numbers from 1 to 1000000
call main and print result
```

A full list of code examples can be found [here](https://github.com/rbaltrusch/python_interpreter/tree/main/doc/examples).

### Tutorials

Tutorials can be found in the [doc](https://github.com/rbaltrusch/python_interpreter/tree/main/doc) folder.

### Interpreter CLI

The Natscript interpreter CLI has several configureable options:

```
usage: interpreter [-h] [--debug] [--compile COMPILE] [--compiled-format {pickle,json}]
                             [--iterations ITERATIONS]
                             filepath

CLI for the Natscript interpreter

positional arguments:
  filepath              The path of the Natscript file to be run

optional arguments:
  -h, --help            show this help message and exit
  --debug, -d           Enables the interpreter debug mode
  --compile COMPILE, -c COMPILE
                        Enables the bytecode compiler
  --compiled-format {pickle,json}, -f {pickle,json}
                        Specifies the format of the bytecode-compiled file
  --iterations ITERATIONS, -i ITERATIONS
                        Specifies how often the script should be executed
```

The interpreter CLI help message can be shown by running:
```batch
python -m interpreter -h
```

## Pyinstaller

Packaging the interpreter using pyinstaller can speed up execution time of Natscript code by a factor of 2x. Simply bundle it using the command:

```batch
pyinstaller -n interpreter interpreter/__main__.py
```

This will generate an executable file called interpreter.exe (with the same CLI as the python package) in the dist/interpreter folder.

## C++ Implementation

The C++ implementation (work in progress) of the Natscript interpreter can be found [here](https://github.com/rbaltrusch/cpp-natscript). This may be abandoned in the future in favour of LLVM-based JIT acceleration for the Python implementation of Natscript.

## Contributions

Contributions are welcome! For more details, please read the [contribution guidelines](CONTRIBUTING.md).

## Python

Written in Python 3.8.3.

## License

This repository is open-source software available under the [MIT license](https://github.com/rbaltrusch/python_interpreter/blob/main/LICENSE).

## Contact

Please raise an issue for code changes. To reach out, please send an email to richard@baltrusch.net.
