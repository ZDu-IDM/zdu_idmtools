from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment

# Initialize the platform
from idmtools.core.platform_factory import Platform
# job_directory = 'CONTAINER_FILE'
# platform = Platform('Container', job_directory=job_directory)
job_directory = 'PBS_FILE'
platform = Platform('PBS', job_directory=job_directory, job_name='pbs-test', nodes=1, ncpus=2, mem='4gb', waltime='01:00:15')
# platform = Platform('SLURM_LOCAL', job_directory=job_directory)
# platform = Platform('FILE', job_directory=job_directory)
# OR to use ContainerPlatform object directly
# from idmtools_platform_container.container_platform import ContainerPlatform
# platform = ContainerPlatform(job_directory="destination_directory")

# print(platform.pbs_fields)
# exit()

# Define task
command = "python3 Assets/sleep.py 300"    # sleep for 1 hour
task = CommandTask(command=command)
# Run an experiment
experiment = Experiment.from_task(task, name="example")
experiment.add_asset("sleep.py")
experiment.run(wait_until_done=False, dry_run=True)