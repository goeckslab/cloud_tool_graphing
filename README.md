# Cloud Tool Grapher
A tool for generating graphs from cloud instance data for use with cancer.usegalaxy.org

## Installation

```
pip install <path to repo>
```
or, to install it in a venv in the same directory:
```
./venv_setup.sh
```
...which will create a virtual environment in `./venv/` with the requirements and this package which can be activated with:
```
$ source venv/bin/activate
```

## Usage

### in the terminal:

```
$ ./cloudgrapher
```
to use the default included files as data input sources; for more info:
```
./cloudgrapher -h
```

### in python

```
import cloudtoolgrapher
```
...i mean there's clearly more to it but this is a first pass at a readme