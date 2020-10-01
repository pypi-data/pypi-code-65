from .process import sagemaker_processing_run
from .args import sagemaker_processing_args
from argparse import ArgumentParser
import inspect


def sagemaker_processing_main(
    main, script=None,description=None,
    **processing_args
):
    r"""
    Entry point for processing.

    Example
    -------

    .. code-block:: python

        from aws_sagemaker_remote import sagemaker_training_main

        def main(args):
            # your code here
            pass

        if __name__ == '__main__':
            sagemaker_training_main(
                main=main,
                # ... additional configuration
            )

    Parameters
    ----------
    main : function
        Main function. Must accept a single argument ``args:argparse.Namespace``.
    script : str, optional
        Path to script file to execute. 
        Set to ``__file__`` for most use-cases.
        Empty or None defaults to file containing ``main``.
    description: str, optional
        Script description for argparse
    \**processing_args : dict, optional
        Keyword arguments to :meth:`aws_sagemaker_remote.processing.args.sagemaker_processing_args`
    """
    if not script:
        script = inspect.getfile(main)
    parser = ArgumentParser(description=description)
    config = sagemaker_processing_args(
        parser=parser, script=script, **processing_args)
    args = parser.parse_args()
    if args.sagemaker_run:
        # Remote processing
        sagemaker_processing_run(
            args=args,
            config=config
        )
    else:
        # Local processing
        main(args)
