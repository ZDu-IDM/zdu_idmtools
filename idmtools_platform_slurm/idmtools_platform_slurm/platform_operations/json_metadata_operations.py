"""
Here we implement the JSON Metadata operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from typing import TYPE_CHECKING, Type
from dataclasses import dataclass, field
from idmtools_platform_file.platform_operations.json_metadata_operations import \
    JSONMetadataOperations as FileJSONMetadataOperations

if TYPE_CHECKING:
    from idmtools_platform_slurm.slurm_platform import SlurmPlatform


@dataclass
class JSONMetadataOperations(FileJSONMetadataOperations):
    platform: 'SlurmPlatform'  # noqa: F821
    # metadata_filename: str = field(default='metadata.json')
