"""Stable logical identity for the v0.5 dense constraint index."""

from __future__ import annotations

import os

LOGICAL_DENSE_INDEX = "armie-experts-v0.5-dense"
PHYSICAL_GATE6B_INDEX = "armie-experts-v1-v2-gate6b-dense-10000"


def configured_dense_index() -> str:
    """Return the explicit override or the stable logical runtime identity."""
    return os.getenv("ARMIE_V050_C1_INDEX", LOGICAL_DENSE_INDEX)


def physical_dense_index() -> str:
    """Return the current build identity used behind the logical boundary."""
    return os.getenv("ARMIE_V050_C1_PHYSICAL_INDEX", PHYSICAL_GATE6B_INDEX)
