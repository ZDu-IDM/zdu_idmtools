"""
Here we implement the JSON Metadata operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
import json
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Type, Union
from dataclasses import dataclass, field
from idmtools.core import ItemType
from idmtools.core.interfaces import imetadata_operations
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.utils.json import IDMJSONEncoder
from idmtools_platform_slurm.platform_operations.utils import SlurmSuite, SlurmExperiment, SlurmSimulation

from idmtools_platform_file.platform_operations.json_metadata_operations import JSONMetadataOperations as FileJSONMetadataOperations

if TYPE_CHECKING:
    from idmtools_platform_pbs.pbs_platform import PBSPlatform


@dataclass
class JSONMetadataOperations(FileJSONMetadataOperations):
    platform: 'PBSPlatform'  # noqa: F821
    # platform_type: Type = field(default=None)
    # metadata_filename: str = field(default='metadata.json')
