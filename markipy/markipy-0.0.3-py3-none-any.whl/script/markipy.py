from markipy.basic import Process
import argparse


def Args():
    mparser = argparse.ArgumentParser(description='MarkIpy')
    # Add the arguments
    mparser.add_argument('-pip-up', action="store", default=False)
    return mparser.parse_args()


def Main():
    args = Args()

    if args.pip_up:
        py = args.pip_up
        p_build = Process('Dist.Build', cmd=[py, 'setup.py', 'bdist_wheel'])
        p_upload = Process('Pip.Upload', cmd=[py, '-m', 'twine', 'upload', 'dist/*'])

        p_build.start()
        p_upload.start()
