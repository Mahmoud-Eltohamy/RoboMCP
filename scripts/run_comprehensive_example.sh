#!/bin/bash

# Run the comprehensive Appium API example

# Add the current directory to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run the example
python examples/comprehensive_appium_example.py "$@"

