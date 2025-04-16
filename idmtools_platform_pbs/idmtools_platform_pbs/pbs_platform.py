"""
Here we implement the PBSPlatform object.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
from pathlib import Path
import subprocess
from typing import Optional, Any, Dict, List, Union, Literal
from dataclasses import dataclass, field, fields
from logging import getLogger
from idmtools import IdmConfigParser
from idmtools.core import ItemType, EntityStatus, TRUTHY_VALUES
from idmtools.core.interfaces.ientity import IEntity
from idmtools.entities.suite import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.iplatform import IPlatform, ITEM_TYPE_TO_OBJECT_INTERFACE
from idmtools_platform_file.file_platform import FilePlatform
from idmtools_platform_pbs.assets import generate_script, generate_simulation_script, generate_batch
from idmtools_platform_pbs.platform_operations.json_metadata_operations import JSONMetadataOperations
from idmtools_platform_pbs.platform_operations.asset_collection_operations import \
    PBSPlatformAssetCollectionOperations
from idmtools_platform_pbs.platform_operations.experiment_operations import PBSPlatformExperimentOperations
from idmtools_platform_pbs.platform_operations.simulation_operations import PBSPlatformSimulationOperations
from idmtools_platform_pbs.platform_operations.suite_operations import PBSPlatformSuiteOperations
from idmtools_platform_pbs.utils import get_max_array_size, check_pbs
from idmtools_platform_slurm.utils.slurm_job import run_script_on_slurm, slurm_installed

logger = getLogger(__name__)

op_defaults = dict(default=None, compare=False, metadata={"pickle_ignore": True})
CONFIG_PARAMETERS = ['job_name', 'ntasks', 'nodes', 'ncpus',
                     'mem', 'wall_time', 'depend', 'queue', 'email', 'environment', 'job_dir',
                     'max_running_jobs', 'array_batch_size', 'mpi_type']


@dataclass(repr=False)
class PBSPlatform(FilePlatform):
    # job_directory: str = field(default=None, metadata=dict(help="Job Directory"))

    # region: Resources request

    # choose e-mail type
    job_name: Optional[str] = field(default=None, metadata=dict(pbs=True, help="Job Name"))

    # How many nodes to be used: [ZD] seems like it is required, set to 1 by default
    nodes: Optional[int] = field(default=1, metadata=dict(pbs=True, help="Number of nodes"))

    # CPU # per task
    ncpus: Optional[int] = field(default=None, metadata=dict(pbs=True, help="Number of CPUs per task"))

    # Memory per core: MB of memory
    mem: Optional[str] = field(default=None, metadata=dict(pbs=True, help="Memory per core"))

    # Memory per core: MB of memory
    # mem_per_cpu: Optional[int] = field(default=None, metadata=dict(pbs=True, help="Memory per CPU"))

    # Limit time on this job hrs:min:sec
    wall_time: str = field(default=None, metadata=dict(pbs=True, help="Limit time on this job"))

    # Which partition to use
    depend: Optional[str] = field(default=None, metadata=dict(pbs=True,
                                                              help="Submits jobs that depend on another job’s successful completion."))

    # Specify compute node
    queue: Optional[str] = field(default=None,
                                 metadata=dict(pbs=True, help="Specifies which queue to submit the job to."))

    # Allocated nodes can not be shared with other jobs/users
    email: bool = field(default=None, metadata=dict(pbs=True, help="Sends job status emails."))

    # Specifies that the batch job should be eligible for requeuing
    environment: bool = field(default=True, metadata=dict(pbs=True, help="Requeue"))

    # if set to something, jobs will run with the specified account in slurm
    # account: str = field(default=None, metadata=dict(pbs=True, help="Account"))

    # Default retries for jobs
    job_dir: int = field(default=None, metadata=dict(pbs=True, help="Default retries for jobs"))

    # Pass custom commands to sbatch generation script
    # sbatch_custom: Optional[str] = field(default=None, metadata=dict(sbatch=True, help="Custom sbatch commands"))

    # modules to be load
    modules: list = field(default_factory=list, metadata=dict(pbs=True, help="Modules to be loaded"))

    # Specifies default setting of whether slurm should fail if item directory already exists
    dir_exist_ok: bool = field(default=False, repr=False, compare=False, metadata=dict(help="Directory exist ok"))

    # Set array max size for Slurm job
    array_batch_size: int = field(default=None, metadata=dict(pbs=False, help="Array batch size"))

    # determine if run script as Slurm job
    run_on_pbs: bool = field(default=False, repr=False, compare=False, metadata=dict(help="Run script as Slurm job"))

    # mpi type: default to pmi2 for older versions of MPICH or OpenMPI or an MPI library that explicitly requires PMI2
    mpi_type: Optional[Literal['pmi2', 'pmix', 'mpirun']] = field(default="pmi2", metadata=dict(pbs=True,
                                                                                                help="MPI types ('pmi2', 'pmix' for slurm MPI, 'mpirun' for independently MPI)"))

    # Maximum of running jobs(Per experiment)
    max_running_jobs: Optional[int] = field(default=100, metadata=dict(pbs=True, help="Maximum of running jobs"))
    # endregion

    _suites: PBSPlatformSuiteOperations = field(**op_defaults, repr=False, init=False)
    _experiments: PBSPlatformExperimentOperations = field(**op_defaults, repr=False, init=False)
    _simulations: PBSPlatformSimulationOperations = field(**op_defaults, repr=False, init=False)
    _assets: PBSPlatformAssetCollectionOperations = field(**op_defaults, repr=False, init=False)
    _metas: JSONMetadataOperations = field(**op_defaults, repr=False, init=False)

    def __post_init__(self):
        super().__post_init__()
        self.__init_interfaces()
        self.supported_types = {ItemType.SUITE, ItemType.EXPERIMENT, ItemType.SIMULATION}
        if self.job_directory is None:
            raise ValueError("Job Directory is required.")
        self.job_directory = os.path.abspath(self.job_directory)
        self.name_directory = IdmConfigParser.get_option(None, "name_directory", 'True').lower() in TRUTHY_VALUES
        self.sim_name_directory = IdmConfigParser.get_option(None, "sim_name_directory",
                                                             'False').lower() in TRUTHY_VALUES

        # check max_array_size from slurm configuration
        self._max_array_size = None
        if check_pbs():
            self._max_array_size = get_max_array_size()

        if self.mpi_type.lower() not in {'pmi2', 'pmix', 'mpirun'}:
            raise ValueError(f"Invalid mpi_type '{self.mpi_type}'. Allowed values are 'pmi2', 'pmix', or 'mpirun'.")

        self._object_cache_expiration = 600

        # check if run script as a slurm job
        # r = run_script_on_slurm(self, run_on_slurm=self.run_on_pbs)
        # if r:
        #     exit(0)  # finish the current workflow

    def __init_interfaces(self):
        self._suites = PBSPlatformSuiteOperations(platform=self)
        self._experiments = PBSPlatformExperimentOperations(platform=self)
        self._simulations = PBSPlatformSimulationOperations(platform=self)
        self._assets = PBSPlatformAssetCollectionOperations(platform=self)
        self._metas = JSONMetadataOperations(platform=self)

    def post_setstate(self):
        self.__init_interfaces()

    @property
    def pbs_fields(self):
        """
        Get list of fields that have metadata sbatch.
        Returns:
            Set of fields that have sbatch metadata
        """
        return set(f.name for f in fields(self) if "pbs" in f.metadata and f.metadata["pbs"])

    def get_pbs_configs(self, **kwargs) -> Dict[str, Any]:
        """
        Identify the Slurm config parameters from the fields.
        Args:
            kwargs: additional parameters
        Returns:
            slurm config dict
        """
        config_dict = {k: getattr(self, k) for k in self.pbs_fields}
        config_dict.update(kwargs)
        return config_dict

    def create_batch_file(self, item: Union[Experiment, Simulation], max_running_jobs: int = None, retries: int = None,
                          array_batch_size: int = None, dependency: bool = True, **kwargs) -> None:
        """
        Create batch file.
        Args:
            item: the item to build batch file for
            kwargs: keyword arguments used to expand functionality.
        Returns:
            None
        """
        if isinstance(item, Experiment):
            generate_batch(self, item, max_running_jobs, array_batch_size, dependency)
            generate_script(self, item, max_running_jobs)
        elif isinstance(item, Simulation):
            generate_simulation_script(self, item, retries)
        else:
            raise NotImplementedError(f"{item.__class__.__name__} is not supported for batch creation.")

    def submit_job(self, item: Union[Experiment, Simulation], **kwargs) -> None:
        """
        Submit a Slurm job.
        Args:
            item: idmtools Experiment or Simulation
            kwargs: keyword arguments used to expand functionality
        Returns:
            None
        """
        if isinstance(item, Experiment):
            working_directory = self.get_directory(item)
            subprocess.run(['bash', 'batch.sh'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(working_directory))
        elif isinstance(item, Simulation):
            pass
        else:
            raise NotImplementedError(f"Submit job is not implemented on SlurmPlatform.")


    # def get_job_id(self, item_id: str, item_type: ItemType) -> List:
    #     """
    #     Retrieve the job id for item that had been run.
    #     Args:
    #         item_id: id of experiment/simulation
    #         item_type: ItemType (Experiment or Simulation)
    #     Returns:
    #         List of slurm job ids
    #     """
    #     if item_type not in (ItemType.EXPERIMENT, ItemType.SIMULATION):
    #         raise RuntimeError(f"Not support item type: {item_type}")
    #
    #     item_dir = self.get_directory_by_id(item_id, item_type)
    #     job_id_file = item_dir.joinpath('job_id.txt')
    #     if not job_id_file.exists():
    #         logger.debug(f"{job_id_file} not found.")
    #         return None
    #
    #     job_id = open(job_id_file).read().strip()
    #     return job_id.split('\n')