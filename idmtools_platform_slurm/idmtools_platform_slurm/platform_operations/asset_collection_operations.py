"""
Here we implement the SlurmPlatform asset collection operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from dataclasses import field, dataclass
from logging import getLogger
from typing import TYPE_CHECKING, Type, List, Dict, Union, Optional
from idmtools_platform_file.platform_operations.asset_collection_operations import FilePlatformAssetCollectionOperations

if TYPE_CHECKING:
    from idmtools_platform_slurm.slurm_platform import SlurmPlatform


@dataclass
class SlurmPlatformAssetCollectionOperations(FilePlatformAssetCollectionOperations):
    """
    Provides AssetCollection Operations to SlurmPlatform.
    """
    platform: 'SlurmPlatform'  # noqa F821
