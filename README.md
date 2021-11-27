# Registry Migration

## Installation Guide

Project dependencies are available for Linux, Windows and MacOS. However, we highly recommend using a recent version of a Debian-based Linux distribution. The installation below was validated on **Ubuntu 20.04.1 LTS**.

### Prerequisites

We use a Python library called Poetry to manage project dependencies. In addition to selecting and downloading proper versions of project dependencies, Poetry automatically provisions virtual environments for the simulator, avoiding problems with external dependencies. On Linux and MacOS, we can install Poetry with the following command:

```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

The command above installs Poetry executable inside Poetry’s bin directory. On Unix it is located at `$HOME/.poetry/bin`. We can get more information about Poetry installation at: https://python-poetry.org/docs/#installation.

### Configuration

Considering that we already downloaded the repository, the first thing we need to do is install dependencies using Poetry. To do so, we access the command line in the root directory and type the following command:

```bash
poetry shell
```

The command we just ran creates a virtual Python environment that we will use to run the simulator. Notice that Poetry automatically sends us to the newly created virtual environment. Next, we need to install the project dependencies using the following command:

```bash
poetry install
```

After a few moments, Poetry will have installed all the dependencies needed by the simulator and we will be ready to run the experiments.

## Usage Guide

Once we are inside Poetry's virtual environment, we just need to execute the main simulation file through the command below. We can customize which heuristics are executed by modifying the `edge_sim_py/__main__.py` file.

```bash
python3 -B -m edge_sim_py
```
