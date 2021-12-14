# Setup tests

To install all dependencies, run:

    cd tests
    python -m pip install -r requirements.txt

# How to run tests

Run tests using the run_tests.py module:

    cd tests
    python run_tests.py

## Run all tests

To include all tests (include slow) run:

    cd tests
    python run_tests.py --all

## Options

A number of other options are available:

    usage: run_tests.py [-h] [--all] [--slow] [--debug] [--no-report] [--no-keep] [--no-open]

    Unit test interface

    optional arguments:
      -h, --help        show this help message and exit
      --all, -a         Include all tests
      --slow, -s        Includes slow tests
      --debug, -d       Enables debug mode
      --no-report, -nr  Does not generate test reports
      --no-keep, -nk    Removes test report after showing
      --no-open, -no    Suppresses test report

## Help

To display help for run_tests.py, run the following command:

    python run_tests.py -h
