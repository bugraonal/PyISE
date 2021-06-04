# PyISE
This is a Python wrapper for Xilinx ISE with the added functionality of batch synthesis and simulation. The console output of batch operations are logged.

## Installation
This project is currently composed of a single script. Linux and Windows are supported.
In order to use it, the following are neccessary:
- Python3
- colorama (pip package)
- Xilinx ISE
- ISIM

In order to use this package, clone this repo with
```
git clone https://github.com/bugraonal/PyISE.git
```

An installation script will be added in the future.

## Usage
PyISE can be used either in other Python scripts or stand-alone. 

Examples of usage in other scripts can be found in the test scripts inside test directory. When used like this, you can include PyISE in your custom script or program. 

Examples of standalone usage can be seen with the two scripts named batch.sh and batch.bat for Linux and Windows respectively. These were written for automating grading for submissons form a Moodle platform. It will simulate and synthesize all the submissons and create logs. 

For further detail about the usage, check the docstring. It contains information regarding the usage. 

## Support
You can use the issues section to ask for help regarding PyISE. 

