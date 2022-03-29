# Registry Migration

## Repository Structure

Within the repository, you'll find the following directories and files, logically grouping common assets used to simulate maintenance of edge computing infrastructures. You'll see something like this:

```
├── datasets/
│   ├── dataset_25occupation.json
│   ├── dataset_50occupation.json
│   └── dataset_75occupation.json
├── simulator/
│   ├── component_builders/
│   ├── components/
│   ├── dataset_generator.py
│   ├── algorithms/
│   │   ├── follow_vehicle.py
│   │   └── never_follow.py
│   ├── __main__.py
│   ├── object_collection.py
│   └── simulator.py
├── poetry.lock
└── pyproject.toml
```

In the root directory, the `pyproject.toml` file organizes all project dependencies, including the minimum required version of the Python language. This file guides the execution of the Poetry library, which installs the simulator securely, avoiding conflicts with external dependencies.

> Modifications made to the pyproject.toml file are automatically inserted into poetry.lock whenever Poetry is called.

The "datasets" directory contains JSON files describing the components that will be simulated during the experiments. We can create custom datasets modifying the `dataset_generator.py` file, located inside the "simulator" directory.

The "simulator/algorithms" directory accommodates the source code for the migration strategies used in the simulator.

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

Once we are inside Poetry's virtual environment, we just need to run the simulator with parameters that dictate what is executed. A description of the simulator parameters is presented below.

| **Parameter** | **Description**                                                                               |
| ------------- | --------------------------------------------------------------------------------------------- |
| -s            | Seed number that allows reproducibility (e.g., "1")                                           |
| -i            | Dataset file (e.g.: "dataset_25occupation", "dataset_50occupation", "dataset_75occupation")   |
| -a            | Algorithm that will be executed (e.g.: "never_follow, "follow_vehicle", "proposed_heuristic") |
| -d            | Delay threshold for the proposed algorithm (e.g.: "0.7", "0.8, "0.9", "1.0"                   |
| -p            | Provisioning time threshold for the proposed algorithm (e.g.: "0.7", "0.8, "0.9", "1.0"       |


Based on the parameters above, we can run the simulation, as shown below.

```bash
python3 -B -m simulator -s 1 -i "dataset_25occupation" -a "proposed_heuristic" -d "0.7" -p "0.7"
```
