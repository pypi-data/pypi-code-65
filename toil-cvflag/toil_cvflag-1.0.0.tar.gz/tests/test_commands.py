"""
toil_cvflag commands tests.

tmpdir is a py.path.local, learn: https://py.readthedocs.io/en/latest/path.html
"""
from os.path import join
import gzip

import pytest

from toil_cvflag import commands
from tests.utils import TEST

REFERENCE = TEST["reference"]
NORMAL_BAM = TEST["normal_bam"]
TUMOR_BAM = TEST["tumor_bam"]
BEDFILELOC = TEST["bedFileLoc"]
INDELBED = TEST["indelBed"]
ANNOBEDLOC = TEST["annoBedLoc"]
UNMATCHEDVCFLOC = TEST["unmatchedVCFLoc"]
INPUT_VCF = TEST["input_vcf"]
EXPECTED_OUTPUT = TEST["expected_vcf"]

# VCF has 707 variants. Different values test parallel and non-parallel runs.
@pytest.mark.parametrize("bin_size", ["97", "800"], ids=["parallel", "non-parallel"])
def test_run_flagging(tmpdir, bin_size):
    """Test snvs flagging."""
    outdir = tmpdir.strpath
    jobstore = join(outdir, "jobstore")
    logfile = join(outdir, "log.txt")
    flagged_vcf = join(outdir, "output.vcf.gz")

    args = [
        jobstore,
        "--logFile",
        logfile,
        "--vcf",
        INPUT_VCF,
        "--out",
        flagged_vcf,
        "--bin-size",
        bin_size,
        "--normal-bam",
        NORMAL_BAM,
        "--tumor-bam",
        TUMOR_BAM,
        "--bedFileLoc",
        BEDFILELOC,
        "--indelBed",
        INDELBED,
        "--unmatchedVCFLoc",
        UNMATCHEDVCFLOC,
        "--reference",
        REFERENCE,
        "--annoBedLoc",
        ANNOBEDLOC,
        "--sequencing-method",
        "TGD",
        "--memory",
        "1G",
    ]

    # Get and validate options.
    parser = commands.get_parser()
    options = parser.parse_args(args)
    options = commands.process_parsed_options(options)

    # Call pipeline
    commands.run_toil(options)

    # Test to see if split is correct
    with gzip.open(EXPECTED_OUTPUT) as f:
        lines = f.readlines()
    variants = [l for l in lines if not l.startswith("#")]
    expected_num_variants = len(variants)

    with gzip.open(flagged_vcf) as f:
        lines = f.readlines()
    variants = [l for l in lines if not l.startswith("#")]
    obs_num_variants = len(variants)
    assert expected_num_variants == obs_num_variants

    # Assert new caveman flags are added that are not in initial flags
    assert any("DMY" in variant for variant in variants)
    assert any("SRP" in variant for variant in variants)
