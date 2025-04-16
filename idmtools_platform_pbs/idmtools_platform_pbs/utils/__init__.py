"""
idmtools PBSPlatform platform operations module.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import subprocess

# get_max_array_size = 1000


def check_pbs() -> bool:
    """
    Check if PBS is installed and available.
    Returns:
        bool: True if PBS is installed and running, False otherwise.
    """
    try:
        # Check if PBS commands exist
        subprocess.run(["qstat", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        subprocess.run(["pbsnodes", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        # Check if PBS services are running
        pbs_status = subprocess.run(["qstat"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if pbs_status.returncode == 0:
            print("PBS is installed and available.")
            return True
        else:
            print("PBS is installed but not responding properly.")
            return False
    except FileNotFoundError:
        print("PBS is not installed.")
        return False
    except subprocess.CalledProcessError:
        print("PBS commands exist but may not be functioning correctly.")
        return False


def get_max_array_size() -> int:
    """
    Get PBS Pro MaxArraySize from the server configuration.
    Returns:
        PBS system MaxArraySize
    """
    try:
        output = subprocess.check_output(['qmgr', '-c', 'p s'], stderr=subprocess.DEVNULL)
        for line in output.decode().splitlines():
            if "max_array_size" in line:
                max_array_size = int(line.split("=")[1].strip())
                return max_array_size - 1
    except (subprocess.CalledProcessError, IndexError, ValueError):
        pass

    return None
