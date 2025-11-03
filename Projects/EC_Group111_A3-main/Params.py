"""Shared parameters and helpers for the EC_Group111_A3 examples.

Put global constants and small utilities here so example scripts can
import a single source of truth when editing experiment parameters.
"""

from pathlib import Path
from typing import Final

import numpy as np
import numpy.typing as npt
import matplotlib.pyplot as plt
import mujoco as mj
from mujoco import viewer
import random
import time
from datetime import datetime
import json
from functools import wraps
import threading

# ARIEL / project utilities
from ariel import console
from ariel.body_phenotypes.robogen_lite.constructor import (
	construct_mjspec_from_graph,
)
from ariel.body_phenotypes.robogen_lite.decoders.hi_prob_decoding import (
	HighProbabilityDecoder,
	save_graph_as_json,
)
from ariel.ec.genotypes.nde import NeuralDevelopmentalEncoding
from ariel.simulation.controllers.controller import Controller
from ariel.simulation.environments import OlympicArena
from ariel.utils.renderers import single_frame_renderer, video_renderer
from ariel.utils.runners import simple_runner
from ariel.utils.tracker import Tracker
from ariel.utils.video_recorder import VideoRecorder

# Evolutionary algorithm library (used by EA.py)
from deap import base, creator, tools

# Randomness
SEED: Final[int] = 42
RNG = np.random.default_rng(SEED)

# World / robot constants
NUM_OF_MODULES: Final[int] = 30
SPAWN_POS = [-0.8, 0, 0.1]
SPAWN_POSITIONS = [[-0.8, 0, 0.1], [0.5, 0, 0.1], [2.5, 0, 0.2]]
TARGET_POSITION = [5, 0, 0.5]

# Genotype / evaluation defaults
GENOTYPE_SIZE: Final[int] = 64
INIT_EVAL_DURATION: Final[int] = 20


def data_dir_for(script_name: str) -> Path:
	"""Return a Path to __data__/<script_name> and ensure it exists.

	Example:
		DATA = data_dir_for(__file__.split('/')[-1][:-3])
	"""
	# Place the DATA folder inside this examples package directory so each
	# EC_Group111_* example keeps its data nearby.
	module_dir = Path(__file__).parent
	data = module_dir / "DATA" / script_name
	data.mkdir(parents=True, exist_ok=True)
	return data


# ---------------- EA / experiment configuration -----------------
# Brain EA parameters
BRAIN_HIDDEN_SIZE: Final[int] = 8
BRAIN_GENERATIONS: Final[int] = 100
BRAIN_POPULATION_SIZE: Final[int] = 20
BRAIN_CROSSOVER_PROBABILITY: Final[float] = 0.2
BRAIN_MUTATION_PROBABILITY: Final[float] = 0.8
BRAIN_NUMBER_OF_ELITES: Final[int] = 1

# Body EA parameters
BODY_GENERATIONS: Final[int] = 10
BODY_POPULATION_SIZE: Final[int] = 5
BODY_INIT_POP_SIZE: Final[int] = BODY_POPULATION_SIZE * 20
BODY_CROSSOVER_PROBABILITY: Final[float] = 0.2
BODY_MUTATION_PROBABILITY: Final[float] = 0.8
BODY_NUMBER_OF_ELITES: Final[int] = 1

SIGMA_START = 0.5
SIGMA_END   = 0.1
INPB_START = 0.4
INPB_END   = 0.1


def make_run_name(prefix: str = "RUN") -> str:
	"""Create a timestamped run name (same format used in EA.py before)."""
	return prefix + f"___[{datetime.now().strftime('%d%b_%H-%M')}]"

# Re-export convenient names that example modules commonly import
# (This file intentionally exposes many names so examples can import a
# single module. Be aware that importing Params will import heavy libs
# like MuJoCo and matplotlib and may have runtime requirements.)
__all__ = [
	# stdlib / helpers
	"Path",
	"datetime",
	"time",
	"random",

	# numpy
	"np",
	"npt",
	"RNG",

	# plotting / rendering
	"plt",
	"mj",
	"viewer",

	# ariel helpers
	"console",
	"construct_mjspec_from_graph",
	"HighProbabilityDecoder",
	"save_graph_as_json",
	"NeuralDevelopmentalEncoding",
	"Controller",
	"OlympicArena",
	"single_frame_renderer",
	"video_renderer",
	"simple_runner",
	"Tracker",
	"VideoRecorder",

	# EA / deap
	"base",
	"creator",
	"tools",

	# constants and helpers
	"SEED",
	"NUM_OF_MODULES",
	"SPAWN_POS",
	"TARGET_POSITION",
	"GENOTYPE_SIZE",
	"INIT_EVAL_DURATION",
	"data_dir_for",
	"BRAIN_HIDDEN_SIZE",
	"BRAIN_GENERATIONS",
	"BRAIN_POPULATION_SIZE",
	"BRAIN_CROSSOVER_PROBABILITY",
	"BRAIN_MUTATION_PROBABILITY",
	"BRAIN_NUMBER_OF_ELITES",
	"BODY_GENERATIONS",
	"BODY_POPULATION_SIZE",
	"BODY_INIT_POP_SIZE",
	"BODY_CROSSOVER_PROBABILITY",
	"BODY_MUTATION_PROBABILITY",
	"BODY_NUMBER_OF_ELITES",
	"make_run_name",
	"DATA",
	"SIGMA_START",
	"SIGMA_END",
	"INPB_START",
	"INPB_END",
]

# Default common data folder for examples
# Default DATA folder is inside the example package directory
DATA: Path = Path(__file__).parent / "DATA"
DATA.mkdir(parents=True, exist_ok=True)
