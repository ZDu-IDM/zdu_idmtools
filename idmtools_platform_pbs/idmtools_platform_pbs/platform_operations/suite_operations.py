"""
Here we implement the PBSPlatform suite operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import shutil
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, List, Type, Dict, Tuple
from logging import getLogger
from idmtools.core import ItemType
from idmtools.entities import Suite
from idmtools.entities.iplatform_ops.iplatform_suite_operations import IPlatformSuiteOperations
from idmtools_platform_file.platform_operations.suite_operations import FilePlatformSuiteOperations
from idmtools_platform_file.platform_operations.utils import FileSuite, FileExperiment

if TYPE_CHECKING:
    from idmtools_platform_pbs.pbs_platform import PBSPlatform

logger = getLogger(__name__)
user_logger = getLogger('user')


@dataclass
class PBSPlatformSuiteOperations(FilePlatformSuiteOperations):
    """
    Provides Suite operation to the PBSPlatform.
    """
    platform: 'PBSPlatform'  # noqa F821

    # platform_type: Type = field(default=SlurmSuite)

    def platform_cancel(self, suite_id: str, force: bool = False) -> None:
        """
        Cancel platform suite's slurm job.
        Args:
            suite_id: suite id
            force: bool, True/False
        Returns:
            None
        """
        suite = self.platform.get_item(suite_id, ItemType.SUITE, raw=False)
        logger.debug(f"cancel pbs job for suite: {suite_id}...")
        for exp in suite.experiments:
            self.platform._experiments.platform_cancel(exp.id, force)
