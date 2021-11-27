""" Contains map creation functions."""


def create_hexagonal_grid(x_size: int, y_size: int) -> list:
    """Creates a hexagonal grid to represent the map based on: https://doi.org/10.1109/TSUSC.2021.3049850.

    Args:
        x_size (int): Horizontal size of the hexagonal grid.
        y_size (int): Vertical size of the hexagonal grid.

    Returns:
        list: Created coordinates.
    """
    map_coordinates = []

    x_range = list(range(0, x_size * 2))
    y_range = list(range(0, y_size))

    for i, y in enumerate(y_range):
        for x in x_range:
            if x % 2 == i % 2:
                map_coordinates.append((x, y))

    return map_coordinates
