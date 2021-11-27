# pylint: disable=invalid-name
"""Contains the basic structure necessary to execute the simulator.
"""
from edge_sim_py.simulator import Simulator

from edge_sim_py.heuristics.migration.follow_vehicle import follow_vehicle
from edge_sim_py.heuristics.migration.never_follow import never_follow


def stopping_criterion_migration_heuristics() -> bool:
    """Function that determines when the simulation should be stopped according to a given number of time steps.

    Returns:
        criterion (bool): Boolean expression that stops the simulation.
    """
    criterion = Simulator.first().current_step > Simulator.first().simulation_steps
    return criterion


def main():
    # Creates a Simulator object
    simulator = Simulator()

    # Loads the dataset file
    simulator.load_dataset(input_file="datasets/dataset1.json")

    # Executes a group of algorithms
    simulator.run(algorithm=never_follow, stopping_criterion=stopping_criterion_migration_heuristics)
    simulator.run(algorithm=follow_vehicle, stopping_criterion=stopping_criterion_migration_heuristics)

    # Displays simulation results
    simulator.show_results()


if __name__ == "__main__":
    main()
