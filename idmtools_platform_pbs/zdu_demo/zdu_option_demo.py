from idmtools.assets import Asset
from idmtools.entities import CommandLine
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment

# Initialize the platform
from idmtools.core.platform_factory import Platform
job_directory = 'CONTAINER_FILE'
platform = Platform('Container', job_directory=job_directory)
# OR to use ContainerPlatform object directly
# from idmtools_platform_container.container_platform import ContainerPlatform
# platform = ContainerPlatform(job_directory="destination_directory")

# Define task
# command = "python3 Assets/rst store/hello.py"
command = "'python Assets/hello.py'"
cmd = CommandLine(command)
cmd.add_option("--hi", "Assets/rst store/hello.py")
# cmd.add_option("--hi", "Assets/hello.py")
task = CommandTask(command=cmd)
# Run an experiment
experiment = Experiment.from_task(task, name="example")
asset = Asset(r'C:\Projects\idmtools_zhaoweidu\examples\platform_container\zdu_demo\rst store\hello.py', relative_path='rst store')
experiment.add_asset(asset)
experiment.add_asset("rst store/hello.py")
# experiment.add_asset(r'C:\Projects\idmtools_zhaoweidu\examples\platform_container\zdu_demo\rst store\hello.py')
experiment.run(wait_until_done=False, dry_run=False)