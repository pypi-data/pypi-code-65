"""   Definitions to configure the app   """

from pathlib import Path

DEVICE_SERIAL_NO = '166018'  # Default 'device_serial_no'

# Keys that are relevant for IQMs
RELEVANT_KEYS = [
    'bids_meta.modality',
    'spacing_x', 'size_x',
    'spacing_y', 'size_y',
    'spacing_z', 'size_z',
    'bids_meta.RepetitionTime',
    'bids_meta.InversionTime',
    'bids_meta.EchoTime',
    'bids_meta.FlipAngle',
    'bids_meta.PartialFourier',
    'bids_meta.PixelBandwidth',
    'bids_meta.ReceiveCoilName',
    'bids_meta.ParallelReductionFactorInPlane',
]

# Keys that are irrelevant, so we won't even save to file:
DISCARD_KEYS = [
    'Slices'
]

MRIQC_SERVER = 'mriqc.nimh.nih.gov'

# REPOSITORY_PATH = Path('/BIDS/CBI/mriqc/local_stats')
REPOSITORY_PATH = Path.home() / 'data/scratch/mriqc/local_stats'

DEFAULT_T1_PROTOCOL = {
    'size_x': 240,    # no. slices
    'size_y': 256,
    'size_z': 256,
    'spacing_x': 0.9,
    'spacing_y': 0.9,
    'spacing_z': 0.9,
    'bids_meta.InversionTime': 0.9,
    'bids_meta.EchoTime': 0.00232,
    'bids_meta.FlipAngle': 8,
#    'bids_meta.ParallelReductionFactorInPlane': 2,
#    'bids_meta.PartialFourier': 1,
    'bids_meta.PixelBandwidth': 200,
#    'bids_meta.ReceiveCoilName': 'HeadNeck_64',
    'bids_meta.RepetitionTime': 2.3,
}

DEFAULT_T2_PROTOCOL = {
    'size_x': 240,    # no. slices
    'size_y': 256,
    'size_z': 256,
    'spacing_x': 0.9,
    'spacing_y': 0.9,
    'spacing_z': 0.9,
    'bids_meta.EchoTime': 0.564,
#    'bids_meta.PartialFourier': 1,
    'bids_meta.PixelBandwidth': 750,
#    'bids_meta.ReceiveCoilName': 'HeadNeck_64',
    'bids_meta.RepetitionTime': 3.2,
}

DEFAULT_BOLD_PROTOCOL = {
    'size_x': 104,    # R>L
    'size_y': 104,
#    'size_z': 64,
    'spacing_x': 2,
    'spacing_y': 2,
    'spacing_z': 2,
    'bids_meta.EchoTime': 0.035,
#    'bids_meta.ParallelReductionFactorInPlane': 2,
#    'bids_meta.PartialFourier': 1,
    'bids_meta.PixelBandwidth': 2290,
#    'bids_meta.ReceiveCoilName': 'HeadNeck_64',
#    'bids_meta.RepetitionTime': 1.3,
}
