"""
SlurmPlatform utilities.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from pathlib import Path
from jinja2 import Template
from typing import TYPE_CHECKING, Optional, Union
from idmtools.entities.experiment import Experiment
from idmtools_platform_slurm.platform_operations.utils import check_home

if TYPE_CHECKING:
    from idmtools_platform_pbs.pbs_platform import PBSPlatform, CONFIG_PARAMETERS

DEFAULT_TEMPLATE_FILE = Path(__file__).parent.joinpath("sbatch.pbs.jinja2")
BATCH_TEMPLATE_FILE = Path(__file__).parent.joinpath("batch.sh.jinja2")


def generate_batch(platform: 'PBSPlatform', experiment: Experiment,
                   max_running_jobs: Optional[int] = None, array_batch_size: Optional[int] = None,
                   dependency: Optional[bool] = None,
                   template: Union[Path, str] = BATCH_TEMPLATE_FILE, **kwargs) -> None:
    """
    Generate bash script file batch.sh
    Args:
        platform: PBS Platform
        experiment: idmtools Experiment
        max_running_jobs: int, how many allowed to run
        array_size: INT, array size for slurm job
        dependency: bool, determine if Slurm jobs depend on each other
        template: template to be used to build batch file
        kwargs: keyword arguments used to expand functionality
    Returns:
        None
    """
    template_vars = dict(njobs=experiment.simulation_count)

    # Set max_running_jobs
    if max_running_jobs is not None:
        if platform.max_running_jobs is not None:
            template_vars['max_running_jobs'] = min(max_running_jobs, platform.max_running_jobs)
        else:
            template_vars['max_running_jobs'] = max_running_jobs
    else:
        if platform.max_running_jobs is not None:
            template_vars['max_running_jobs'] = platform.max_running_jobs
        else:
            template_vars['max_running_jobs'] = 1

    # Set array_size
    if array_batch_size is not None:
        platform.array_batch_size = array_batch_size

    if platform._max_array_size is not None:
        if platform.array_batch_size is not None:
            template_vars['array_batch_size'] = min(platform._max_array_size, platform.array_batch_size,
                                                    experiment.simulation_count)
        else:
            template_vars['array_batch_size'] = min(platform._max_array_size, experiment.simulation_count)
    elif platform.array_batch_size is not None:
        template_vars['array_batch_size'] = min(platform.array_batch_size, experiment.simulation_count)
    else:
        template_vars['array_batch_size'] = experiment.simulation_count

    # Consider dependency
    if dependency is None:
        dependency = True
    template_vars['dependency'] = dependency

    # Update with possible override values
    template_vars.update(kwargs)

    # Build batch based on the given template
    with open(template) as file_:
        t = Template(file_.read())

    # Write out file
    output_target = platform.get_directory(experiment).joinpath("batch.sh")
    with open(output_target, "w") as tout:
        tout.write(t.render(template_vars))

    # Make executable
    platform.update_script_mode(output_target)


def generate_script(platform: 'PBSPlatform', experiment: Experiment, max_running_jobs: Optional[int] = None,
                    template: Union[Path, str] = DEFAULT_TEMPLATE_FILE, **kwargs) -> None:
    """
    Generate batch file sbatch.sh
    Args:
        platform: PBS Platform
        experiment: idmtools Experiment
        max_running_jobs: int, how many allowed to run at the same time
        template: template to be used to build batch file
        kwargs: keyword arguments used to expand functionality
    Returns:
        None
    """
    from idmtools_platform_pbs.pbs_platform import CONFIG_PARAMETERS
    template_vars = dict(njobs=experiment.simulation_count)

    select = ['nodes', 'ncpus', 'mem']
    select_dict = {}
    # populate from our platform config vars
    for p in CONFIG_PARAMETERS:
        if getattr(platform, p) is not None:
            template_vars[p] = getattr(platform, p)
            if p in select:
                select_dict[p] = getattr(platform, p)

    if 'nodes' in select_dict:
        select_dict['select'] = int(select_dict['nodes'])
    select_dict.pop('nodes', None)

    # re-arrange the keys
    keys = list(select_dict.keys())
    if 'select' in keys:
        keys.remove('select')
        keys.insert(0, 'select')

    # Build select string with select in the beginning
    select_str = ''
    for k in keys:
        select_str += f'{k}={select_dict[k]}:'
    select_str = select_str.rstrip(':')
    template_vars['select'] = select_str
    # print(select_dict)
    # exit()

    # Set default here
    if max_running_jobs is not None:
        template_vars['max_running_jobs'] = max_running_jobs
    if max_running_jobs is None and platform.max_running_jobs is None:
        template_vars['max_running_jobs'] = 1

    # Add any overides. We need some validation here later
    # TODO add validation for valid config options
    template_vars.update(kwargs)

    if platform.modules:
        template_vars['modules'] = platform.modules

    with open(template) as file_:
        t = Template(file_.read())

    # Write out file
    output_target = platform.get_directory(experiment).joinpath("sbatch.pbs")
    with open(output_target, "w") as tout:
        tout.write(t.render(template_vars))
    # Make executable
    platform.update_script_mode(output_target)


def generate_simulation_script(platform: 'PBSPlatform', simulation, retries: Optional[int] = None,  **kwargs) -> None:
    """
    Generate batch file _run.sh
    Args:
        platform: PBS Platform
        simulation: idmtools Simulation
        retries: int
        kwargs: keyword arguments used to expand functionality
    Returns:
        None
    """
    experiment_dir = platform.get_directory(simulation.parent).absolute()
    experiment_dir = str(experiment_dir).replace('\\', '/')
    check = check_home(experiment_dir)
    sim_script = platform.get_directory(simulation).joinpath("_run.sh")
    with open(sim_script, "w") as tout:
        with open(Path(__file__).parent.parent.joinpath("assets/_run.sh.jinja2")) as tin:
            tvars = dict(
                platform=platform,
                simulation=simulation,
                retries=retries if retries else platform.retries
            )
            if not check:
                tvars['experiment_dir'] = str(experiment_dir)

            t = Template(tin.read())
            tout.write(t.render(tvars))
    # Make executable
    platform.update_script_mode(sim_script)
