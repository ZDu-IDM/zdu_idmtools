"""
Here we implement the SlurmPlatform asset collection operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import shutil
from uuid import UUID
from pathlib import Path
from dataclasses import field, dataclass
from logging import getLogger
from typing import TYPE_CHECKING, Type, List, Dict, Union, Optional
from idmtools.core import ItemType
from idmtools.assets import AssetCollection, Asset
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.iplatform_ops.iplatform_asset_collection_operations import IPlatformAssetCollectionOperations
from idmtools_platform_file.platform_operations.asset_collection_operations import FilePlatformAssetCollectionOperations
from idmtools_platform_slurm.platform_operations.utils import SlurmSimulation

if TYPE_CHECKING:
    from idmtools_platform_pbs.pbs_platform import PBSPlatform

logger = getLogger(__name__)
user_logger = getLogger("user")

EXCLUDE_FILES = ['_run.sh', 'metadata.json', 'stdout.txt', 'stderr.txt', 'status.txt', 'job_id.txt', 'job_status.txt']


@dataclass
class PBSPlatformAssetCollectionOperations(FilePlatformAssetCollectionOperations):
    """
    Provides AssetCollection Operations to PBSPlatform.
    """
    platform: 'PBSPlatform'  # noqa F821
    # platform_type: Type = field(default=None)