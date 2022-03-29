"""Automatic Python configuration file.
"""
__version__ = "0.1.0"

# Simulator components
from .simulator import Simulator

# Resource management algorithms
from .algorithms.never_follow import never_follow
from .algorithms.follow_user import follow_user
from .algorithms.proposed_heuristic import proposed_heuristic
