import click

DISK_SIZE_ERROR_MSG = "Invalid disk size, should be greater than 100Gb"


def validate_config(cfg: dict):
    disk_size = cfg['compute']['train']['disk_size']
    if disk_size is not None and disk_size < 100:
        raise click.ClickException(DISK_SIZE_ERROR_MSG)


def validate_disk_size_callback(ctx, param, value):
    if value < 100:
        raise click.BadParameter(DISK_SIZE_ERROR_MSG)
