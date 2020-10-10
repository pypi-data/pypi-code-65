from pypigeonhole_build.pip_dep_utils import Installer, PIP

CONDA = Installer(name='CONDA')


def gen_conda_yaml(libs, target_file):  # output all libs, install or dev.
    if not CONDA.env:
        raise ValueError("Need to define conda env name!")

    with open(target_file, 'w') as f:
        f.write(f'name: {CONDA.env}\n')
        f.write('\n')

        if CONDA.channels:
            f.write('channels:\n')
            for c in CONDA.channels:
                f.write(f'    - {c}\n')
            f.write('\n')

        f.write('dependencies:\n')
        # we do it this because we need to keep the order of the input.
        for lib in libs:
            if lib.installer == CONDA:
                f.write(f'    - {lib.name}{lib.version}\n')

        f.write('    - pip:\n')
        for lib in libs:
            if lib.installer == PIP:
                if lib.url:
                    f.write(f'        - {lib.url}')
                else:
                    f.write(f'        - {lib.name}{lib.version}\n')
