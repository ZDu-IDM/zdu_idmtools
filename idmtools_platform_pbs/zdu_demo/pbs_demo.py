from idmtools.core.platform_factory import Platform
def file_platform_demo():
    from idmtools_platform_file.file_platform import FilePlatform

    configuration = {'job_directory': 'PBS_FILE'}
    platform = FilePlatform(**configuration)
    print(platform)


def pbs_platform_demo():
    from idmtools_platform_pbs.pbs_platform import PBSPlatform

    configuration = {'job_directory': 'PBS_FILE'}
    platform = PBSPlatform(**configuration)
    print(platform)

def check_pbs_deno():
    from idmtools_platform_pbs.utils import check_pbs
    check_pbs()

def main():
    platform = Platform('FILE', job_directory='PBS_FILE')
    print(platform)


if __name__ == '__main__':
    # file_platform_demo()
    # exit()

    check_pbs_deno()
    exit()

    main()
