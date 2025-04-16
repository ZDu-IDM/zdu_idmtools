#!/usr/bin/env bash
# Get the parameters passed from sbatch.pbs
mpi_type="$2"

# Convert SLURM_ARRAY_TASK_ID to PBS_ARRAY_INDEX
SIMULATION_INDEX=$((${PBS_ARRAY_INDEX} + $1))
JOB_DIRECTORY=$(find . -type d -maxdepth 1 -mindepth 1 | grep -v Assets | head -$SIMULATION_INDEX | tail -1)
cd $JOB_DIRECTORY
current_dir=$(pwd)
echo "The script is running from: $current_dir"

# Run the simulation based on whether MPI is required
if [ "$mpi_type" = "no-mpi" ]; then
    echo "Run without MPI"
    ./_run.sh 1> stdout.txt 2> stderr.txt
elif [ "$mpi_type" = "mpirun" ]; then
    echo "Run mpirun"
    mpirun "$current_dir"/_run.sh 1> stdout.txt 2> stderr.txt
elif [ "$mpi_type" = "pmi2" ] || [ "$mpi_type" = "pmix" ]; then # pmi2 or pmix
    echo "Run MPI with $mpi_type"
    mpiexec --mca pml $mpi_type _run.sh 1> stdout.txt 2> stderr.txt
else
    echo "Invalid MPI type: $mpi_type"
fi
