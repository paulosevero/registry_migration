# pylint: disable=invalid-name
"""Contains the basic structure necessary to execute the simulator.
"""
# Simulator components and algorithms
from simulator import *

# Python libraries
import argparse
import random


def stopping_criterion_migration_heuristics() -> bool:
    """Function that determines when the simulation should be stopped according to a given number of time steps.

    Returns:
        criterion (bool): Boolean expression that stops the simulation.
    """
    criterion = Simulator.first().current_step > Simulator.first().simulation_steps
    return criterion


def main(params: dict = {}):
    """Executes the simulation.

    Args:
        params (dict, optional): User-defined parameters for the algorithms. Defaults to {}.
    """
    random.seed(params["seed"])

    # Creates a Simulator object
    simulator = Simulator()

    # Loads the dataset file (e.g.: "dataset_25occupation", "dataset_50occupation", "dataset_75occupation")
    simulator.load_dataset(input_file=f"datasets/{params['dataset']}.json")

    # Executes the algorithm (e.g.: "never_follow, "follow_vehicle", "proposed_heuristic")
    simulator.run(
        algorithm=globals()[params["algorithm"]],
        stopping_criterion=stopping_criterion_migration_heuristics,
        params=params,
    )

    # Displays simulation results
    simulator.show_results(verbose=True, params=params)


if __name__ == "__main__":
    # Parsing named arguments from the command line
    parser = argparse.ArgumentParser()

    # Defining valid arguments
    parser.add_argument("--seed", "-s", help="Seed number that allows reproducibility")
    parser.add_argument("--dataset", "-i", help="Dataset file")
    parser.add_argument("--algorithm", "-a", help="Algorithm that will be executed")
    parser.add_argument("--delay-threshold", "-d", help="Delay threshold for the proposed algorithm")
    parser.add_argument("--prov-time-threshold", "-p", help="Provisioning time threshold for the proposed algorithm")

    # Parsing arguments
    args = parser.parse_args()

    seed = int(args.seed)
    dataset = args.dataset
    algorithm = args.algorithm
    delay_threshold = float(args.delay_threshold)
    prov_time_threshold = float(args.prov_time_threshold)

    # Building a dictionary with the arguments
    params = {
        "seed": seed,
        "dataset": dataset,
        "algorithm": algorithm,
        "delay_threshold": delay_threshold,
        "prov_time_threshold": prov_time_threshold,
    }

    # Calling the main function
    main(params=params)
