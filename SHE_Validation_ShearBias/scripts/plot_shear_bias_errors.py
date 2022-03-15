""" @file plot_shear_bias_errors.py

    Script to generate a plot of shear bias errors compared to requirements.
"""
import numpy as np

# Constants for requirement values

FULL_REQS = {"m": 2e-3,
             "c": 5e-4}

ALG_REQ_FACTOR = 20

ALG_REQS = {"m": FULL_REQS["m"] / ALG_REQ_FACTOR,
            "c": FULL_REQS["C"] / ALG_REQ_FACTOR}

SPATIAL_REQ_FACTOR = np.sqrt(14514 / 59.5)

SPATIAL_REQS = {"m": FULL_REQS["m"] * SPATIAL_REQ_FACTOR,
                "c": FULL_REQS["C"] * SPATIAL_REQ_FACTOR}

SPATIAL_ALG_REQS = {"m": ALG_REQS["m"] * SPATIAL_REQ_FACTOR,
                    "c": ALG_REQS["C"] * SPATIAL_REQ_FACTOR}
