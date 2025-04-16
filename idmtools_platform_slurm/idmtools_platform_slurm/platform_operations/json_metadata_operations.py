"""
Here we implement the JSON Metadata operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from typing import TYPE_CHECKING
from dataclasses import dataclass
from idmtools_platform_file.platform_operations.json_metadata_operations import \
    JSONMetadataOperations as FileJSONMetadataOperations

if TYPE_CHECKING:
    from idmtools_platform_slurm.slurm_platform import SlurmPlatform


@dataclass
class JSONMetadataOperations(FileJSONMetadataOperations):
    platform: 'SlurmPlatform'  # noqa: F821
    # platform_type: Type = field(default=None)
    # metadata_filename: str = field(default='metadata.json')
