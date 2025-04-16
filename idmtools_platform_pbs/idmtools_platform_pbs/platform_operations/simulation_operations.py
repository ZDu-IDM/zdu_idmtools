"""
Here we implement the PBSPlatform simulation operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Dict, Type, Optional, Union, Any
import shutil
from idmtools.assets import Asset
from idmtools.core import ItemType, EntityStatus
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.iplatform_ops.iplatform_simulation_operations import IPlatformSimulationOperations
from idmtools_platform_file.platform_operations.simulation_operations import FilePlatformSimulationOperations
from idmtools_platform_file.platform_operations.utils import FileSimulation, FileExperiment, clean_experiment_name
from logging import getLogger

logger = getLogger(__name__)
user_logger = getLogger('user')

if TYPE_CHECKING:
    from idmtools_platform_pbs.pbs_platform import PBSPlatform

logger = getLogger(__name__)


@dataclass
class PBSPlatformSimulationOperations(FilePlatformSimulationOperations):
    platform: 'PBSPlatform'  # noqa: F821

    # platform_type: Type = field(default=SlurmSimulation)

    def platform_cancel(self, sim_id: str, force: bool = False) -> Any:
        """
        Cancel platform simulation's slurm job.
        Args:
            sim_id: simulation id
            force: bool, True/False
        Returns:
            Any
        """
        sim = self.platform.get_item(sim_id, ItemType.SIMULATION, raw=False)
        if force or sim.status == EntityStatus.RUNNING:
            logger.debug(f"cancel pbs job for simulation: {sim_id}...")
            job_id = self.platform.get_job_id(sim_id, ItemType.SIMULATION)
            if job_id is None:
                logger.debug(f"PBS job for simulation: {sim_id} is not available!")
                return
            else:
                result = self.platform.cancel_job(job_id)
                user_logger.info(f"Cancel Simulation: {sim_id}: {result}")
                return result
        else:
            user_logger.info(f"Simulation {sim_id} is not running, no cancel needed...")
